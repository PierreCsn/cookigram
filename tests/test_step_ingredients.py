from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def _render_cook(recipe):
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    return env.get_template("cook.html").render(recipe=recipe)


def test_step_ingredients_are_rendered_in_cook_mode():
    recipe = parse_recipe(Path("recipes/poulet-tikka-masala.gram"))
    cook_html = _render_cook(recipe)

    # The contextual card must be present for steps that mention ingredients
    assert "step-ingredients-card" in cook_html
    assert "step-ingredients-title" in cook_html
    assert "step-ingredients-list" in cook_html
    assert "step-ingredient-item" in cook_html

    # Quantities carry data-scale-text for dynamic portion scaling
    assert 'data-scale-text="5 c. à café"' in cook_html


def test_step_ingredients_scale_data_attr_present():
    recipe = parse_recipe(Path("recipes/poulet-tikka-masala.gram"))
    cook_html = _render_cook(recipe)

    # Every rendered quantity exposes its raw value via data-scale-text
    for li in [x.strip() for x in cook_html.split("step-ingredient-qty") if "data-scale-text=" in x]:
        assert "data-scale-text=" in li


def test_steps_without_ingredients_do_not_render_empty_card():
    recipe = parse_recipe(Path("recipes/poulet-tikka-masala.gram"))
    # The card count must equal the number of steps that have ingredients
    cook_html = _render_cook(recipe)
    card_count = cook_html.count("step-ingredients-card")
    steps_with = [s for s in recipe.steps if s.ingredients]
    assert card_count == len(steps_with)
    assert steps_with
