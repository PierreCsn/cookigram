from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe
from generator.plugins import PluginManager


def test_no_empty_plugin_box_for_thermomix_settings():
    """The thermomix_settings plugin must not render an empty .plugin aside."""
    recipe = parse_recipe(Path("recipes/poulet-tikka-masala.gram"))
    PluginManager.from_directory(Path("plugins")).apply(recipe)
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )

    cook_html = env.get_template("cook.html").render(recipe=recipe)

    # The generic plugin container must not render an empty box for thermomix_settings
    assert '<aside class="plugin"><b></b>' not in cook_html
    assert "thermomix_settings" not in cook_html

    # Thermomix settings are still exposed via the dedicated badge
    assert "tmx-badge" in cook_html


def test_plugin_with_instruction_still_renders():
    """Any future plugin carrying label/instruction continues to render."""
    recipe = parse_recipe(Path("recipes/poulet-tikka-masala.gram"))
    PluginManager.from_directory(Path("plugins")).apply(recipe)
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )

    # Simulate a future plugin with textual instruction (key != thermomix_settings)
    for step in recipe.steps:
        step.plugins["sous_vide"] = {"label": "Sous vide", "instruction": "Cuire 2 h à 60°C"}

    cook_html = env.get_template("cook.html").render(recipe=recipe)
    assert '<aside class="plugin"><b>Sous vide</b><span>Cuire 2 h à 60°C</span></aside>' in cook_html
