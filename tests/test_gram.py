from pathlib import Path

from generator.gram import parse_recipe


def test_example_recipe_is_parsed():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    assert recipe.title == "Curry de poulet à la noix de coco"
    assert len(recipe.steps) == 8
    assert recipe.steps[2].timers[0]["seconds"] == 1200
    assert any(item.name == "filet de poulet" for item in recipe.ingredients)


def test_scalable_recipe_parsing(tmp_path):
    source = tmp_path / "scalable.gram"
    source.write_text("""---
title: Recette ajustable
portions: 4
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
---
[Cuire] Cuire les @pommes de terre{800 g} pendant ~{20 min}.
""", encoding="utf-8")
    recipe = parse_recipe(source)
    assert recipe.scalable is True
    assert recipe.min_portions == 2
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
    assert recipe.image == "images/curry-poulet-noix-coco.jpg"
    assert recipe.metadata["image_credit"]["license"] == "CC BY-SA 4.0"
