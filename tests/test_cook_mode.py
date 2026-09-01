from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_cook_template_contains_voice_and_timer_controls():
    recipe = parse_recipe(Path("recipes/magret-rose.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("cook.html").render(recipe=recipe)

    assert "auto-speak" in rendered
    assert "step-speak" in rendered
    assert "timer" in rendered
    assert "timer-toggle" in rendered
    assert "timer-reset" in rendered
    assert 'data-seconds="420"' in rendered
    assert 'data-step-num="3"' in rendered
