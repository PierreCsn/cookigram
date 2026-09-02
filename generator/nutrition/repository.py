"""Repository managing ingredient nutritional reference data, density, piece weights, and provenance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import IngredientData, IngredientProvenance, NutritionalValues

ROOT = Path(__file__).resolve().parents[2]

# Standard CIQUAL fallback reference values per 100g
CIQUAL_NUTRITION_PER_100G: dict[str, dict[str, float]] = {
    "ail": {"calories": 131, "protein": 6.4, "carbs": 23.5, "fat": 0.5},
    "ail-en-poudre": {"calories": 331, "protein": 16.5, "carbs": 64.0, "fat": 0.7},
    "amande-en-poudre": {"calories": 634, "protein": 21.9, "carbs": 5.4, "fat": 55.8},
    "aneth": {"calories": 43, "protein": 3.5, "carbs": 7.0, "fat": 1.1},
    "aubergine": {"calories": 21, "protein": 0.9, "carbs": 2.5, "fat": 0.2},
    "basilic-frais": {"calories": 23, "protein": 3.2, "carbs": 2.7, "fat": 0.6},
    "bechamel": {"calories": 135, "protein": 3.5, "carbs": 9.5, "fat": 9.0},
    "beurre": {"calories": 751, "protein": 0.8, "carbs": 0.7, "fat": 82.5},
    "bouillon-de-legumes": {"calories": 15, "protein": 0.5, "carbs": 2.5, "fat": 0.3},
    "bouquet-garni": {"calories": 10, "protein": 0.5, "carbs": 1.5, "fat": 0.2},
    "brocoli": {"calories": 35, "protein": 3.1, "carbs": 2.4, "fat": 0.6},
    "cannelle": {"calories": 261, "protein": 4.0, "carbs": 56.1, "fat": 1.2},
    "capres": {"calories": 23, "protein": 2.4, "carbs": 4.9, "fat": 0.9},
    "caramel-liquide": {"calories": 310, "protein": 0.0, "carbs": 77.0, "fat": 0.1},
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
    "cube-de-bouillon": {"calories": 240, "protein": 12.0, "carbs": 20.0, "fat": 12.0},
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
    "fromage-rape": {"calories": 380, "protein": 26.0, "carbs": 1.0, "fat": 30.0},
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
    "pistaches": {"calories": 600, "protein": 18.0, "carbs": 12.0, "fat": 53.0},
    "poireau": {"calories": 31, "protein": 1.5, "carbs": 4.0, "fat": 0.3},
    "poivre-moulu": {"calories": 283, "protein": 10.4, "carbs": 38.3, "fat": 3.3},
    "poivron": {"calories": 28, "protein": 1.1, "carbs": 4.9, "fat": 0.3},
    "pomme": {"calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2},
    "pomme-de-terre": {"calories": 80, "protein": 2.0, "carbs": 17.0, "fat": 0.1},
    "porc-hache": {"calories": 263, "protein": 17.0, "carbs": 0.0, "fat": 21.5},
    "poulet": {"calories": 121, "protein": 21.0, "carbs": 0.0, "fat": 3.8},
    "quatre-epices": {"calories": 260, "protein": 6.0, "carbs": 45.0, "fat": 5.0},
    "riz-a-risotto": {"calories": 355, "protein": 7.5, "carbs": 78.0, "fat": 0.8},
    "riz-basmati": {"calories": 355, "protein": 8.5, "carbs": 77.0, "fat": 0.9},
    "riz-long-blanc": {"calories": 355, "protein": 7.0, "carbs": 79.0, "fat": 0.6},
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
    "tomate": {"calories": 19, "protein": 0.8, "carbs": 2.5, "fat": 0.3},
    "tomate-cerise": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "tomates-concassees": {"calories": 25, "protein": 1.2, "carbs": 3.8, "fat": 0.2},
    "torsades": {"calories": 355, "protein": 12.5, "carbs": 72.0, "fat": 1.5},
    "vin-blanc": {"calories": 82, "protein": 0.1, "carbs": 1.5, "fat": 0.0},
    "vinaigre-blanc": {"calories": 18, "protein": 0.0, "carbs": 0.5, "fat": 0.0},
    "vinaigre-de-riz": {"calories": 18, "protein": 0.1, "carbs": 4.0, "fat": 0.0},
}


class NutritionRepository:
    """Loads and queries ingredient data, nutritional values, and provenance."""

    def __init__(self, db_path: Path | None = None, provenance_path: Path | None = None):
        self.db_path = db_path or (ROOT / ".gram" / "ingredients.yaml")
        self.provenance_path = provenance_path or (ROOT / ".gram" / "ingredient-provenance.yaml")
        self._ingredients: dict[str, IngredientData] = {}
        self._alias_map: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        ingredients_data: dict[str, Any] = {}
        if self.db_path.exists():
            payload = yaml.safe_load(self.db_path.read_text(encoding="utf-8")) or {}
            ingredients_data = payload.get("ingredients", {})

        provenance_data: dict[str, Any] = {}
        if self.provenance_path.exists():
            payload = yaml.safe_load(self.provenance_path.read_text(encoding="utf-8")) or {}
            provenance_data = payload.get("ingredients", {})

        for slug, raw in ingredients_data.items():
            name = str(raw.get("name", slug))
            aliases = [str(a) for a in raw.get("aliases", [])]
            category = str(raw.get("category", ""))
            pantry_staple = bool(raw.get("pantry_staple", False))
            density = float(raw["density"]) if "density" in raw else None
            piece_weight = float(raw["piece_weight"]) if "piece_weight" in raw else None
            conversions = {str(k): float(v) for k, v in raw.get("conversions", {}).items()}

            nutr = None
            if "nutrition" in raw and isinstance(raw["nutrition"], dict):
                n_dict = raw["nutrition"]
                nutr = NutritionalValues(
                    calories=float(n_dict.get("calories", 0.0)),
                    protein=float(n_dict.get("protein", 0.0)),
                    carbs=float(n_dict.get("carbs", 0.0)),
                    fat=float(n_dict.get("fat", 0.0)),
                )
            elif slug in CIQUAL_NUTRITION_PER_100G:
                n_dict = CIQUAL_NUTRITION_PER_100G[slug]
                nutr = NutritionalValues(
                    calories=float(n_dict.get("calories", 0.0)),
                    protein=float(n_dict.get("protein", 0.0)),
                    carbs=float(n_dict.get("carbs", 0.0)),
                    fat=float(n_dict.get("fat", 0.0)),
                )

            # Provenance
            prov_raw = provenance_data.get(slug, {})
            sources = []
            if "sources" in prov_raw:
                sources = [str(s).upper() if str(s).lower() == "ciqual" else str(s) for s in prov_raw["sources"]]
            elif "source" in prov_raw:
                s = str(prov_raw["source"])
                sources = ["CIQUAL" if "ciqual" in s.lower() else s]
            elif nutr is not None:
                sources = ["CIQUAL"]

            prov = IngredientProvenance(
                status=str(prov_raw.get("status", "verified" if nutr else "unspecified")),
                sources=sources,
                note=str(prov_raw.get("note", "")),
                locked=bool(prov_raw.get("locked", False)),
            )

            item = IngredientData(
                slug=slug,
                name=name,
                aliases=aliases,
                category=category,
                pantry_staple=pantry_staple,
                nutrition=nutr,
                density=density,
                piece_weight=piece_weight,
                conversions=conversions,
                provenance=prov,
            )
            self._ingredients[slug] = item

            # Index aliases
            self._alias_map[slug.casefold().strip()] = slug
            self._alias_map[name.casefold().strip()] = slug
            for alias in aliases:
                self._alias_map[alias.casefold().strip()] = slug

    def get_ingredient_slug(self, ingredient_name: str) -> str:
        """Finds matching slug in database by checking slug, name and aliases."""
        clean = ingredient_name.casefold().strip()
        if clean in self._alias_map:
            return self._alias_map[clean]
        with_spaces = clean.replace("-", " ")
        if with_spaces in self._alias_map:
            return self._alias_map[with_spaces]
        with_hyphens = clean.replace(" ", "-")
        if with_hyphens in self._alias_map:
            return self._alias_map[with_hyphens]

        # Singular/plural variants
        for cand in (clean, with_spaces, with_hyphens):
            if cand.endswith("s") and cand[:-1] in self._alias_map:
                return self._alias_map[cand[:-1]]

        # Fallback slug generation
        return re.sub(r"[^\w]+", "-", clean).strip("-")

    def get_ingredient(self, ingredient_name_or_slug: str) -> IngredientData | None:
        """Looks up ingredient by name, alias, or slug."""
        if ingredient_name_or_slug in self._ingredients:
            return self._ingredients[ingredient_name_or_slug]
        slug = self.get_ingredient_slug(ingredient_name_or_slug)
        if slug in self._ingredients:
            return self._ingredients[slug]
        return None


def get_ingredient_slug(ingredient_name: str, database: dict | None = None) -> str:
    """Finds matching slug in database by checking slug, name and aliases.

    Compatible with legacy dictionary signature or uses default repository.
    """
    clean = ingredient_name.casefold().strip()
    if database is not None:
        for slug, data in database.items():
            if slug == clean or data.get("name", "").casefold() == clean:
                return slug
            for alias in data.get("aliases", []):
                if alias.casefold() == clean:
                    return slug
        return re.sub(r"[^\w]+", "-", clean).strip("-")

    repo = NutritionRepository()
    return repo.get_ingredient_slug(ingredient_name)
