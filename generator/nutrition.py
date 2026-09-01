"""Nutritional data and calculation engine for CookiGram.

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
    "ail-en-poudre": {"calories": 331, "protein": 16.5, "carbs": 64.0, "fat": 0.7},
    "amande-en-poudre": {"calories": 634, "protein": 21.9, "carbs": 5.4, "fat": 55.8},
    "aneth": {"calories": 43, "protein": 3.5, "carbs": 7.0, "fat": 1.1},
    "aubergine": {"calories": 21, "protein": 0.9, "carbs": 2.5, "fat": 0.2},
    "basilic-frais": {"calories": 23, "protein": 3.2, "carbs": 2.7, "fat": 0.6},
    "beurre": {"calories": 751, "protein": 0.8, "carbs": 0.7, "fat": 82.5},
    "bouillon-de-legumes": {"calories": 15, "protein": 0.5, "carbs": 2.5, "fat": 0.3},
    "bouquet-garni": {"calories": 10, "protein": 0.5, "carbs": 1.5, "fat": 0.2},
    "brocoli": {"calories": 35, "protein": 3.1, "carbs": 2.4, "fat": 0.6},
    "cannelle": {"calories": 261, "protein": 4.0, "carbs": 56.1, "fat": 1.2},
    "capres": {"calories": 23, "protein": 2.4, "carbs": 4.9, "fat": 0.9},
    "carotte": {"calories": 40, "protein": 0.8, "carbs": 7.6, "fat": 0.3},
    "champignons-de-paris": {"calories": 22, "protein": 2.5, "carbs": 1.4, "fat": 0.4},
    "chapelure": {"calories": 360, "protein": 12.0, "carbs": 72.0, "fat": 2.0},
    "chou-fleur": {"calories": 25, "protein": 1.9, "carbs": 2.4, "fat": 0.3},
    "citron": {"calories": 29, "protein": 1.1, "carbs": 9.3, "fat": 0.3},
    "concentre-de-tomate": {"calories": 96, "protein": 4.8, "carbs": 14.8, "fat": 0.6},
    "coriandre-fraiche": {"calories": 28, "protein": 2.1, "carbs": 1.9, "fat": 0.5},
    "courge-butternut": {"calories": 45, "protein": 1.0, "carbs": 9.6, "fat": 0.1},
    "courgette": {"calories": 17, "protein": 1.2, "carbs": 1.8, "fat": 0.3},
    "creme-fraiche-epaisse": {"calories": 292, "protein": 2.2, "carbs": 3.0, "fat": 30.0},
    "creme-fraiche-liquide": {"calories": 292, "protein": 2.2, "carbs": 3.0, "fat": 30.0},
    "cube-de-bouillon-de-boeuf": {"calories": 240, "protein": 12.0, "carbs": 18.0, "fat": 12.0},
    "cube-de-bouillon-de-legumes": {"calories": 230, "protein": 8.0, "carbs": 20.0, "fat": 12.0},
    "cube-de-bouillon-de-volaille": {"calories": 240, "protein": 12.0, "carbs": 20.0, "fat": 12.0},
    "cuisse-de-poulet": {"calories": 180, "protein": 19.0, "carbs": 0.0, "fat": 11.5},
    "cumin": {"calories": 375, "protein": 17.8, "carbs": 44.2, "fat": 22.3},
    "curcuma": {"calories": 312, "protein": 7.8, "carbs": 58.2, "fat": 3.3},
    "curry-en-poudre": {"calories": 337, "protein": 12.7, "carbs": 32.2, "fat": 13.8},
    "eau": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
    "echalote": {"calories": 72, "protein": 2.5, "carbs": 14.5, "fat": 0.1},
    "echine-de-porc": {"calories": 245, "protein": 19.5, "carbs": 0.0, "fat": 18.5},
    "emmental-rape": {"calories": 380, "protein": 28.5, "carbs": 0.5, "fat": 29.5},
    "epinards": {"calories": 23, "protein": 2.9, "carbs": 1.5, "fat": 0.4},
    "farfalle": {"calories": 355, "protein": 12.5, "carbs": 72.0, "fat": 1.5},
    "farine": {"calories": 355, "protein": 10.0, "carbs": 71.0, "fat": 1.2},
    "filet-de-poisson": {"calories": 80, "protein": 17.5, "carbs": 0.0, "fat": 1.0},
    "filet-de-poulet": {"calories": 110, "protein": 23.9, "carbs": 0.0, "fat": 1.2},
    "filet-mignon-de-porc": {"calories": 120, "protein": 22.0, "carbs": 0.0, "fat": 3.5},
    "fond-de-legumes": {"calories": 180, "protein": 6.0, "carbs": 25.0, "fat": 5.0},
    "fond-de-viande": {"calories": 190, "protein": 10.0, "carbs": 20.0, "fat": 6.0},
    "gingembre": {"calories": 80, "protein": 1.8, "carbs": 15.8, "fat": 0.8},
    "gingembre-moulu": {"calories": 335, "protein": 9.0, "carbs": 71.6, "fat": 4.2},
    "graine-de-moutarde": {"calories": 508, "protein": 26.1, "carbs": 28.1, "fat": 36.2},
    "graine-de-sesame": {"calories": 573, "protein": 17.7, "carbs": 23.4, "fat": 49.7},
    "herbes-de-provence": {"calories": 275, "protein": 9.0, "carbs": 45.0, "fat": 7.0},
    "huile-de-coco": {"calories": 892, "protein": 0.0, "carbs": 0.0, "fat": 99.1},
    "huile-de-sesame": {"calories": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "huile-olive": {"calories": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "huile-vegetale": {"calories": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "jus-de-citron-vert": {"calories": 25, "protein": 0.4, "carbs": 2.8, "fat": 0.1},
    "la-vache-qui-rit": {"calories": 240, "protein": 10.5, "carbs": 6.5, "fat": 19.5},
    "lait-de-coco": {"calories": 181, "protein": 1.6, "carbs": 2.8, "fat": 18.0},
    "lait-de-soja": {"calories": 45, "protein": 3.3, "carbs": 2.2, "fat": 1.8},
    "lait-demi-ecreme": {"calories": 46, "protein": 3.3, "carbs": 4.8, "fat": 1.6},
    "lardons": {"calories": 280, "protein": 16.0, "carbs": 0.5, "fat": 24.0},
    "laurier": {"calories": 313, "protein": 7.6, "carbs": 48.7, "fat": 8.4},
    "lentilles-corail": {"calories": 338, "protein": 24.0, "carbs": 52.0, "fat": 1.5},
    "magret-de-canard": {"calories": 230, "protein": 25.0, "carbs": 0.0, "fat": 14.0},
    "mais": {"calories": 96, "protein": 3.2, "carbs": 18.7, "fat": 1.2},
    "maizena": {"calories": 355, "protein": 0.3, "carbs": 87.0, "fat": 0.1},
    "mascarpone": {"calories": 412, "protein": 4.5, "carbs": 3.5, "fat": 42.0},
    "miel": {"calories": 327, "protein": 0.4, "carbs": 81.1, "fat": 0.0},
    "moutarde-de-dijon": {"calories": 150, "protein": 7.0, "carbs": 5.0, "fat": 11.0},
    "noix-de-muscade": {"calories": 525, "protein": 5.8, "carbs": 49.3, "fat": 36.3},
    "nouilles-chinoises": {"calories": 350, "protein": 10.0, "carbs": 70.0, "fat": 2.5},
    "oeuf": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5},
    "oignon": {"calories": 39, "protein": 1.3, "carbs": 7.1, "fat": 0.2},
    "olives-noires": {"calories": 130, "protein": 1.0, "carbs": 3.0, "fat": 13.0},
    "olives-vertes": {"calories": 145, "protein": 1.0, "carbs": 3.8, "fat": 15.3},
    "origan": {"calories": 265, "protein": 9.0, "carbs": 68.9, "fat": 4.3},
    "pain-de-mie": {"calories": 265, "protein": 8.5, "carbs": 49.0, "fat": 3.5},
    "paleron-de-boeuf": {"calories": 155, "protein": 21.0, "carbs": 0.0, "fat": 8.0},
    "paprika": {"calories": 282, "protein": 14.1, "carbs": 34.0, "fat": 12.9},
    "parmesan": {"calories": 431, "protein": 35.8, "carbs": 0.0, "fat": 32.7},
    "pate-miso": {"calories": 198, "protein": 11.7, "carbs": 26.5, "fat": 6.0},
    "penne": {"calories": 355, "protein": 12.5, "carbs": 72.0, "fat": 1.5},
    "persil-frais": {"calories": 36, "protein": 3.0, "carbs": 3.5, "fat": 0.8},
    "petits-pois": {"calories": 70, "protein": 5.5, "carbs": 9.5, "fat": 0.5},
    "piment-de-cayenne": {"calories": 318, "protein": 12.0, "carbs": 56.6, "fat": 17.3},
    "piment-rouge": {"calories": 40, "protein": 1.9, "carbs": 7.0, "fat": 0.4},
    "poireau": {"calories": 31, "protein": 1.5, "carbs": 4.0, "fat": 0.3},
    "poivre-moulu": {"calories": 283, "protein": 10.4, "carbs": 38.3, "fat": 3.3},
    "poivron": {"calories": 28, "protein": 1.1, "carbs": 4.9, "fat": 0.3},
    "pomme-de-terre": {"calories": 80, "protein": 2.0, "carbs": 17.0, "fat": 0.1},
    "porc-hache": {"calories": 263, "protein": 17.0, "carbs": 0.0, "fat": 21.5},
    "poulet": {"calories": 121, "protein": 21.0, "carbs": 0.0, "fat": 3.8},
    "riz-a-risotto": {"calories": 355, "protein": 7.5, "carbs": 78.0, "fat": 0.8},
    "riz-basmati": {"calories": 355, "protein": 8.5, "carbs": 77.0, "fat": 0.9},
    "roti-de-porc": {"calories": 180, "protein": 24.0, "carbs": 0.0, "fat": 9.0},
    "sauce-soja": {"calories": 53, "protein": 8.1, "carbs": 4.9, "fat": 0.1},
    "sauce-tomate": {"calories": 50, "protein": 1.5, "carbs": 7.0, "fat": 1.5},
    "saumon-frais": {"calories": 208, "protein": 20.4, "carbs": 0.0, "fat": 13.4},
    "saumon-fume": {"calories": 185, "protein": 21.5, "carbs": 0.5, "fat": 11.0},
    "sel": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
    "sucre": {"calories": 400, "protein": 0.0, "carbs": 100.0, "fat": 0.0},
    "sucre-roux": {"calories": 390, "protein": 0.0, "carbs": 97.5, "fat": 0.0},
    "tahini": {"calories": 595, "protein": 17.0, "carbs": 21.0, "fat": 54.0},
    "thym": {"calories": 276, "protein": 9.1, "carbs": 63.9, "fat": 7.4},
    "tomate-cerise": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "tomates-concassees": {"calories": 25, "protein": 1.2, "carbs": 3.8, "fat": 0.2},
    "torsades": {"calories": 355, "protein": 12.5, "carbs": 72.0, "fat": 1.5},
    "vin-blanc": {"calories": 82, "protein": 0.1, "carbs": 1.5, "fat": 0.0},
    "vinaigre-blanc": {"calories": 18, "protein": 0.0, "carbs": 0.5, "fat": 0.0},
    "vinaigre-de-riz": {"calories": 18, "protein": 0.1, "carbs": 4.0, "fat": 0.0},
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
        if "echalote" in ingredient_slug:
            return count * 25.0
        if "bouillon" in ingredient_slug:
            return count * 10.0
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
        "# Base locale CookiGram enrichie avec les données nutritionnelles ANSES CIQUAL.\n"
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
