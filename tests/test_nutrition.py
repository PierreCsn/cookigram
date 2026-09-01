from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe
from generator.nutrition import calculate_recipe_nutrition, parse_quantity_grams


def test_parse_quantity_grams():
    assert parse_quantity_grams("800 g") == 800.0
    assert parse_quantity_grams("1.5 kg") == 1500.0
    assert parse_quantity_grams("250 ml") == 250.0
    assert parse_quantity_grams("2 c. à soupe") == 30.0
    assert parse_quantity_grams("1 c. à café") == 5.0
    assert parse_quantity_grams("2 pincées") == 1.0
    assert parse_quantity_grams("3", "magrets-de-canard") == 1050.0


def test_calculate_recipe_nutrition():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    nutrition = calculate_recipe_nutrition(curry)

    assert nutrition["calories"] > 400
    assert nutrition["protein"] > 20
    assert nutrition["carbs"] > 30
    assert nutrition["fat"] > 10


def test_nutrition_rendered_in_templates():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered_recipe = env.get_template("recipe.html").render(recipe=curry)
    rendered_index = env.get_template("index.html").render(recipes=[curry], all_tags=[])

    assert "nutrition-card" in rendered_recipe
    assert "nutrition-breakdown" in rendered_recipe
    assert "breakdown-item" in rendered_recipe
    assert "nutrition-tag" in rendered_index
    assert f"{curry.nutrition['calories']} kcal" in rendered_recipe
    assert f"{curry.nutrition['calories']} kcal" in rendered_index
