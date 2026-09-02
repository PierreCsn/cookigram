"""Canonical schema and contract validation for CookiGram .gram recipes."""

import re
from pathlib import Path
from typing import Any

import yaml

from .models import Recipe

ROOT = Path(__file__).resolve().parents[1]


class RecipeValidationError(ValueError):
    """Raised when a recipe does not satisfy the canonical contract."""

    def __init__(self, path: Path, field: str, value: Any, message: str):
        self.path = path
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"{path}: field '{field}': {message} (got {value!r})")


def get_known_ingredient_names(root: Path = ROOT) -> set[str]:
    db_path = root / ".gram" / "ingredients.yaml"
    if not db_path.exists():
        return set()
    payload = yaml.safe_load(db_path.read_text(encoding="utf-8")) or {}
    ingredients = payload.get("ingredients", {})
    known = set()
    for item in ingredients.values():
        if "name" in item:
            known.add(item["name"].strip().casefold())
        for alias in item.get("aliases", []):
            known.add(alias.strip().casefold())
    return known


def validate_recipe_contract(recipe: Recipe, path: Path, metadata: dict[str, Any], root: Path = ROOT) -> None:
    """Strict validation of a parsed recipe against the CookiGram contract."""
    # 1. Title
    title = metadata.get("title")
    if not isinstance(title, str) or not title.strip():
        raise RecipeValidationError(path, "title", title, "recipe must have a non-empty string title in frontmatter")

    # 2. Portions & Steps
    portions = metadata.get("portions")
    if not isinstance(portions, int) or portions <= 0:
        raise RecipeValidationError(path, "portions", portions, "portions must be a positive integer")

    if not recipe.steps:
        raise RecipeValidationError(path, "steps", len(recipe.steps), "recipe must have at least one step")

    for step in recipe.steps:
        if not step.action or not step.action.strip():
            raise RecipeValidationError(path, "steps.action", step.action, "step action cannot be empty")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", step.id):
            raise RecipeValidationError(path, "steps.id", step.id, f"invalid step id format '{step.id}'")
        for timer in step.timers:
            if timer.get("seconds", 0) <= 0:
                raise RecipeValidationError(
                    path, "steps.timer", timer, f"timer duration must be > 0 in step '{step.id}'"
                )

    # 3. Tags, prep_time, total_time
    tags = metadata.get("tags")
    if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t.strip() for t in tags):
        raise RecipeValidationError(path, "tags", tags, "tags must be a non-empty list of non-empty strings")

    prep_time = metadata.get("prep_time")
    if not isinstance(prep_time, str) or not prep_time.strip():
        raise RecipeValidationError(path, "prep_time", prep_time, "prep_time must be declared as a non-empty string")

    total_time = metadata.get("total_time")
    if not isinstance(total_time, str) or not total_time.strip():
        raise RecipeValidationError(path, "total_time", total_time, "total_time must be declared as a non-empty string")

    # 4. Source & Author
    source = metadata.get("source")
    if not isinstance(source, str) or not source.strip():
        raise RecipeValidationError(path, "source", source, "source must be a non-empty string or URL")

    author = metadata.get("author")
    if not isinstance(author, str) or not author.strip():
        raise RecipeValidationError(path, "author", author, "author must be a non-empty string")

    # 5. Image & Image Credits
    image = metadata.get("image")
    if not isinstance(image, str) or not image.strip():
        raise RecipeValidationError(path, "image", image, "image must be declared as a relative path string")

    image_file = root / "static" / image
    if not image_file.is_file():
        raise RecipeValidationError(path, "image", image, f"image file '{image_file}' does not exist on disk")

    image_credit = metadata.get("image_credit")
    if not isinstance(image_credit, dict):
        raise RecipeValidationError(
            path, "image_credit", image_credit, "image_credit must be a dictionary with author, source, and license"
        )
    for credit_field in ("author", "source", "license"):
        val = image_credit.get(credit_field)
        if not isinstance(val, str) or not val.strip():
            raise RecipeValidationError(
                path, f"image_credit.{credit_field}", val, f"image_credit.{credit_field} is required"
            )

    # 6. Scaling
    if recipe.scalable:
        if recipe.min_portions <= 0:
            raise RecipeValidationError(path, "scaling.min_portions", recipe.min_portions, "min_portions must be > 0")
        if recipe.max_portions < recipe.min_portions:
            raise RecipeValidationError(
                path,
                "scaling.max_portions",
                recipe.max_portions,
                f"max_portions ({recipe.max_portions}) cannot be smaller than min_portions ({recipe.min_portions})",
            )
        if not (recipe.min_portions <= recipe.portions <= recipe.max_portions):
            raise RecipeValidationError(
                path,
                "scaling.portions",
                recipe.portions,
                f"base portions ({recipe.portions}) must be within [min_portions ({recipe.min_portions}), max_portions ({recipe.max_portions})]",
            )
        if recipe.portion_step <= 0:
            raise RecipeValidationError(path, "scaling.step", recipe.portion_step, "scaling step must be > 0")
    else:
        if not recipe.scaling_note or not recipe.scaling_note.strip():
            raise RecipeValidationError(path, "scaling.reason", None, "non-scalable recipe must declare scaling.reason")

    # 7. Ingrédients dans la base locale
    known_ingredients = get_known_ingredient_names(root)
    if known_ingredients:
        all_ingredients = list(recipe.ingredients)
        for variant in recipe.variants:
            all_ingredients.extend(variant.ingredients)

        for item in all_ingredients:
            if item.name.strip().casefold() not in known_ingredients:
                raise RecipeValidationError(
                    path, "ingredients", item.name, f"ingredient '{item.name}' is missing from .gram/ingredients.yaml"
                )

    # 8. Réglages d'appareil (appliances)
    appliances = metadata.get("appliances")
    if appliances is not None:
        if not isinstance(appliances, dict):
            raise RecipeValidationError(path, "appliances", appliances, "appliances must be a dictionary")
        for app_name, models in appliances.items():
            if not isinstance(models, list):
                raise RecipeValidationError(
                    path,
                    f"appliances.{app_name}",
                    models,
                    f"models for appliance '{app_name}' must be a list of supported model strings",
                )
