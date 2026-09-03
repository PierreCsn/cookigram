"""Resolve optional ingredient icons without ever breaking text rendering."""

import re
from pathlib import Path
from typing import Any

import yaml

from .nutrition import get_ingredient_slug

ROOT = Path(__file__).resolve().parents[1]

# Several Gram entries describe a preparation or a cut of the same ingredient.
# Keep one visual vocabulary for those families instead of duplicating SVGs.
ICON_FAMILY_BY_SLUG = {
    "creme-fraiche-epaisse": "creme-fraiche",
    "creme-fraiche-liquide": "creme-fraiche",
    "parmesan": "parmesan",
    "saumon-frais": "saumon",
    "saumon-fume": "saumon",
    "poulet": "poulet",
    "filet-de-poulet": "poulet",
    "cuisse-de-poulet": "poulet",
    "paleron-de-boeuf": "boeuf",
    "porc-hache": "porc",
    "filet-mignon-de-porc": "porc",
    "echine-de-porc": "porc",
    "roti-de-porc": "porc",
    "riz-a-risotto": "riz",
    "riz-basmati": "riz",
    "riz-long-blanc": "riz",
    "farfalle": "pates",
    "penne": "pates",
    "torsades": "pates",
    "nouilles-chinoises": "pates",
    "champignons-de-paris": "champignon",
    "concentre-de-tomate": "concentre-tomate",
    "cube-de-bouillon-de-volaille": "bouillon-volaille",
    "moutarde-de-dijon": "moutarde",
    "persil-frais": "persil",
    "coriandre-fraiche": "coriandre",
    "piment-rouge": "piment",
    "piment-de-cayenne": "piment",
    "curry-en-poudre": "curry",
    "ail-en-poudre": "ail",
    "tomate-cerise": "tomate",
    "tomates-concassees": "tomate",
    "poivron": "poivron",
    "poireau": "poireau",
    "laurier": "laurier",
    "thym": "thym",
    "basilic-frais": "basilic-frais",
    "lait": "lait",
    "lait-demi-ecreme": "lait",
    "noix-de-muscade": "noix-de-muscade",
    "bouillon-de-legumes": "bouillon-de-legumes",
    "oeuf": "oeuf",
    "miel": "miel",
    "olives-noires": "olives-noires",
    "paprika": "paprika",
    "sauce-soja": "sauce-soja",
    "concombre": "concombre",
    "aubergine": "aubergine",
    "courgette": "courgette",
    "chou-fleur": "chou-fleur",
    "petits-pois": "petits-pois",
    "crevettes": "crevettes",
    "feta": "feta",
    "cannelle": "cannelle",
    "cumin": "cumin",
    "curcuma": "curcuma",
    "maizena": "maizena",
    "lentilles-corail": "lentilles-corail",
}


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
        if slug == "ail" and re.search(r"\b(?:tête|têtes)\b", quantity, flags=re.IGNORECASE):
            return "ail-tete"
        return ICON_FAMILY_BY_SLUG.get(slug, slug)


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
