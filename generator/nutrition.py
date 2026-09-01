"""Nutritional data and calculation engine for CookGram.

Uses official ANSES CIQUAL / Open Food Facts reference values per 100g.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from .models import Recipe

# Nutritional values per 100g of edible portion (CIQUAL / Open Food Facts)
CIQUAL_NUTRITION_PER_100G: dict[str, dict[str, float]] = {
    "ail": {"calories": 131, "protein": 6.4, "carbs": 23.5, "fat": 0.5},
    "concentre-de-tomate": {"calories": 96, "protein": 4.8, "carbs": 14.8, "fat": 0.6},
    "coriandre-fraiche": {"calories": 28, "protein": 2.1, "carbs": 1.9, "fat": 0.5},
    "courgette": {"calories": 17, "protein": 1.2, "carbs": 1.8, "fat": 0.3},
    "curry-en-poudre": {"calories": 337, "protein": 12.7, "carbs": 32.2, "fat": 13.8},
    "eau": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
    "filet-de-poulet": {"calories": 110, "protein": 23.9, "carbs": 0.0, "fat": 1.2},
    "huile-vegetale": {"calories": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "lait-de-coco": {"calories": 181, "protein": 1.6, "carbs": 2.8, "fat": 18.0},
    "magret-de-canard": {"calories": 230, "protein": 25.0, "carbs": 0.0, "fat": 14.0},
    "miel": {"calories": 327, "protein": 0.4, "carbs": 81.1, "fat": 0.0},
    "oignon": {"calories": 39, "protein": 1.3, "carbs": 7.1, "fat": 0.2},
    "poivre-moulu": {"calories": 283, "protein": 10.4, "carbs": 38.3, "fat": 3.3},
    "poivron": {"calories": 28, "protein": 1.1, "carbs": 4.9, "fat": 0.3},
    "riz-basmati": {"calories": 355, "protein": 8.5, "carbs": 77.0, "fat": 0.9},
    "sel": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
}


def parse_quantity_grams(quantity_str: str, ingredient_slug: str = "") -> float:
    """Estimates the weight in grams from a human-readable Gram quantity string."""
    if not quantity_str:
        return 0.0

    raw = quantity_str.lower().strip()

    # Direct grams: "800 g", "200g"
    m_g = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:g|gr)\b", raw)
    if m_g:
        return float(m_g.group(1).replace(",", "."))

    # Kilograms: "1.2 kg"
    m_kg = re.search(r"(\d+(?:[.,]\d+)?)\s*kg\b", raw)
    if m_kg:
        return float(m_kg.group(1).replace(",", ".")) * 1000.0

    # Milliliters: "270 ml"
    m_ml = re.search(r"(\d+(?:[.,]\d+)?)\s*ml\b", raw)
    if m_ml:
        return float(m_ml.group(1).replace(",", "."))

    # Centiliters: "25 cl"
    m_cl = re.search(r"(\d+(?:[.,]\d+)?)\s*cl\b", raw)
    if m_cl:
        return float(m_cl.group(1).replace(",", ".")) * 10.0

    # Liters: "1 l"
    m_l = re.search(r"(\d+(?:[.,]\d+)?)\s*l\b", raw)
    if m_l:
        return float(m_l.group(1).replace(",", ".")) * 1000.0

    # Tablespoons (c. à soupe ~ 15g)
    m_cs = re.search(r"(\d+(?:[.,]\d+)?|\d+/\d+)\s*(?:c\.\s*à\s*soupe|cuill[èe]res?\s*à\s*soupe)", raw)
    if m_cs:
        val = eval_fraction(m_cs.group(1))
        return val * 15.0

    # Teaspoons (c. à café ~ 5g)
    m_cc = re.search(r"(\d+(?:[.,]\d+)?|\d+/\d+)\s*(?:c\.\s*à\s*caf[ée]|cuill[èe]res?\s*à\s*caf[ée])", raw)
    if m_cc:
        val = eval_fraction(m_cc.group(1))
        return val * 5.0

    # Pinches (pincée ~ 0.5g)
    m_pinc = re.search(r"(\d+)\s*pinc[ée]es?", raw)
    if m_pinc:
        return float(m_pinc.group(1)) * 0.5

    # Cloves (gousse ~ 5g)
    m_gousse = re.search(r"(\d+)\s*gousses?", raw)
    if m_gousse:
        return float(m_gousse.group(1)) * 5.0

    # Pure count: e.g. "3" for magrets (~350g each)
    m_num = re.match(r"^(\d+(?:[.,]\d+)?)$", raw)
    if m_num:
        count = float(m_num.group(1).replace(",", "."))
        if "magret" in ingredient_slug:
            return count * 350.0
        return count * 100.0

    return 10.0


def eval_fraction(token: str) -> float:
    token = token.replace(",", ".")
    if "/" in token:
        parts = token.split("/")
        return float(parts[0]) / float(parts[1])
    return float(token)


def get_ingredient_slug(ingredient_name: str, database: dict) -> str:
    """Finds matching slug in database by checking slug, name and aliases."""
    name_clean = ingredient_name.casefold().strip()
    for slug, data in database.items():
        if slug == name_clean or data.get("name", "").casefold() == name_clean:
            return slug
        for alias in data.get("aliases", []):
            if alias.casefold() == name_clean:
                return slug
    return re.sub(r"[^\w]+", "-", name_clean)


def calculate_recipe_nutrition(recipe: Recipe, db_path: Path | None = None) -> dict[str, float]:
    """Calculates nutrition per portion for a given recipe."""
    if db_path is None:
        db_path = Path(".gram/ingredients.yaml")

    database = {}
    if db_path.exists():
        payload = yaml.safe_load(db_path.read_text(encoding="utf-8")) or {}
        database = payload.get("ingredients", {})

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    breakdown_items = []

    for item in recipe.ingredients:
        slug = get_ingredient_slug(item.name, database)
        data = database.get(slug, {})
        nutrition = data.get("nutrition") or CIQUAL_NUTRITION_PER_100G.get(slug)

        if not nutrition:
            continue

        grams = parse_quantity_grams(item.quantity, slug)
        factor = grams / 100.0

        item_cal = nutrition.get("calories", 0.0) * factor
        total_calories += item_cal
        total_protein += nutrition.get("protein", 0.0) * factor
        total_carbs += nutrition.get("carbs", 0.0) * factor
        total_fat += nutrition.get("fat", 0.0) * factor

        breakdown_items.append({
            "name": item.name,
            "quantity": item.quantity,
            "calories_raw": item_cal,
        })

    portions = max(1, recipe.portions)

    formatted_breakdown = []
    for bi in sorted(breakdown_items, key=lambda x: x["calories_raw"], reverse=True):
        cals_per_portion = round(bi["calories_raw"] / portions)
        pct = round((bi["calories_raw"] / total_calories * 100), 1) if total_calories else 0.0
        formatted_breakdown.append({
            "name": bi["name"],
            "quantity": bi["quantity"],
            "calories": cals_per_portion,
            "percentage": pct,
        })

    return {
        "calories": round(total_calories / portions),
        "protein": round(total_protein / portions, 1),
        "carbs": round(total_carbs / portions, 1),
        "fat": round(total_fat / portions, 1),
        "breakdown": formatted_breakdown,
    }


def enrich_ingredient_database(
    ingredients_path: Path = Path(".gram/ingredients.yaml"),
    provenance_path: Path = Path(".gram/ingredient-provenance.yaml"),
) -> None:
    """Populates ingredients.yaml with CIQUAL nutrition and updates provenance.yaml."""
    if not ingredients_path.exists():
        return

    ing_data = yaml.safe_load(ingredients_path.read_text(encoding="utf-8")) or {}
    ingredients = ing_data.get("ingredients", {})

    prov_data = {}
    if provenance_path.exists():
        prov_data = yaml.safe_load(provenance_path.read_text(encoding="utf-8")) or {}
    prov_ingredients = prov_data.setdefault("ingredients", {})

    for slug, values in CIQUAL_NUTRITION_PER_100G.items():
        if slug in ingredients:
            ingredients[slug]["nutrition"] = values
            prov_ingredients[slug] = {
                "status": "verified",
                "locked": False,
                "sources": ["ciqual"],
                "note": "Valeurs nutritionnelles pour 100g issues de la table CIQUAL ANSES.",
            }

    # Re-write ingredients.yaml
    ing_header = (
        "# Base locale CookGram enrichie avec les données nutritionnelles ANSES CIQUAL.\n"
    )
    ingredients_path.write_text(ing_header + yaml.safe_dump(ing_data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    # Re-write ingredient-provenance.yaml
    prov_header = (
        "# Suivi de la provenance des ingrédients et niveaux de confiance.\n"
    )
    provenance_path.write_text(prov_header + yaml.safe_dump(prov_data, sort_keys=False, allow_unicode=True), encoding="utf-8")


if __name__ == "__main__":
    enrich_ingredient_database()
    print("Database enriched successfully with ANSES CIQUAL nutrition!")
