"""Small Gram reader for the MVP.

The public Recipe model deliberately isolates templates from parser details. This
reader supports the Gram constructs used by the UI; it can later be replaced by
an adapter over the official compiler without changing the PWA.
"""

import copy
import re
from pathlib import Path

import yaml

from .models import Ingredient, ParallelOperation, Recipe, RecipeVariant, Step
from .nutrition import calculate_recipe_nutrition
from .schema import ROOT, RecipeValidationError, validate_recipe_contract
from .shopping import evaluate_recipe_shopping

ACTION = re.compile(r"^\[([^]]+)]\s*(.*)$")
SUBSTEP = re.compile(r"^[-*]\s+(.+)$")
PARALLEL = re.compile(r"^\|\|\s*(?:(?P<id>[a-z0-9][a-z0-9-]*)\s*\|\s*)?(?P<label>[^:]+):\s*(?P<body>.+)$")
INGREDIENT = re.compile(r"@([^@{}]+)\{([^}]*)}")
EQUIPMENT = re.compile(r"#([^#{}]+)\{[^}]*}")
TIMER = re.compile(r"~(?:_[\w-]+)?\{\s*(\d+(?:[.,]\d+)?)\s*(s|sec|m|min|h)\s*}", re.IGNORECASE)
TEMPERATURE = re.compile(r"\^\{\s*([^}]+)\s*}")


def _seconds(value: str, unit: str) -> int:
    number = float(value.replace(",", "."))
    factor = 3600 if unit.lower() == "h" else 60 if unit.lower() in {"m", "min"} else 1
    return round(number * factor)


def _clean(text: str) -> str:
    text = INGREDIENT.sub(
        lambda m: f"{m.group(1).strip()}" + (f" ({m.group(2).strip()})" if m.group(2).strip() else ""), text
    )
    text = EQUIPMENT.sub(lambda m: m.group(1).strip(), text)
    text = TIMER.sub(lambda m: f"{m.group(1)} {m.group(2)}", text)
    text = TEMPERATURE.sub(lambda m: m.group(1).strip(), text)
    return re.sub(r"\s+", " ", text).strip()


def _slug(value: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", normalized.casefold()).strip("-") or "step"


def _mentions(text: str) -> tuple[list[Ingredient], list[str], list[dict], list[str]]:
    ingredients = [Ingredient(m.group(1).strip(), m.group(2).strip()) for m in INGREDIENT.finditer(text)]
    equipment = [m.group(1).strip() for m in EQUIPMENT.finditer(text)]
    timers = [
        {"seconds": _seconds(m.group(1), m.group(2)), "label": f"{m.group(1)} {m.group(2)}"}
        for m in TIMER.finditer(text)
    ]
    temperatures = [m.group(1).strip() for m in TEMPERATURE.finditer(text)]
    return ingredients, equipment, timers, temperatures


def _parse_steps(source: str, path: Path) -> list[Step]:
    step_blocks: list[dict] = []
    current_block: dict | None = None

    for raw in source.splitlines():
        line = raw.strip()
        action_match = ACTION.match(line)
        if action_match:
            if current_block:
                step_blocks.append(current_block)
            header, body = action_match.groups()
            if "|" in header:
                step_id, action = (part.strip() for part in header.split("|", 1))
            else:
                action = header.strip()
                step_id = _slug(action)
            current_block = {
                "id": step_id,
                "action": action,
                "body": body.strip(),
                "substeps": [],
                "parallel": [],
                "raw_lines": [body.strip()] if body.strip() else [],
            }
            continue

        parallel_match = PARALLEL.match(line)
        if parallel_match and current_block is not None:
            operation = parallel_match.groupdict()
            operation["id"] = operation["id"] or _slug(operation["label"])
            current_block["parallel"].append(operation)
            current_block["raw_lines"].append(operation["body"])
            continue

        substep_match = SUBSTEP.match(line)
        if substep_match and current_block is not None:
            substep_text = substep_match.group(1).strip()
            current_block["substeps"].append(substep_text)
            current_block["raw_lines"].append(substep_text)
            continue

        if line and not line.startswith("#") and current_block is not None:
            current_block["raw_lines"].append(line)
            current_block["body"] = f"{current_block['body']} {line}".strip()

    if current_block:
        step_blocks.append(current_block)

    seen_step_ids: set[str] = set()
    steps: list[Step] = []
    for block in step_blocks:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", block["id"]):
            raise RecipeValidationError(path, "steps.id", block["id"], f"invalid step id '{block['id']}'")
        if block["id"] in seen_step_ids:
            raise RecipeValidationError(path, "steps.id", block["id"], f"duplicate step id '{block['id']}'")
        seen_step_ids.add(block["id"])

        full_text = " ".join(block["raw_lines"])
        ingredients, equipment, timers, temperatures = _mentions(full_text)
        parallel: list[ParallelOperation] = []
        seen_operation_ids: set[str] = set()
        for operation in block["parallel"]:
            if operation["id"] in seen_operation_ids:
                raise RecipeValidationError(
                    path,
                    "parallel.id",
                    operation["id"],
                    f"duplicate parallel operation id '{operation['id']}' in step '{block['id']}'",
                )
            seen_operation_ids.add(operation["id"])
            op_ingredients, op_equipment, op_timers, op_temperatures = _mentions(operation["body"])
            parallel.append(
                ParallelOperation(
                    id=operation["id"],
                    label=operation["label"].strip(),
                    text=_clean(operation["body"]),
                    timers=op_timers,
                    temperatures=op_temperatures,
                    ingredients=op_ingredients,
                    equipment=op_equipment,
                )
            )

        steps.append(
            Step(
                id=block["id"],
                action=block["action"],
                text=_clean(block["body"]),
                timers=timers,
                temperatures=temperatures,
                ingredients=ingredients,
                equipment=equipment,
                substeps=[_clean(s) for s in block["substeps"]],
                parallel=parallel,
            )
        )
    return steps


def _collect_ingredients(steps: list[Step]) -> list[Ingredient]:
    collected: dict[str, Ingredient] = {}
    for step in steps:
        for ingredient in step.ingredients:
            key = ingredient.name.casefold()
            current = collected.get(key)
            if current is None or (not current.quantity and ingredient.quantity):
                collected[key] = copy.deepcopy(ingredient)
    return list(collected.values())


def _collect_equipment(steps: list[Step]) -> list[str]:
    return list(dict.fromkeys(item for step in steps for item in step.equipment))


def _patch_ingredients(ingredients: list[Ingredient], patch: dict, path: Path) -> list[Ingredient]:
    result = {item.name.casefold(): copy.deepcopy(item) for item in ingredients}
    for name in patch.get("remove", []):
        result.pop(str(name).casefold(), None)
    for old_name, value in patch.get("replace", {}).items():
        if old_name.casefold() not in result:
            raise ValueError(f"{path}: ingredient replacement references unknown ingredient '{old_name}'")
        result.pop(old_name.casefold())
        item = value if isinstance(value, dict) else {"name": old_name, "quantity": value}
        ingredient = Ingredient(str(item.get("name", old_name)), str(item.get("quantity", "")))
        result[ingredient.name.casefold()] = ingredient
    for item in patch.get("add", []):
        if isinstance(item, str):
            ingredient = Ingredient(item)
        else:
            ingredient = Ingredient(str(item["name"]), str(item.get("quantity", "")))
        result[ingredient.name.casefold()] = ingredient
    return list(result.values())


def _build_variants(metadata: dict, base_steps: list[Step], portions: int, path: Path) -> list[RecipeVariant]:
    declarations = metadata.get("variants", [])
    if not declarations:
        return []
    if not isinstance(declarations, list):
        raise ValueError(f"{path}: variants must be a list")

    ids = [str(item.get("id", "")) for item in declarations]
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", item_id) for item_id in ids):
        raise ValueError(f"{path}: variant ids must use lowercase letters, numbers and hyphens")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: variant ids must be unique")
    if sum(bool(item.get("default")) for item in declarations) > 1:
        raise ValueError(f"{path}: only one variant may be the default")
    default_id = next((item["id"] for item in declarations if item.get("default")), ids[0])

    variants: list[RecipeVariant] = []
    for declaration in declarations:
        steps = copy.deepcopy(base_steps)
        changes = declaration.get("steps", {}) or {}
        base_ids = {step.id for step in steps}
        referenced = set(changes.get("remove", [])) | set(changes.get("replace", {}).keys())
        for mapping_name in ("before", "after"):
            referenced |= set(changes.get(mapping_name, {}).keys())
        unknown = referenced - base_ids
        if unknown:
            raise ValueError(
                f"{path}: variant '{declaration['id']}' references unknown step(s): {', '.join(sorted(unknown))}"
            )

        replacements: dict[str, Step] = {}
        for step_id, fragment in changes.get("replace", {}).items():
            parsed = _parse_steps(str(fragment), path)
            if len(parsed) != 1:
                raise ValueError(f"{path}: replacement for '{step_id}' must contain exactly one step")
            replacements[step_id] = parsed[0]

        def inserted(mapping: dict, step_id: str) -> list[Step]:
            fragments = mapping.get(step_id, [])
            if isinstance(fragments, str):
                fragments = [fragments]
            return [step for fragment in fragments for step in _parse_steps(str(fragment), path)]

        resolved: list[Step] = []
        for step in steps:
            resolved.extend(inserted(changes.get("before", {}), step.id))
            if step.id not in changes.get("remove", []):
                resolved.append(replacements.get(step.id, step))
            resolved.extend(inserted(changes.get("after", {}), step.id))
        resolved_ids = [step.id for step in resolved]
        if len(resolved_ids) != len(set(resolved_ids)):
            raise ValueError(f"{path}: variant '{declaration['id']}' produces duplicate step ids")

        ingredients = _patch_ingredients(_collect_ingredients(resolved), declaration.get("ingredients", {}) or {}, path)
        equipment = _collect_equipment(resolved)
        equipment_patch = declaration.get("equipment", {}) or {}
        removed_equipment = {str(item).casefold() for item in equipment_patch.get("remove", [])}
        equipment = [item for item in equipment if item.casefold() not in removed_equipment]
        equipment.extend(item for item in equipment_patch.get("add", []) if item not in equipment)

        proxy = type("VariantRecipe", (), {"ingredients": ingredients, "portions": portions})()
        variants.append(
            RecipeVariant(
                id=declaration["id"],
                name=str(declaration.get("name", declaration["id"])),
                description=str(declaration.get("description", "")),
                default=declaration["id"] == default_id,
                steps=resolved,
                ingredients=ingredients,
                equipment=equipment,
                prep_time=str(declaration.get("prep_time", metadata.get("prep_time", ""))),
                total_time=str(declaration.get("total_time", metadata.get("total_time", ""))),
                appliances=copy.deepcopy(declaration.get("appliances", metadata.get("appliances", {}))),
                tags=list(metadata.get("tags", [])),
                metadata={
                    **copy.deepcopy(metadata),
                    "appliances": copy.deepcopy(declaration.get("appliances", metadata.get("appliances", {}))),
                },
                nutrition=calculate_recipe_nutrition(proxy),
                shopping=evaluate_recipe_shopping(proxy),
            )
        )
    return variants


def parse_recipe(path: Path, validate: bool = True, root: Path = ROOT) -> Recipe:
    source = path.read_text(encoding="utf-8")
    metadata: dict = {}
    if source.startswith("---"):
        _, raw_meta, source = source.split("---", 2)
        metadata = yaml.safe_load(raw_meta) or {}

    title = metadata.get("title")
    body_lines: list[str] = []
    for raw in source.splitlines():
        line = raw.strip()
        if line.startswith("## ") and not title:
            title = line[3:].strip()
            continue
        body_lines.append(raw)

    steps = _parse_steps("\n".join(body_lines), path)
    all_ingredients = _collect_ingredients(steps)
    all_equipment = _collect_equipment(steps)

    portions = int(metadata.get("portions", 4))
    scaling = metadata.get("scaling", {})
    if isinstance(scaling, bool):
        scaling = {"enabled": scaling}
    scalable = bool(scaling.get("enabled", True))
    scaling_note = str(scaling.get("note" if scalable else "reason", "")).strip()
    if not scalable and not scaling_note:
        raise RecipeValidationError(path, "scaling.reason", None, "a non-scalable recipe must declare scaling.reason")

    recipe = Recipe(
        slug=path.stem,
        title=title or path.stem.replace("-", " ").title(),
        portions=portions,
        description=metadata.get("description", ""),
        tags=list(metadata.get("tags", [])),
        image=metadata.get("image", ""),
        steps=steps,
        ingredients=all_ingredients,
        equipment=all_equipment,
        metadata=metadata,
        prep_time=str(metadata.get("prep_time", "")).strip(),
        total_time=str(metadata.get("total_time", "")).strip(),
        scalable=scalable,
        min_portions=int(scaling.get("min_portions", 1)),
        max_portions=int(scaling.get("max_portions", max(12, portions))),
        portion_step=int(scaling.get("step", 1)),
        scaling_note=scaling_note,
    )
    recipe.nutrition = calculate_recipe_nutrition(recipe, db_path=root / ".gram/ingredients.yaml")
    recipe.shopping = evaluate_recipe_shopping(recipe, db_path=root / ".gram/ingredients.yaml")
    recipe.variants = _build_variants(metadata, steps, portions, path)

    if validate:
        validate_recipe_contract(recipe, path, metadata, root=root)

    return recipe
