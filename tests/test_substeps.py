from pathlib import Path

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


def test_substeps_rendered_in_templates(render_template):
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    cook_html = render_template("cook.html", recipe=recipe)
    recipe_html = render_template("recipe.html", recipe=recipe)

    assert "substeps-card" in cook_html
    assert "substep-checkbox" in cook_html
    assert "substeps-preview-list" in recipe_html
