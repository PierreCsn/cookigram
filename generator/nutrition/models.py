"""Data models for CookiGram nutrition engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NutritionalValues:
    """Nutritional values per 100g of edible portion."""

    calories: float
    protein: float
    carbs: float
    fat: float

    def to_dict(self) -> dict[str, float]:
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
        }


@dataclass
class IngredientProvenance:
    """Provenance and confidence metadata for an ingredient."""

    status: str = "unspecified"  # "verified", "estimated", "manual", "unspecified"
    sources: list[str] = field(default_factory=list)  # ["CIQUAL", "Open Food Facts", etc.]
    note: str = ""
    locked: bool = False


@dataclass
class IngredientData:
    """Complete local database record for an ingredient."""

    slug: str
    name: str
    aliases: list[str] = field(default_factory=list)
    category: str = ""
    pantry_staple: bool = False
    nutrition: NutritionalValues | None = None
    density: float | None = None  # in g/ml (e.g. 0.92 for oil, 1.42 for honey)
    piece_weight: float | None = None  # in grams per piece/unit (e.g. 120.0 for onion)
    conversions: dict[str, float] = field(default_factory=dict)  # unit -> grams
    provenance: IngredientProvenance = field(default_factory=IngredientProvenance)


@dataclass
class ParsedQuantity:
    """Structured representation of a parsed recipe quantity string."""

    value: float | None
    unit: str
    raw: str
    per_piece_value: float | None = None
    per_piece_unit: str = ""
    notes: str = ""
    is_unquantified: bool = False


@dataclass
class ConversionResult:
    """Result of converting a recipe quantity to grams."""

    grams: float | None
    method: str  # "direct_mass", "density_volume", "piece_weight", "spoon_volume", "pinch_weight", "custom_unit", "unquantified_condiment", "non_convertible"
    confidence: str  # "verified", "estimated", "unconvertible", "unquantified"
    reason: str = ""
    density_used: float | None = None
    piece_weight_used: float | None = None


@dataclass
class IngredientBreakdownItem:
    """Caloric and macronutrient breakdown for an individual ingredient in a recipe."""

    name: str
    quantity: str
    slug: str
    grams: float | None
    calories: int  # per portion
    calories_raw: float  # total across whole recipe
    protein: float
    carbs: float
    fat: float
    percentage: float  # percentage of total recipe calories
    source: str
    confidence: str
    conversion_method: str
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "slug": self.slug,
            "grams": round(self.grams, 1) if self.grams is not None else None,
            "calories": self.calories,
            "calories_raw": round(self.calories_raw, 1),
            "percentage": self.percentage,
            "protein": round(self.protein, 1),
            "carbs": round(self.carbs, 1),
            "fat": round(self.fat, 1),
            "source": self.source,
            "confidence": self.confidence,
            "conversion_method": self.conversion_method,
            "warning": self.warning,
        }


class RecipeNutrition(dict):
    """Calculated nutritional profile for a recipe.

    Inherits from dict for transparent Jinja2 template and backwards-compatibility
    with dict-style item access `recipe.nutrition['calories']` and attribute access.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'RecipeNutrition' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value
