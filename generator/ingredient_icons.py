"""Resolve optional ingredient icons without ever breaking text rendering."""

import re
from pathlib import Path
from typing import Any

import yaml

from .nutrition import get_ingredient_slug

ROOT = Path(__file__).resolve().parents[1]

# Several Gram entries describe a preparation or a cut of the same ingredient.
# Keep one visual vocabulary for those families instead of duplicating SVGs.
ICON_FAMILY_BY_SLUG = {
    "creme-fraiche-epaisse": "creme-fraiche",
    "creme-fraiche-liquide": "creme-fraiche",
    "parmesan": "parmesan",
    "saumon-frais": "saumon",
    "saumon-fume": "saumon",
    "poulet": "poulet",
    "filet-de-poulet": "poulet",
    "cuisse-de-poulet": "poulet",
    "paleron-de-boeuf": "boeuf",
    "faux-filet": "boeuf",
    "souris-d-agneau": "plat-de-cote-de-boeuf",
    "porc-hache": "porc",
    "filet-mignon-de-porc": "porc",
    "echine-de-porc": "porc",
    "roti-de-porc": "porc",
    "riz-a-risotto": "riz",
    "riz-basmati": "riz",
    "riz-long-blanc": "riz",
    "farfalle": "pates",
    "penne": "pates",
    "torsades": "pates",
    "nouilles-chinoises": "pates",
    "champignons-de-paris": "champignon",
    "concentre-de-tomate": "concentre-tomate",
    "cube-de-bouillon-de-volaille": "bouillon-volaille",
    "moutarde-de-dijon": "moutarde",
    "persil-frais": "persil",
    "coriandre-fraiche": "coriandre",
    "piment-rouge": "piment",
    "piment-de-cayenne": "piment",
    "curry-en-poudre": "curry",
    "ail-en-poudre": "ail",
    "tomate-cerise": "tomate",
    "tomates-concassees": "tomate",
    "poivron": "poivron",
    "poireau": "poireau",
    "laurier": "laurier",
    "thym": "thym",
    "basilic-frais": "basilic-frais",
    "lait": "lait",
    "lait-demi-ecreme": "lait",
    "noix-de-muscade": "noix-de-muscade",
    "bouillon-de-legumes": "bouillon-de-legumes",
    "oeuf": "oeuf",
    "miel": "miel",
    "olives-noires": "olives-noires",
    "paprika": "paprika",
    "sauce-soja": "sauce-soja",
    "concombre": "concombre",
    "aubergine": "aubergine",
    "courgette": "courgette",
    "chou-fleur": "chou-fleur",
    "petits-pois": "petits-pois",
    "crevettes": "crevettes",
    "feta": "feta",
    "cannelle": "cannelle",
    "cumin": "cumin",
    "curcuma": "curcuma",
    "maizena": "maizena",
    "lentilles-corail": "lentilles-corail",
    "banane": "banane",
    "pomme": "pomme",
    "potiron": "potiron",
    "courge-butternut": "potiron",
    "asperges": "asperges",
    "panais": "panais",
    "mache": "mache",
    "salade-romaine": "salade-romaine",
    "oignon-nouveau": "oignon-nouveau",
    "celeri": "celeri",
    "anchois": "anchois",
    "filet-de-poisson": "filet-de-poisson",
    "langoustines": "langoustines",
    "viande-hachee": "viande-hachee",
    "lardons": "lardons",
    "jambon-cru": "jambon-cru",
    "chorizo": "chorizo",
    "chataignes": "chataignes",
    "pois-chiches": "pois-chiches",
    "pois-gourmands": "pois-gourmands",
    "lentilles-vertes": "lentilles-vertes",
    "pistaches": "pistaches",
    "pignons-de-pin": "pignons-de-pin",
    "amandes-effilees": "amandes-effilees",
    "amande-en-poudre": "amandes-en-poudre",
    "chapelure": "chapelure",
    "feuilles-de-lasagne": "feuilles-de-lasagne",
    "pate-seche-a-lasagne": "feuilles-de-lasagne",
    "pain-de-mie": "pain-de-mie",
    "emmental-rape": "fromage-rape",
    "fromage-rape": "fromage-rape",
    "sauce-tomate": "sauce-tomate",
    "bechamel": "bechamel",
    "caramel-liquide": "caramel-liquide",
    "jus-de-citron-vert": "jus-de-citron-vert",
    "vin-rouge": "vin-rouge",
    "vinaigre-blanc": "vinaigre-blanc",
    "vinaigre-de-riz": "vinaigre-de-riz",
    "vinaigre-de-vin": "vinaigre-de-vin",
    "aneth": "aneth",
    "cerfeuil": "cerfeuil-frais",
    "estragon": "estragon-frais",
    "herbes-de-provence": "herbes-de-provence",
    "gingembre-moulu": "gingembre-moulu",
    "quatre-epices": "quatre-epices",
    "garam-masala": "garam-masala",
    "graine-de-fenouil": "graines-de-fenouil",
    "graine-de-moutarde": "graines-de-moutarde",
    "graine-de-sesame": "graines-de-sesame-blanc",
    "epices-cajun": "epices-cajun",
    "la-vache-qui-rit": "produit-laitier",
    "clou-de-girofle": "clou-de-girofle",
    "coriandre-moulue": "coriandre-moulue",
    "croutons": "croutons",
    "cube-de-bouillon": "cube-de-bouillon",
    "cube-de-bouillon-de-boeuf": "cube-de-bouillon",
    "cube-de-bouillon-de-legumes": "cube-de-bouillon",
    "capres": "capres",
    "fond-de-legumes": "fond-de-legumes",
    "fond-de-viande": "fond-de-viande",
    "fruits-secs": "fruits-secs",
    "ghee": "ghee",
    "huile-de-coco": "huile-vegetale",
    "huile-de-pepins-de-raisin": "huile-vegetale",
    "huile-de-sesame": "huile-vegetale",
    "huile-vegetale": "huile-vegetale",
    "jaune-d-oeuf": "oeuf",
    "jus-de-canneberge": "jus-de-canneberge",
    "jus-de-cuisson-sous-vide": "jus-de-cuisson-sous-vide",
    "lait-de-soja": "lait",
    "lard": "lardons",
    "mascarpone": "produit-laitier",
    "mais": "mais",
    "mozzarella": "produit-laitier",
    "olives-vertes": "olives-vertes",
    "origan": "origan",
    "piment-vert": "piment-vert",
    "pate-miso": "pate-miso",
    "pate-tikka": "pate-tikka",
    "ricotta": "produit-laitier",
    "sauce-worcestershire": "sauce-worcestershire",
    "sauge": "sauge",
    "sucre-roux": "sucre-roux",
    "tahini": "tahini",
    "tomates-sechees": "tomate",
    "whisky": "whisky",
    "levure-boulangere": "levure-chimique",
    "romarin": "herbes-de-provence",
    "gousse-de-vanille": "extrait-de-vanille",
    "kirsch": "whisky",
    "cacao-en-poudre": "chocolat-noir",
    "copeaux-de-chocolat": "chocolat-noir",
    "chocolat-noir": "chocolat-noir",
    "cerise": "cerise",
    "poivre-vert": "poivre",
    "cognac": "whisky",
    "cepes": "champignon",
    "harissa": "piment",
    "pain-d-epices": "pain-de-mie",
    "biere-brune": "whisky",
    "jarret-de-veau": "boeuf",
    "orange": "jus-d-orange",
    "vin-de-shaoxing": "whisky",
    "saucisse-fumee": "lardons",
    "bouillon-de-volaille": "bouillon-volaille",
}

CATEGORY_FALLBACK_ICONS = {
    "boissons": "eau",
    "boissons et alcools": "whisky",
    "boissons et condiments": "whisky",
    "boissons et liquides": "eau",
    "boucherie et charcuterie": "boeuf",
    "boucherie et volaille": "boeuf",
    "boucherie et volailles": "boeuf",
    "boulangerie": "pain-de-mie",
    "charcuterie": "lardons",
    "charcuterie et traiteur": "lardons",
    "condiments": "epices-cajun",
    "condiments et aides culinaires": "bouillon-volaille",
    "condiments et assaisonnements": "epices-cajun",
    "conserves et bocaux": "concentre-tomate",
    "crèmerie et oeufs": "produit-laitier",
    "céréales et féculents": "riz",
    "fromages": "fromage-rape",
    "fruits": "pomme",
    "fruits et légumes": "pomme",
    "fruits secs": "fruits-secs",
    "fruits à coque et graines": "fruits-secs",
    "fruits, légumes, légumineuses et oléagineux": "pomme",
    "féculents et céréales": "riz",
    "herbes et épices": "herbes-de-provence",
    "lait et produits laitiers": "produit-laitier",
    "légumes et aromates": "oignon",
    "matières grasses": "huile-vegetale",
    "poissons et fruits de mer": "filet-de-poisson",
    "poissons, viandes, œufs": "filet-de-poisson",
    "produits céréaliers": "pain-de-mie",
    "produits laitiers": "produit-laitier",
    "produits laitiers et matières grasses": "produit-laitier",
    "produits laitiers et substituts": "produit-laitier",
    "produits sucrés": "sucre",
    "pâtes et préparations": "pates",
    "viandes": "boeuf",
    "viandes et volailles": "boeuf",
    "épicerie": "farine",
    "épicerie salée": "farine",
    "épicerie sucrée": "sucre",
}


class IngredientIconResolver:
    """Map ingredient names to existing icon assets using the Gram database."""

    def __init__(self, root: Path = ROOT) -> None:
        database_path = root / ".gram" / "ingredients.yaml"
        payload = yaml.safe_load(database_path.read_text(encoding="utf-8")) or {}
        self.database = payload.get("ingredients", {})
        self.icons_dir = root / "static" / "icons" / "ingredients"

    def resolve(self, name: str, quantity: str = "") -> str:
        slug = get_ingredient_slug(name, self.database)
        icon_slug = self._variant_slug(slug, quantity)
        filename = f"{icon_slug}.svg"
        if (self.icons_dir / filename).is_file():
            return f"icons/ingredients/{filename}"

        # Category-based fallback if specific icon does not exist
        entry = self.database.get(slug, {})
        category = entry.get("category", "").strip().casefold()
        fallback_slug = CATEGORY_FALLBACK_ICONS.get(category)
        if fallback_slug:
            fallback_filename = f"{fallback_slug}.svg"
            if (self.icons_dir / fallback_filename).is_file():
                return f"icons/ingredients/{fallback_filename}"

        return ""

    @staticmethod
    def _variant_slug(slug: str, quantity: str) -> str:
        if slug == "ail" and re.search(r"\b(?:tête|têtes)\b", quantity, flags=re.IGNORECASE):
            return "ail-tete"
        return ICON_FAMILY_BY_SLUG.get(slug, slug)


def attach_ingredient_icons(recipe: Any, resolver: IngredientIconResolver) -> None:
    """Attach icon paths to recipe views and their shopping projections."""
    views = [recipe, *recipe.variants]
    for view in views:
        for ingredient in view.ingredients:
            ingredient.icon = resolver.resolve(ingredient.name, ingredient.quantity)
        for step in view.steps:
            for ingredient in step.ingredients:
                ingredient.icon = resolver.resolve(ingredient.name, ingredient.quantity)
        for group in view.shopping.get("aisles", {}).values():
            for item in group:
                item["icon"] = resolver.resolve(item["slug"], item.get("raw_quantity", ""))
        for item in view.shopping.get("staples", []):
            item["icon"] = resolver.resolve(item["slug"], item.get("raw_quantity", ""))
