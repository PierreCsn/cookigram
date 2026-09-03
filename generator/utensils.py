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
        "pince de cuisine",
        "pince",
    ],
    "planche": [
        "planche a decouper",
        "planche à découper",
        "planche de decoupe",
        "planche",
    ],
    "plat-gratin": [
        "plat a gratin",
        "plat à gratin",
        "plat a rotir",
        "plat à rôtir",
        "plat de service",
        "plat pour bain-marie",
        "plat profond",
        "bain-marie",
        "plat au four",
    ],
    "thermomix": [
        "thermomix",
        "robot cuiseur",
        "robot multifonction",
        "robot",
        "instant pot",
        "multicuiseur",
        "tm31",
        "tm5",
        "tm6",
        "tm7",
    ],
    "moule": [
        "moule a charniere",
        "moule à charnière",
        "moule a flan",
        "moule à flan",
        "moule a cake",
        "moule a gateau",
        "moule à gâteau",
        "moule",
    ],
    "panier-vapeur": [
        "panier cuisson",
        "panier vapeur",
        "varoma",
        "plateau vapeur",
        "passoire",
        "panier",
    ],
    "econome": [
        "econome",
        "économe",
        "epluche-legumes",
        "épluche-légumes",
        "eplucheur",
        "éplucheur",
        "rasoir a legumes",
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
    padded_norm = f" {norm} "
    tokens = set(norm.split())

    for icon, keywords in UTENSIL_ICON_KEYWORDS.items():
        for kw in keywords:
            kw_norm = normalize_keyword(kw)
            if " " in kw_norm:
                if f" {kw_norm} " in padded_norm:
                    return icon
            else:
                if kw_norm in tokens:
                    return icon
    return None


def attach_utensil_icons(recipe: Any) -> None:
    """Attach structured equipment items with resolved icons to recipe metadata."""
    equipment = recipe.metadata.get("required_equipment")
    if equipment and isinstance(equipment, list):
        recipe.metadata["equipment_items"] = [
            {"name": str(item), "icon": resolve_utensil_icon(str(item))} for item in equipment
        ]
    else:
        recipe.metadata["equipment_items"] = []
