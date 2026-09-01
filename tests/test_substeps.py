from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_substeps_are_parsed_correctly():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))

    assert len(recipe.steps) == 8
    # Step 0: [Préparer le bol et le riz]
    assert len(recipe.steps[0].substeps) == 3
    assert any("riz basmati" in s for s in recipe.steps[0].substeps)
    assert any(ing.name == "riz basmati" for ing in recipe.ingredients)
    assert any(eq == "bol Thermomix" for eq in recipe.equipment)

    # Step 1: [Préparer la volaille et les légumes au Varoma]
    assert len(recipe.steps[1].substeps) == 5

    # Step 2: [Lancer la cuisson vapeur]
    assert recipe.steps[2].timers[0]["seconds"] == 1200


def test_substeps_rendered_in_templates():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )

    cook_html = env.get_template("cook.html").render(recipe=recipe)
    recipe_html = env.get_template("recipe.html").render(recipe=recipe)

    assert "substeps-card" in cook_html
    assert "substep-checkbox" in cook_html
    assert "substeps-preview-list" in recipe_html
