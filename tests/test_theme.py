from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_theme_toggle_is_present_on_all_pages():
    recipe = parse_recipe(Path("recipes/magret-rose.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )

    index_html = env.get_template("index.html").render(recipes=[recipe])
    recipe_html = env.get_template("recipe.html").render(recipe=recipe)
    cook_html = env.get_template("cook.html").render(recipe=recipe)

    assert "theme-toggle" in index_html
    assert "theme-toggle" in recipe_html
    assert "theme-toggle" in cook_html
    assert "cookigram:theme" in index_html
