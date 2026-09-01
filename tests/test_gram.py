from pathlib import Path

from generator.gram import parse_recipe


def test_example_recipe_is_parsed():
    recipe = parse_recipe(Path("recipes/magret-rose.gram"))
    assert recipe.title == "Magret de canard rosé"
    assert len(recipe.steps) == 6
    assert recipe.steps[2].timers[0]["seconds"] == 420
    assert recipe.steps[0].temperatures == ["180 C"]
    assert any(item.name == "magrets de canard" for item in recipe.ingredients)
    assert recipe.scalable is True
    assert recipe.min_portions == 1
    assert recipe.max_portions == 8


def test_fixed_recipe_requires_a_reason(tmp_path):
    source = tmp_path / "fixed.gram"
    source.write_text("""---
title: Recette précise
portions: 4
scaling:
  enabled: false
  reason: Calibrée pour un bol précis.
---
[Mélanger] Mélanger @farine{100 g}.
""", encoding="utf-8")

    recipe = parse_recipe(source)
    assert recipe.scalable is False
    assert recipe.scaling_note == "Calibrée pour un bol précis."


def test_cookidoo_recipe_exposes_preparation_times():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))

    assert recipe.prep_time == "10 min"
    assert recipe.total_time == "45 min"
    assert recipe.scalable is False
    assert recipe.metadata["appliances"]["thermomix"] == ["TM5", "TM6", "TM7"]
