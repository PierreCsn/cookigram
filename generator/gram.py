"""Small Gram reader for the MVP.

The public Recipe model deliberately isolates templates from parser details. This
reader supports the Gram constructs used by the UI; it can later be replaced by
an adapter over the official compiler without changing the PWA.
"""

import re
from pathlib import Path

import yaml

from .models import Ingredient, Recipe, Step
from .nutrition import calculate_recipe_nutrition
from .shopping import evaluate_recipe_shopping

ACTION = re.compile(r"^\[([^]]+)]\s*(.*)$")
SUBSTEP = re.compile(r"^[-*]\s+(.+)$")
INGREDIENT = re.compile(r"@([^@{}]+)\{([^}]*)}")
EQUIPMENT = re.compile(r"#([^#{}]+)\{[^}]*}")
TIMER = re.compile(r"~(?:_[\w-]+)?\{\s*(\d+(?:[.,]\d+)?)\s*(s|sec|m|min|h)\s*}", re.IGNORECASE)
TEMPERATURE = re.compile(r"\^\{\s*([^}]+)\s*}")


def _seconds(value: str, unit: str) -> int:
    number = float(value.replace(",", "."))
    factor = 3600 if unit.lower() == "h" else 60 if unit.lower() in {"m", "min"} else 1
    return round(number * factor)


def _clean(text: str) -> str:
    text = INGREDIENT.sub(lambda m: f"{m.group(1).strip()}" + (f" ({m.group(2).strip()})" if m.group(2).strip() else ""), text)
    text = EQUIPMENT.sub(lambda m: m.group(1).strip(), text)
    text = TIMER.sub(lambda m: f"{m.group(1)} {m.group(2)}", text)
    text = TEMPERATURE.sub(lambda m: m.group(1).strip(), text)
    return re.sub(r"\s+", " ", text).strip()


def parse_recipe(path: Path) -> Recipe:
    source = path.read_text(encoding="utf-8")
    metadata: dict = {}
    if source.startswith("---"):
        _, raw_meta, source = source.split("---", 2)
        metadata = yaml.safe_load(raw_meta) or {}

    title = metadata.get("title")
    steps: list[Step] = []
    all_ingredients: dict[str, Ingredient] = {}
    all_equipment: list[str] = []

    step_blocks: list[dict] = []
    current_block: dict | None = None

    for raw in source.splitlines():
        line = raw.strip()
        if line.startswith("## ") and not title:
            title = line[3:].strip()
            continue

        action_match = ACTION.match(line)
        if action_match:
            if current_block:
                step_blocks.append(current_block)
            action, body = action_match.groups()
            current_block = {
                "action": action.strip(),
                "body": body.strip(),
                "substeps": [],
                "raw_lines": [body.strip()] if body.strip() else [],
            }
            continue

        substep_match = SUBSTEP.match(line)
        if substep_match and current_block is not None:
            substep_text = substep_match.group(1).strip()
            current_block["substeps"].append(substep_text)
            current_block["raw_lines"].append(substep_text)
            continue

        if line and not line.startswith("#") and current_block is not None:
            current_block["raw_lines"].append(line)
            if not current_block["body"]:
                current_block["body"] = line
            else:
                current_block["body"] += " " + line

    if current_block:
        step_blocks.append(current_block)

    for block in step_blocks:
        action = block["action"]
        full_text = " ".join(block["raw_lines"])
        ingredients = [Ingredient(m.group(1).strip(), m.group(2).strip()) for m in INGREDIENT.finditer(full_text)]
        equipment = [m.group(1).strip() for m in EQUIPMENT.finditer(full_text)]
        timers = [
            {"seconds": _seconds(m.group(1), m.group(2)), "label": f"{m.group(1)} {m.group(2)}"}
            for m in TIMER.finditer(full_text)
        ]
        temperatures = [m.group(1).strip() for m in TEMPERATURE.finditer(full_text)]

        for ingredient in ingredients:
            key = ingredient.name.casefold()
            current = all_ingredients.get(key)
            if current is None or (not current.quantity and ingredient.quantity):
                all_ingredients[key] = ingredient
        for item in equipment:
            if item not in all_equipment:
                all_equipment.append(item)

        cleaned_body = _clean(block["body"])
        cleaned_substeps = [_clean(s) for s in block["substeps"]]

        steps.append(Step(
            action=action,
            text=cleaned_body,
            timers=timers,
            temperatures=temperatures,
            ingredients=ingredients,
            equipment=equipment,
            substeps=cleaned_substeps,
        ))

    portions = int(metadata.get("portions", 4))
    scaling = metadata.get("scaling", {})
    if isinstance(scaling, bool):
        scaling = {"enabled": scaling}
    scalable = bool(scaling.get("enabled", True))
    scaling_note = str(scaling.get("note" if scalable else "reason", "")).strip()
    if not scalable and not scaling_note:
        raise ValueError(f"{path}: a non-scalable recipe must declare scaling.reason")

    recipe = Recipe(
        slug=path.stem,
        title=title or path.stem.replace("-", " ").title(),
        portions=portions,
        description=metadata.get("description", ""),
        tags=list(metadata.get("tags", [])),
        image=metadata.get("image", ""),
        steps=steps,
        ingredients=list(all_ingredients.values()),
        equipment=all_equipment,
        metadata=metadata,
        prep_time=str(metadata.get("prep_time", "")).strip(),
        total_time=str(metadata.get("total_time", "")).strip(),
        scalable=scalable,
        min_portions=max(1, int(scaling.get("min_portions", 1))),
        max_portions=max(portions, int(scaling.get("max_portions", max(12, portions)))),
        portion_step=max(1, int(scaling.get("step", 1))),
        scaling_note=scaling_note,
    )
    recipe.nutrition = calculate_recipe_nutrition(recipe)
    recipe.shopping = evaluate_recipe_shopping(recipe)
    return recipe
