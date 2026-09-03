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
    source.write_text(
        """---
title: Recette ajustable
portions: 4
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
---
[Cuire] Cuire les @pommes de terre{800 g} pendant ~{20 min}.
""",
        encoding="utf-8",
    )
    recipe = parse_recipe(source, validate=False)
    assert recipe.scalable is True
    assert recipe.min_portions == 2
    assert recipe.max_portions == 8


def test_fixed_recipe_requires_a_reason(tmp_path):
    source = tmp_path / "fixed.gram"
    source.write_text(
        """---
title: Recette précise
portions: 4
scaling:
  enabled: false
  reason: Calibrée pour un bol précis.
---
[Mélanger] Mélanger @farine{100 g}.
""",
        encoding="utf-8",
    )

    recipe = parse_recipe(source, validate=False)
    assert recipe.scalable is False
    assert recipe.scaling_note == "Calibrée pour un bol précis."


def test_cookidoo_recipe_exposes_preparation_times():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))

    assert recipe.prep_time == "10 min"
    assert recipe.total_time == "45 min"
    assert recipe.scalable is False
    assert recipe.metadata["appliances"]["thermomix"] == ["TM31", "TM5", "TM6", "TM7"]
    assert recipe.metadata["source_appliances"]["thermomix"] == ["TM5", "TM6", "TM7"]
    assert recipe.metadata["appliance_validation"]["TM31"]["status"] == "human-tested"
    assert recipe.metadata["appliance_validation"]["TM31"]["portions"] == 6
    assert recipe.image == "images/curry-poulet-noix-coco.jpg"
    assert recipe.metadata["image_credit"]["license"] == "Illustration générée par IA pour CookiGram"
    assert recipe.metadata["image_generation"]["generated_at"] == "2026-09-02"


def test_compound_durations_are_parsed():
    for path, seconds, label in [
        ("recipes/curry-poulet-express.gram", 290, "4 min 50 s"),
        ("recipes/gratin-pommes-de-terre-saumon-epinards.gram", 270, "4 min 30 s"),
        ("recipes/lasagnes-bolognaise.gram", 630, "10 min 30 s"),
        ("recipes/saumon-a-la-toscane.gram", 90, "1 min 30 s"),
        ("recipes/veloute-langoustines-coriandre.gram", 90, "1 min 30 s"),
    ]:
        recipe = parse_recipe(Path(path), validate=False)
        timer = next(t for step in recipe.steps for t in step.timers if t["seconds"] == seconds)
        assert timer["label"] == label, path


def test_duration_range_is_parsed_with_preserved_label():
    recipe = parse_recipe(Path("recipes/lasagnes-bolognaise.gram"), validate=False)
    timer = next(t for step in recipe.steps for t in step.timers if t["label"] == "30-35 min")
    assert timer["seconds"] == 2100
