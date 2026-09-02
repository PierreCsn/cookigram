from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_recipe_page_contains_share_button():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "share-btn" in rendered
    assert "recipe-actions" in rendered
    assert "Partager" in rendered


def test_recipe_page_contains_shopping_checklist_and_export():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "checklist" in rendered
    assert "copy-list" in rendered
    assert "keep-list" in rendered
    assert "share-list" in rendered
    assert "reset-checklist" in rendered
    assert "ingredient-checkbox" in rendered
    assert "toast" in rendered


def test_recipe_page_distinguishes_source_and_human_appliance_compatibility():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "Matériel indispensable" in rendered
    assert "Thermomix TM31, TM5, TM6 ou TM7" in rendered
    assert "TM31 · compatibilité testée par un humain sur 6 portions" in rendered
    assert "Illustration :" in rendered
    assert "Illustration générée par IA pour CookiGram" in rendered
