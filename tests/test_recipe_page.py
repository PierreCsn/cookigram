from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_recipe_page_contains_share_button():
    recipe = parse_recipe(Path("recipes/magret-rose.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "share-btn" in rendered
    assert "recipe-actions" in rendered
    assert "Partager" in rendered
