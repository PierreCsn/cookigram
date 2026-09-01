from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_index_page_contains_search_and_filter_elements():
    recipe1 = parse_recipe(Path("recipes/risotto-poulet-champignons.gram"))
    recipe2 = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    recipes = [recipe1, recipe2]
    all_tags = sorted({t for r in recipes for t in r.tags})

    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("index.html").render(recipes=recipes, all_tags=all_tags)

    assert 'id="recipe-search"' in rendered
    assert "search-clear" in rendered
    assert "filter-chips" in rendered
    assert 'data-tag="all"' in rendered
    assert "empty-search" in rendered
    assert "recipes-count" in rendered
    assert "data-title=" in rendered
    assert "data-ingredients=" in rendered


def test_index_page_contains_advanced_filters():
    recipe1 = parse_recipe(Path("recipes/risotto-poulet-champignons.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("index.html").render(
        recipes=[recipe1],
        primary_tags=["risotto", "volaille"],
        advanced_tags=["champignons", "fromage", "italien"],
    )

    assert "advanced-filter-toggle" in rendered
    assert "advanced-filters-panel" in rendered
    assert 'data-advanced-tag="champignons"' in rendered
    assert "clear-advanced-btn" in rendered
