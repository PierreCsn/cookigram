"""Kitchen utensils mapping and icon resolution for CookiGram."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

UTENSIL_ICON_KEYWORDS: dict[str, list[str]] = {
    "couteau": [
        "couteau",
        "couteaux",
        "couteau de chef",
        "couteau d'office",
        "couteau eminceur",
        "couteau santoku",
    ],
    "casserole": [
        "casserole",
        "casseroles",
        "faitout",
        "marmite",
        "cocotte",
        "cocotte en fonte",
    ],
    "poele": [
        "poele",
        "poêle",
        "poeles",
        "poêles",
        "sauteuse",
        "wok",
    ],
    "fouet": [
        "fouet",
        "fouets",
        "fouet manuel",
        "fouet de cuisine",
    ],
    "saladier": [
        "saladier",
        "saladiers",
        "bol",
        "bols",
        "bol thermomix",
        "cul-de-poule",
        "cul de poule",
    ],
    "spatule": [
        "spatule",
        "spatules",
        "cuillere en bois",
        "cuillere",
        "cuillère en bois",
        "maryse",
    ],
}


def normalize_keyword(text: str) -> str:
    """Normalize text for fuzzy keyword matching."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s-]", " ", text).strip()


def resolve_utensil_icon(equipment_name: str) -> str | None:
    """Resolves an equipment item name to a standard utensil icon name, or None if fallback needed."""
    if not equipment_name or not isinstance(equipment_name, str):
        return None

    norm = normalize_keyword(equipment_name)
    tokens = norm.split()

    for icon, keywords in UTENSIL_ICON_KEYWORDS.items():
        for kw in keywords:
            kw_norm = normalize_keyword(kw)
            if kw_norm in norm or any(token == kw_norm for token in tokens):
                return icon
    return None


def attach_utensil_icons(recipe: Any) -> None:
    """Attach structured equipment items with resolved icons to recipe metadata."""
    required_equipment = recipe.metadata.get("required_equipment") or []
    step_equipment = getattr(recipe, "equipment", [])

    def structured_items(equipment: Any) -> list[dict[str, str | None]]:
        if not equipment or not isinstance(equipment, list):
            return []
        return [
            {
                "name": str(item.get("name", "")) if isinstance(item, dict) else str(item),
                "icon": (
                    item.get("icon")
                    if isinstance(item, dict) and item.get("icon")
                    else resolve_utensil_icon(str(item.get("name", "")) if isinstance(item, dict) else str(item))
                ),
            }
            for item in equipment
        ]

    recipe.metadata["equipment_items"] = structured_items(required_equipment)
    recipe.metadata["step_equipment_items"] = structured_items(step_equipment)
