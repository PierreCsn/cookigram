from pathlib import Path

from generator.gram import parse_recipe


def test_theme_toggle_is_present_on_all_pages(render_template):
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    index_html = render_template("index.html", recipes=[recipe], all_tags=[])
    recipe_html = render_template("recipe.html", recipe=recipe)
    cook_html = render_template("cook.html", recipe=recipe)

    assert "theme-toggle" in index_html
    assert "theme-toggle" in recipe_html
    assert "theme-toggle" in cook_html
    assert "cookigram:theme" in index_html
