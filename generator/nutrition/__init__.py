"""CookiGram Nutrition Module.

Provides nutritional reference data, robust quantity parsing, density/piece-weight conversions,
coverage calculation, and source provenance tracking.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .calculator import calculate_recipe_nutrition
from .conversions import convert_quantity_to_grams, parse_quantity_grams
from .models import (
    ConversionResult,
    IngredientBreakdownItem,
    IngredientData,
    IngredientProvenance,
    NutritionalValues,
    ParsedQuantity,
    RecipeNutrition,
)
from .parsing import eval_fraction, parse_quantity, parse_value_token
from .repository import CIQUAL_NUTRITION_PER_100G, NutritionRepository, get_ingredient_slug

ROOT = Path(__file__).resolve().parents[2]


def enrich_ingredient_database(
    ingredients_path: Path | None = None,
    provenance_path: Path | None = None,
) -> None:
    """Populates ingredients.yaml with CIQUAL nutrition and updates provenance.yaml."""
    if ingredients_path is None:
        ingredients_path = ROOT / ".gram" / "ingredients.yaml"
    if provenance_path is None:
        provenance_path = ROOT / ".gram" / "ingredient-provenance.yaml"

    if not ingredients_path.exists():
        return

    ing_data = yaml.safe_load(ingredients_path.read_text(encoding="utf-8")) or {}
    ingredients = ing_data.get("ingredients", {})

    prov_data: dict = {}
    if provenance_path.exists():
        prov_data = yaml.safe_load(provenance_path.read_text(encoding="utf-8")) or {}
    prov_ingredients = prov_data.setdefault("ingredients", {})

    for slug, values in CIQUAL_NUTRITION_PER_100G.items():
        if slug in ingredients:
            ingredients[slug]["nutrition"] = values
            prov_ingredients[slug] = {
                "status": "verified",
                "locked": False,
                "sources": ["CIQUAL"],
                "note": "Valeurs nutritionnelles pour 100g issues de la table CIQUAL ANSES.",
            }

    ing_header = "# Base locale CookiGram enrichie avec les données nutritionnelles ANSES CIQUAL.\n"
    ingredients_path.write_text(
        ing_header + yaml.safe_dump(ing_data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    prov_header = "# Suivi de la provenance des ingrédients et niveaux de confiance.\n"
    provenance_path.write_text(
        prov_header + yaml.safe_dump(prov_data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


__all__ = [
    "CIQUAL_NUTRITION_PER_100G",
    "ConversionResult",
    "IngredientBreakdownItem",
    "IngredientData",
    "IngredientProvenance",
    "NutritionalValues",
    "NutritionRepository",
    "ParsedQuantity",
    "RecipeNutrition",
    "calculate_recipe_nutrition",
    "convert_quantity_to_grams",
    "enrich_ingredient_database",
    "eval_fraction",
    "get_ingredient_slug",
    "parse_quantity",
    "parse_quantity_grams",
    "parse_value_token",
]
