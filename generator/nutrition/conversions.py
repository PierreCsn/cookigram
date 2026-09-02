"""Conversion engine translating recipe quantities into grams using density and piece weights."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ConversionResult, IngredientData, ParsedQuantity
from .parsing import parse_quantity

if TYPE_CHECKING:
    from .repository import NutritionRepository

# Default densities in g/ml when not specified in database
DEFAULT_DENSITIES: dict[str, float] = {
    "water": 1.0,
    "oil": 0.92,
    "milk": 1.03,
    "cream": 1.01,
    "honey": 1.42,
    "syrup": 1.35,
    "vinegar": 1.01,
    "wine": 0.99,
}


def convert_quantity_to_grams(
    parsed: ParsedQuantity,
    ingredient: IngredientData | None = None,
) -> ConversionResult:
    """Converts a ParsedQuantity into grams with full traceability and no silent arbitrary fallback."""
    if parsed.is_unquantified:
        return ConversionResult(
            grams=0.0,
            method="unquantified_condiment",
            confidence="unquantified",
            reason="Assaisonnement non quantifié (0 g)",
        )

    if parsed.value is None or parsed.value < 0:
        return ConversionResult(
            grams=None,
            method="non_convertible",
            confidence="unconvertible",
            reason=f"Quantité non reconnue : '{parsed.raw}'",
        )

    val = parsed.value

    # 1. Direct mass
    if parsed.unit == "kg":
        return ConversionResult(
            grams=val * 1000.0,
            method="direct_mass",
            confidence="verified",
            reason="Conversion directe kg -> g",
        )
    if parsed.unit == "g":
        return ConversionResult(
            grams=val,
            method="direct_mass",
            confidence="verified",
            reason="Masse directe en grammes",
        )

    # 2. Volume (ml, cl, dl, l) with ingredient density
    volume_factors = {"ml": 1.0, "cl": 10.0, "dl": 100.0, "l": 1000.0}
    if parsed.unit in volume_factors:
        volume_ml = val * volume_factors[parsed.unit]
        density = 1.0
        method = "density_volume_default"
        confidence = "estimated"
        reason = "Volume converti avec densité par défaut de l'eau (1.0 g/ml)"

        if ingredient and ingredient.density is not None:
            density = ingredient.density
            method = "density_volume"
            confidence = "verified"
            reason = f"Volume converti avec densité spécifique ({density} g/ml)"

        grams = volume_ml * density
        return ConversionResult(
            grams=grams,
            method=method,
            confidence=confidence,
            reason=reason,
            density_used=density,
        )

    # 3. Spoons (tablespoon = 15 ml, teaspoon = 5 ml)
    if parsed.unit in {"c. à soupe", "c. à café"}:
        ml_per_spoon = 15.0 if parsed.unit == "c. à soupe" else 5.0
        volume_ml = val * ml_per_spoon
        density = ingredient.density if (ingredient and ingredient.density is not None) else 1.0
        grams = volume_ml * density
        return ConversionResult(
            grams=grams,
            method="spoon_volume",
            confidence="estimated",
            reason=f"Volume de cuillère ({parsed.unit} = {ml_per_spoon} ml, d={density})",
            density_used=density,
        )

    # 4. Pinches (~0.5 g)
    if parsed.unit == "pincée":
        return ConversionResult(
            grams=val * 0.5,
            method="pinch_weight",
            confidence="estimated",
            reason="Pincée estimée à 0.5 g",
        )

    # 5. Explicit piece annotation: "4 pièces, env. 100 g chacun"
    if parsed.per_piece_value is not None:
        piece_val = parsed.per_piece_value
        factor = 1000.0 if parsed.per_piece_unit == "kg" else 1.0
        grams = val * piece_val * factor
        return ConversionResult(
            grams=grams,
            method="piece_annotation",
            confidence="verified",
            reason=f"Poids unitaire explicite ({piece_val} {parsed.per_piece_unit} par pièce)",
            piece_weight_used=piece_val * factor,
        )

    # 6. Specific unit conversions from ingredient profile
    if ingredient and parsed.unit in ingredient.conversions:
        unit_weight = ingredient.conversions[parsed.unit]
        return ConversionResult(
            grams=val * unit_weight,
            method="custom_unit",
            confidence="estimated",
            reason=f"Conversion spécifique d'ingrédient ({parsed.unit} = {unit_weight} g)",
            piece_weight_used=unit_weight,
        )

    # Standard clove conversion if not in conversions
    if parsed.unit == "gousse":
        clove_weight = 5.0
        if ingredient and "gousse" in ingredient.conversions:
            clove_weight = ingredient.conversions["gousse"]
        elif ingredient and ingredient.piece_weight:
            clove_weight = ingredient.piece_weight
        return ConversionResult(
            grams=val * clove_weight,
            method="custom_unit",
            confidence="estimated",
            reason=f"Gousse estimée à {clove_weight} g",
            piece_weight_used=clove_weight,
        )

    # 7. Piece count / bare number with database piece_weight
    if parsed.unit == "pièce":
        if ingredient and ingredient.piece_weight is not None:
            pw = ingredient.piece_weight
            return ConversionResult(
                grams=val * pw,
                method="piece_weight",
                confidence="estimated",
                reason=f"Poids unitaire moyen de la base ({pw} g/pièce)",
                piece_weight_used=pw,
            )
        # NO silent 100g or 10g fallback!
        ing_label = ingredient.name if ingredient else "ingrédient inconnu"
        return ConversionResult(
            grams=None,
            method="non_convertible",
            confidence="unconvertible",
            reason=f"Poids unitaire non référencé pour '{ing_label}' ({val} {parsed.unit})",
        )

    # 8. Unhandled unit: no silent fallback
    ing_label = ingredient.name if ingredient else "ingrédient inconnu"
    return ConversionResult(
        grams=None,
        method="non_convertible",
        confidence="unconvertible",
        reason=f"Unité '{parsed.unit}' non convertible pour '{ing_label}'",
    )


def parse_quantity_grams(
    quantity_str: str,
    ingredient_slug: str = "",
    repository: NutritionRepository | None = None,
) -> float:
    """Estimates the weight in grams from a CookGram quantity string.

    Maintains backwards compatibility while removing silent arbitrary fallback.
    """
    if not quantity_str:
        return 0.0

    parsed = parse_quantity(quantity_str)
    ingredient = None
    if ingredient_slug:
        if repository is None:
            from .repository import NutritionRepository

            repository = NutritionRepository()
        ingredient = repository.get_ingredient(ingredient_slug)

    res = convert_quantity_to_grams(parsed, ingredient)
    return float(res.grams) if res.grams is not None else 0.0
