"""Resolve optional ingredient icons without ever breaking text rendering."""

import re
from pathlib import Path
from typing import Any

import yaml

from .nutrition import get_ingredient_slug

ROOT = Path(__file__).resolve().parents[1]


class IngredientIconResolver:
    """Map ingredient names to existing icon assets using the Gram database."""

    def __init__(self, root: Path = ROOT) -> None:
        database_path = root / ".gram" / "ingredients.yaml"
        payload = yaml.safe_load(database_path.read_text(encoding="utf-8")) or {}
        self.database = payload.get("ingredients", {})
        self.icons_dir = root / "static" / "icons" / "ingredients"

    def resolve(self, name: str, quantity: str = "") -> str:
        slug = get_ingredient_slug(name, self.database)
        icon_slug = self._variant_slug(slug, quantity)
        filename = f"{icon_slug}.svg"
        if not (self.icons_dir / filename).is_file():
            return ""
        return f"icons/ingredients/{filename}"

    @staticmethod
    def _variant_slug(slug: str, quantity: str) -> str:
        if slug != "ail":
            return slug
        if re.search(r"\b(?:tête|têtes)\b", quantity, flags=re.IGNORECASE):
            return "ail-tete"
        return slug


def attach_ingredient_icons(recipe: Any, resolver: IngredientIconResolver) -> None:
    """Attach icon paths to recipe views and their shopping projections."""
    views = [recipe, *recipe.variants]
    for view in views:
        for ingredient in view.ingredients:
            ingredient.icon = resolver.resolve(ingredient.name, ingredient.quantity)
        for step in view.steps:
            for ingredient in step.ingredients:
                ingredient.icon = resolver.resolve(ingredient.name, ingredient.quantity)
        for group in view.shopping.get("aisles", {}).values():
            for item in group:
                item["icon"] = resolver.resolve(item["slug"], item.get("raw_quantity", ""))
        for item in view.shopping.get("staples", []):
            item["icon"] = resolver.resolve(item["slug"], item.get("raw_quantity", ""))
