from pathlib import Path
from types import SimpleNamespace

from generator.ingredient_icons import IngredientIconResolver, attach_ingredient_icons
from generator.models import Ingredient


def test_resolver_uses_canonical_aliases_and_existing_assets():
    resolver = IngredientIconResolver()

    assert resolver.resolve("gousses d'ail", "2 gousses") == "icons/ingredients/ail.svg"
    assert resolver.resolve("ail", "1 tête") == "icons/ingredients/ail-tete.svg"
    assert resolver.resolve("huile d'olive", "2 c. à soupe") == "icons/ingredients/huile-olive.svg"


def test_resolver_covers_pilot_family_variants():
    resolver = IngredientIconResolver()

    expected = {
        "crème fraîche liquide": "creme-fraiche.svg",
        "filets de poulet": "poulet.svg",
        "paleron de boeuf": "boeuf.svg",
        "riz basmati": "riz.svg",
        "penne": "pates.svg",
        "champignons de Paris": "champignon.svg",
        "concentré de tomate": "concentre-tomate.svg",
        "cube de bouillon de volaille": "bouillon-volaille.svg",
        "moutarde": "moutarde.svg",
        "piment de Cayenne": "piment.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_common_missing_ingredient_icons():
    resolver = IngredientIconResolver()

    expected = {
        "eau": "eau.svg",
        "poivre blanc moulu": "poivre-moulu.svg",
        "vin blanc": "vin-blanc.svg",
        "bouquet garni": "bouquet-garni.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_reuses_icons_for_ingredient_variants():
    resolver = IngredientIconResolver()

    expected = {
        "ail en poudre": "ail.svg",
        "tomates cerises": "tomate.svg",
        "tomates concassées": "tomate.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_first_common_missing_batch():
    resolver = IngredientIconResolver()

    expected = {
        "poivron rouge": "poivron.svg",
        "poireaux": "poireau.svg",
        "feuilles de laurier": "laurier.svg",
        "thym": "thym.svg",
        "basilic frais": "basilic-frais.svg",
        "lait demi-écrémé": "lait.svg",
        "noix de muscade": "noix-de-muscade.svg",
        "bouillon de légumes": "bouillon-de-legumes.svg",
        "œufs": "oeuf.svg",
        "miel": "miel.svg",
        "olives noires": "olives-noires.svg",
        "paprika": "paprika.svg",
        "sauce soja salée": "sauce-soja.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_second_common_missing_batch():
    resolver = IngredientIconResolver()

    expected = {
        "concombre": "concombre.svg",
        "aubergines": "aubergine.svg",
        "courgette": "courgette.svg",
        "chou-fleur": "chou-fleur.svg",
        "petits pois": "petits-pois.svg",
        "crevettes": "crevettes.svg",
        "feta": "feta.svg",
        "cannelle en poudre": "cannelle.svg",
        "cumin": "cumin.svg",
        "curcuma": "curcuma.svg",
        "maïzena": "maizena.svg",
        "lentilles corail": "lentilles-corail.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_fruit_and_vegetable_batch():
    resolver = IngredientIconResolver()

    expected = {
        "banane": "banane.svg",
        "pomme": "pomme.svg",
        "chair de potiron": "potiron.svg",
        "courge butternut": "potiron.svg",
        "asperges vertes": "asperges.svg",
        "panais": "panais.svg",
        "mâche": "mache.svg",
        "salade romaine": "salade-romaine.svg",
        "oignon nouveau": "oignon-nouveau.svg",
        "céleri": "celeri.svg",
    }

    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_protein_batch():
    resolver = IngredientIconResolver()
    expected = {
        "filets d'anchois": "anchois.svg",
        "filets de merlan": "filet-de-poisson.svg",
        "langoustines": "langoustines.svg",
        "viande hachée": "viande-hachee.svg",
        "lardons": "lardons.svg",
        "jambon cru": "jambon-cru.svg",
        "chorizo": "chorizo.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_legume_and_nut_batch():
    resolver = IngredientIconResolver()
    expected = {
        "châtaignes": "chataignes.svg",
        "pois chiches": "pois-chiches.svg",
        "pois gourmands": "pois-gourmands.svg",
        "lentilles vertes": "lentilles-vertes.svg",
        "pistaches": "pistaches.svg",
        "pignons de pin": "pignons-de-pin.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_dry_pantry_batch():
    resolver = IngredientIconResolver()
    expected = {
        "amandes effilées": "amandes-effilees.svg",
        "amandes en poudre": "amandes-en-poudre.svg",
        "chapelure": "chapelure.svg",
        "feuilles de lasagne": "feuilles-de-lasagne.svg",
        "pâte sèche à lasagne": "feuilles-de-lasagne.svg",
        "pain de mie": "pain-de-mie.svg",
        "emmental râpé": "fromage-rape.svg",
        "fromage râpé": "fromage-rape.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_sauce_and_liquid_batch():
    resolver = IngredientIconResolver()
    expected = {
        "sauce tomate": "sauce-tomate.svg",
        "béchamel": "bechamel.svg",
        "caramel liquide": "caramel-liquide.svg",
        "jus de citron vert": "jus-de-citron-vert.svg",
        "vin rouge": "vin-rouge.svg",
        "vinaigre blanc": "vinaigre-blanc.svg",
        "vinaigre de riz": "vinaigre-de-riz.svg",
        "vinaigre de vin": "vinaigre-de-vin.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_herb_and_spice_batch():
    resolver = IngredientIconResolver()
    expected = {
        "aneth": "aneth.svg",
        "cerfeuil frais": "cerfeuil-frais.svg",
        "estragon frais": "estragon-frais.svg",
        "herbes de Provence": "herbes-de-provence.svg",
        "gingembre moulu": "gingembre-moulu.svg",
        "quatre-épices": "quatre-epices.svg",
        "garam masala": "garam-masala.svg",
        "graines de fenouil": "graines-de-fenouil.svg",
        "graines de moutarde": "graines-de-moutarde.svg",
        "graines de sésame blanc": "graines-de-sesame-blanc.svg",
        "épices cajun": "epices-cajun.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_covers_the_final_ingredient_batch():
    resolver = IngredientIconResolver()
    expected = {
        "La Vache qui rit": "produit-laitier.svg",
        "clous de girofle": "clou-de-girofle.svg",
        "coriandre moulue": "coriandre-moulue.svg",
        "croûtons": "croutons.svg",
        "cube de bouillon": "cube-de-bouillon.svg",
        "cube de bouillon de boeuf": "cube-de-bouillon.svg",
        "câpres": "capres.svg",
        "fond de légumes": "fond-de-legumes.svg",
        "fond de viande": "fond-de-viande.svg",
        "fruits secs variés": "fruits-secs.svg",
        "ghee": "ghee.svg",
        "huile de coco": "huile-vegetale.svg",
        "huile végétale": "huile-vegetale.svg",
        "jaunes d'œufs": "oeuf.svg",
        "jus de canneberge": "jus-de-canneberge.svg",
        "lait de soja": "lait.svg",
        "lard": "lardons.svg",
        "mascarpone": "produit-laitier.svg",
        "maïs en boîte": "mais.svg",
        "mozzarella": "produit-laitier.svg",
        "olives vertes dénoyautées": "olives-vertes.svg",
        "origan": "origan.svg",
        "piments verts": "piment-vert.svg",
        "pâte miso": "pate-miso.svg",
        "pâte tikka": "pate-tikka.svg",
        "ricotta": "produit-laitier.svg",
        "sauce worcestershire": "sauce-worcestershire.svg",
        "sauge fraîche": "sauge.svg",
        "sucre roux": "sucre-roux.svg",
        "tahini - crème de sésame": "tahini.svg",
        "tomates séchées": "tomate.svg",
        "whisky": "whisky.svg",
    }
    for name, filename in expected.items():
        assert resolver.resolve(name) == f"icons/ingredients/{filename}"


def test_resolver_returns_empty_string_when_icon_is_missing():
    resolver = IngredientIconResolver()

    assert resolver.resolve("ingrédient totalement inconnu", "1") == ""


def test_attach_icons_covers_recipe_steps_and_shopping():
    ingredient = Ingredient("Ail", "1 tête")
    recipe = SimpleNamespace(
        ingredients=[ingredient],
        steps=[SimpleNamespace(ingredients=[ingredient])],
        variants=[],
        shopping={
            "aisles": {"Fruits & Légumes": [{"slug": "ail", "raw_quantity": "1 tête"}]},
            "staples": [{"slug": "sel", "raw_quantity": "1 pincée"}],
        },
    )

    attach_ingredient_icons(recipe, IngredientIconResolver(Path.cwd()))

    assert ingredient.icon == "icons/ingredients/ail-tete.svg"
    assert recipe.shopping["aisles"]["Fruits & Légumes"][0]["icon"].endswith("ail-tete.svg")
    assert recipe.shopping["staples"][0]["icon"].endswith("sel.svg")
