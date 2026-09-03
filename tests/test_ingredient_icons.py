from pathlib import Path
from types import SimpleNamespace

from generator.ingredient_icons import IngredientIconResolver, attach_ingredient_icons
from generator.models import Ingredient


def test_resolver_uses_canonical_aliases_and_existing_assets():
    resolver = IngredientIconResolver()

    assert resolver.resolve("gousses d'ail", "2 gousses") == "icons/ingredients/ail.svg"
    assert resolver.resolve("ail", "1 tête") == "icons/ingredients/ail-tete.svg"
    assert resolver.resolve("huile d'olive", "2 c. à soupe") == "icons/ingredients/huile-olive.svg"


def test_resolver_returns_empty_string_when_icon_is_missing():
    resolver = IngredientIconResolver()

    assert resolver.resolve("aubergine", "1") == ""


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
