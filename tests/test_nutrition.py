from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe
from generator.models import Ingredient
from generator.nutrition import (
    NutritionRepository,
    calculate_recipe_nutrition,
    convert_quantity_to_grams,
    parse_quantity,
    parse_quantity_grams,
)
from generator.seo import build_recipe_meta_description, is_thermomix_compatible


def test_parse_quantity_grams():
    assert parse_quantity_grams("800 g") == 800.0
    assert parse_quantity_grams("1.5 kg") == 1500.0
    assert parse_quantity_grams("250 ml") == 250.0
    assert parse_quantity_grams("25 cl") == 250.0
    assert parse_quantity_grams("0,5 l") == 500.0
    assert parse_quantity_grams("2 c. à soupe") == 30.0
    assert parse_quantity_grams("1 c. à café") == 5.0
    assert parse_quantity_grams("2 pincées") == 1.0
    assert parse_quantity_grams("3", "magrets-de-canard") == 1050.0


def test_parse_quantity_mixed_fractions():
    assert parse_quantity_grams("1 1/2 c. à café") == 7.5
    assert parse_quantity_grams("1/2 c. à café") == 2.5
    assert parse_quantity_grams("1 1/2 c. à soupe") == 22.5
    assert parse_quantity_grams("2 1/4 pincées") == 1.125
    assert parse_quantity_grams("1 c. à café, sur 1 1/2 c. à café au total") == 7.5


def test_parse_quantity_unicode_fractions():
    assert parse_quantity_grams("½ c. à café") == 2.5
    assert parse_quantity_grams("¼ c. à café") == 1.25
    assert parse_quantity_grams("1½ c. à soupe") == 22.5
    assert parse_quantity_grams("¾ c. à soupe") == 11.25


def test_parse_quantity_ranges():
    # Ranges take the average: (3.5 + 4.0) / 2 = 3.75 -> * 5 = 18.75
    assert parse_quantity_grams("3 1/2 à 4 c. à café") == 18.75
    # (1 + 2) / 2 = 1.5 -> * 5g per clove
    assert parse_quantity_grams("1-2 gousses", "ail") == 7.5


def test_density_volume_conversions():
    repo = NutritionRepository()
    olive_oil = repo.get_ingredient("huile-olive")
    honey = repo.get_ingredient("miel")
    water = repo.get_ingredient("eau")

    assert olive_oil is not None and olive_oil.density == 0.92
    assert honey is not None and honey.density == 1.42
    assert water is not None and water.density == 1.0

    # 100 ml of olive oil = 92 g
    res_oil = convert_quantity_to_grams(parse_quantity("100 ml"), olive_oil)
    assert res_oil.grams == 92.0
    assert res_oil.method == "density_volume"
    assert res_oil.confidence == "verified"

    # 100 ml of honey = 142 g
    res_honey = convert_quantity_to_grams(parse_quantity("100 ml"), honey)
    assert res_honey.grams == 142.0
    assert res_honey.confidence == "verified"

    # 100 ml of water = 100 g
    res_water = convert_quantity_to_grams(parse_quantity("100 ml"), water)
    assert res_water.grams == 100.0


def test_piece_weight_and_conversions():
    repo = NutritionRepository()
    egg = repo.get_ingredient("oeuf")
    shallot = repo.get_ingredient("echalote")
    celery = repo.get_ingredient("celeri")

    assert egg is not None and egg.piece_weight == 60.0
    assert shallot is not None and shallot.piece_weight == 25.0

    # 2 eggs = 120 g
    res_egg = convert_quantity_to_grams(parse_quantity("2 pièces"), egg)
    assert res_egg.grams == 120.0
    assert res_egg.method == "piece_weight"

    # 3 shallots = 75 g
    res_shallot = convert_quantity_to_grams(parse_quantity("3"), shallot)
    assert res_shallot.grams == 75.0

    # 1 branche of celery = 40 g (from custom conversions)
    res_celery = convert_quantity_to_grams(parse_quantity("1 branche"), celery)
    assert res_celery.grams == 40.0
    assert res_celery.method == "custom_unit"


def test_suppression_silent_fallback_10g():
    # An unrecognized quantity for an ingredient without known piece weight must NOT return 10g or 100g
    unknown_ing = None
    res = convert_quantity_to_grams(parse_quantity("inconnu"), unknown_ing)
    assert res.grams is None
    assert res.method == "non_convertible"
    assert res.confidence == "unconvertible"

    # parse_quantity_grams returns 0.0, never 10.0
    assert parse_quantity_grams("quantité inconnue") == 0.0


def test_ignored_and_non_convertible_tracking():
    mock_recipe = SimpleNamespace(
        portions=4,
        ingredients=[
            Ingredient(name="huile-olive", quantity="100 ml"),
            Ingredient(name="ingredient-inexistant-xyz", quantity="200 g"),
            Ingredient(name="oeuf", quantity="quantite_invalide_totalement"),
        ],
    )
    nutr = calculate_recipe_nutrition(mock_recipe)

    assert "ingredient-inexistant-xyz" in nutr.ignored_ingredients
    assert len(nutr.non_convertible_ingredients) == 1
    assert nutr.non_convertible_ingredients[0]["name"] == "oeuf"
    assert nutr.is_reliable is False
    assert nutr.confidence == "partial"
    assert "partiel" in nutr.badge_label
    assert nutr.warning is not None


def test_coverage_and_reliability_threshold():
    # 1 valid ingredient out of 2 -> 50% coverage
    mock_recipe = SimpleNamespace(
        portions=2,
        ingredients=[
            Ingredient(name="carotte", quantity="200 g"),
            Ingredient(name="farine_mystere", quantity="100 g"),
        ],
    )
    nutr = calculate_recipe_nutrition(mock_recipe)
    assert nutr.coverage_pct == 50.0
    assert nutr.is_reliable is False
    assert "couverture 50.0%" in nutr.warning


def test_dynamic_badge_and_sources():
    repo = NutritionRepository()
    # A fully verified recipe with only CIQUAL sources
    mock_recipe = SimpleNamespace(
        portions=2,
        ingredients=[
            Ingredient(name="carotte", quantity="200 g"),
            Ingredient(name="eau", quantity="500 ml"),
        ],
    )
    nutr = calculate_recipe_nutrition(mock_recipe, repository=repo)
    assert nutr.coverage_pct == 100.0
    assert nutr.is_reliable is True
    assert "CIQUAL" in nutr.sources


def test_calculate_recipe_nutrition():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    nutrition = calculate_recipe_nutrition(curry)

    assert nutrition["calories"] > 400
    assert nutrition["protein"] > 20
    assert nutrition["carbs"] > 30
    assert nutrition["fat"] > 10
    assert nutrition["coverage_pct"] >= 95.0
    assert nutrition["is_reliable"] is True
    assert len(nutrition["breakdown"]) > 0

    # Every item in breakdown must have calories, grams, and method
    for item in nutrition["breakdown"]:
        assert "calories" in item
        assert "grams" in item
        assert "conversion_method" in item
        assert "percentage" in item


def test_nutrition_rendered_in_templates():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    env.globals["recipe_meta_description"] = build_recipe_meta_description
    env.globals["is_thermomix_compatible"] = is_thermomix_compatible
    rendered_recipe = env.get_template("recipe.html").render(recipe=curry, related_recipes=[])
    rendered_index = env.get_template("index.html").render(recipes=[curry], all_tags=[])

    assert "nutrition-card" in rendered_recipe
    assert "nutrition-breakdown" in rendered_recipe
    assert "breakdown-item" in rendered_recipe
    assert "nutrition-badge" in rendered_recipe
    assert "nutrition-tag" in rendered_index
    assert f"{curry.nutrition['calories']} kcal" in rendered_recipe
    assert f"{curry.nutrition['calories']} kcal" in rendered_index


def test_unreliable_nutrition_template_rendering():
    unreliable_recipe = SimpleNamespace(
        slug="recette-partielle",
        title="Recette Partielle",
        description="Recette avec données incomplètes",
        portions=4,
        steps=[],
        tags=["test"],
        ingredients=[
            Ingredient(name="carotte", quantity="100 g"),
            Ingredient(name="inconnu", quantity="100 g"),
        ],
        prep_time="10 min",
        nutrition=calculate_recipe_nutrition(
            SimpleNamespace(
                portions=4,
                ingredients=[
                    Ingredient(name="carotte", quantity="100 g"),
                    Ingredient(name="inconnu", quantity="100 g"),
                ],
            )
        ),
    )

    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered_index = env.get_template("index.html").render(recipes=[unreliable_recipe], all_tags=[])
    # Unreliable calories should NOT be rendered in the index tag
    assert "nutrition-tag" not in rendered_index
