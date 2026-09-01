import re
from pathlib import Path

import yaml

from .models import Recipe

STAPLE_SLUGS = {
    "eau",
    "sel",
    "poivre",
    "poivre-moulu",
    "huile-vegetale",
    "huile-olive",
}

CATEGORY_TO_AISLE = {
    "Viandes": "Boucherie & Volailles",
    "Poissons": "Poissonnerie",
    "Légumes et aromates": "Fruits & Légumes",
    "Fruits": "Fruits & Légumes",
    "Produits laitiers": "Frais & Crèmerie",
    "Céréales et féculents": "Épicerie & Féculents",
    "Boissons et liquides": "Boissons & Vins",
    "Condiments": "Condiments & Épices",
    "Herbes et épices": "Condiments & Épices",
    "Matières grasses": "Fond de placard",
    "Produits sucrés": "Épicerie & Féculents",
}


def clean_shopping_quantity(raw_qty: str) -> str:
    """Strips recipe-specific cooking directives to produce clean shopping notes."""
    if not raw_qty:
        return ""
    q = raw_qty.strip()
    q = re.sub(r",\s*sur\s+.*", "", q, flags=re.IGNORECASE)
    q = re.sub(r",\s*(?:sans peau|en morceaux|en dés|en lanières|coupé[es]*|épluché[es]*|émincé[es]*|plus selon|selon|facultatif|spécial|blancs).*$", "", q, flags=re.IGNORECASE)
    q = re.sub(r",?\s*\bémietté[es]*\b", "", q, flags=re.IGNORECASE)
    q = q.strip().rstrip(",")
    if q.isdigit():
        q = f"{q} pièces"
    return q


def evaluate_recipe_shopping(recipe: Recipe, db_path: Path | None = None) -> dict:
    """Evaluates ingredients to produce a real grocery shopping list."""
    if db_path is None:
        db_path = Path(".gram/ingredients.yaml")

    database = {}
    if db_path.exists():
        payload = yaml.safe_load(db_path.read_text(encoding="utf-8")) or {}
        database = payload.get("ingredients", {})

    from .nutrition import get_ingredient_slug

    to_buy_items = []
    staple_items = []

    for item in recipe.ingredients:
        slug = get_ingredient_slug(item.name, database)
        data = database.get(slug, {})

        if slug == "eau":
            # Tap water is non-purchasable
            continue

        clean_qty = clean_shopping_quantity(item.quantity)
        canonical_name = data.get("name", item.name.capitalize())
        category = data.get("category", "")

        is_staple = slug in STAPLE_SLUGS or data.get("pantry_staple", False)
        aisle = "Fond de placard" if is_staple else CATEGORY_TO_AISLE.get(category, "Épicerie & Féculents")

        entry = {
            "slug": slug,
            "name": canonical_name,
            "quantity": clean_qty,
            "raw_quantity": item.quantity,
            "aisle": aisle,
            "is_staple": is_staple,
        }

        if is_staple:
            staple_items.append(entry)
        else:
            to_buy_items.append(entry)

    # Group to_buy_items by aisle
    aisles_grouped = {}
    for it in to_buy_items:
        aisle = it["aisle"]
        aisles_grouped.setdefault(aisle, []).append(it)

    return {
        "to_buy_count": len(to_buy_items),
        "staples_count": len(staple_items),
        "aisles": aisles_grouped,
        "staples": staple_items,
    }
