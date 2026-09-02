"""Nutrition calculation engine computing per-portion values, coverage, and provenance."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .conversions import convert_quantity_to_grams
from .models import IngredientBreakdownItem, RecipeNutrition
from .parsing import parse_quantity
from .repository import NutritionRepository

if TYPE_CHECKING:
    from ..models import Recipe


def calculate_recipe_nutrition(
    recipe: Recipe | Any,
    db_path: Path | None = None,
    provenance_path: Path | None = None,
    repository: NutritionRepository | None = None,
) -> RecipeNutrition:
    """Calculates nutrition per portion for a recipe with explicit coverage and confidence tracking."""
    if repository is None:
        repository = NutritionRepository(db_path=db_path, provenance_path=provenance_path)

    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    breakdown_items: list[IngredientBreakdownItem] = []
    ignored_ingredients: list[str] = []
    non_convertible_ingredients: list[dict[str, Any]] = []
    sources_set: set[str] = set()
    any_estimated: bool = False

    raw_ingredients = getattr(recipe, "ingredients", [])
    total_count = len(raw_ingredients)
    analyzed_count = 0
    unquantified_condiment_count = 0

    for item in raw_ingredients:
        ing_data = repository.get_ingredient(item.name)
        if not ing_data or not ing_data.nutrition:
            ignored_ingredients.append(item.name)
            continue

        parsed = parse_quantity(item.quantity)
        conv = convert_quantity_to_grams(parsed, ing_data)

        if conv.grams is None:
            non_convertible_ingredients.append(
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "reason": conv.reason,
                }
            )
            continue

        if conv.method == "unquantified_condiment":
            unquantified_condiment_count += 1
            analyzed_count += 1
            continue

        # Valid quantifiable ingredient with nutrition
        analyzed_count += 1
        factor = conv.grams / 100.0
        cals_raw = ing_data.nutrition.calories * factor
        prot_raw = ing_data.nutrition.protein * factor
        carbs_raw = ing_data.nutrition.carbs * factor
        fat_raw = ing_data.nutrition.fat * factor

        total_calories += cals_raw
        total_protein += prot_raw
        total_carbs += carbs_raw
        total_fat += fat_raw

        # Track sources and confidence
        item_sources = ing_data.provenance.sources or ["CIQUAL"]
        for s in item_sources:
            sources_set.add(s)

        is_item_estimated = conv.confidence == "estimated" or ing_data.provenance.status == "estimated"
        if is_item_estimated:
            any_estimated = True

        breakdown_items.append(
            IngredientBreakdownItem(
                name=item.name,
                quantity=item.quantity,
                slug=ing_data.slug,
                grams=conv.grams,
                calories=0,  # calculated per portion below
                calories_raw=cals_raw,
                protein=prot_raw,
                carbs=carbs_raw,
                fat=fat_raw,
                percentage=0.0,
                source=", ".join(item_sources),
                confidence="estimated" if is_item_estimated else "verified",
                conversion_method=conv.method,
                warning=conv.reason if is_item_estimated and "Densité" in conv.reason else None,
            )
        )

    portions = max(1, getattr(recipe, "portions", 1))

    # Coverage rate: (analyzed items) / (total items)
    coverage_pct = 100.0
    if total_count > 0:
        coverage_pct = round((analyzed_count / total_count) * 100.0, 1)

    # Reliability threshold: at least 80% coverage and no critical unconvertible items
    is_reliable = coverage_pct >= 80.0 and len(non_convertible_ingredients) == 0

    warning = None
    if not is_reliable:
        missing_parts = []
        if ignored_ingredients:
            missing_parts.append(f"{len(ignored_ingredients)} non référencé(s)")
        if non_convertible_ingredients:
            missing_parts.append(f"{len(non_convertible_ingredients)} quantité(s) non convertible(s)")
        details = f" ({', '.join(missing_parts)})" if missing_parts else ""
        warning = f"Données nutritionnelles partielles (couverture {coverage_pct}%){details}."
    elif any_estimated:
        warning = "Certaines valeurs sont calculées à partir d'estimations de densités ou de poids unitaires."

    # Sources list
    sorted_sources = sorted(sources_set) if sources_set else ["CIQUAL"]

    # Global confidence
    if not is_reliable:
        confidence = "partial"
    elif any_estimated:
        confidence = "estimated"
    else:
        confidence = "verified"

    # Dynamic badge label
    if not is_reliable:
        badge_label = f"par portion (partiel {int(coverage_pct)}%)"
    elif confidence == "verified":
        source_str = " & ".join(sorted_sources)
        badge_label = f"par portion ({source_str})"
    else:
        badge_label = "par portion (estimé)"

    # Format breakdown items with per-portion calories and percentages
    formatted_breakdown: list[dict[str, Any]] = []
    for bi in sorted(breakdown_items, key=lambda x: x.calories_raw, reverse=True):
        cals_per_portion = round(bi.calories_raw / portions)
        pct = round((bi.calories_raw / total_calories * 100.0), 1) if total_calories > 0 else 0.0
        bi.calories = cals_per_portion
        bi.percentage = pct
        formatted_breakdown.append(bi.to_dict())

    return RecipeNutrition(
        calories=round(total_calories / portions),
        protein=round(total_protein / portions, 1),
        carbs=round(total_carbs / portions, 1),
        fat=round(total_fat / portions, 1),
        breakdown=formatted_breakdown,
        coverage_pct=coverage_pct,
        total_ingredients=total_count,
        analyzed_ingredients=analyzed_count,
        ignored_ingredients=ignored_ingredients,
        non_convertible_ingredients=non_convertible_ingredients,
        sources=sorted_sources,
        confidence=confidence,
        is_reliable=is_reliable,
        badge_label=badge_label,
        warning=warning,
    )
