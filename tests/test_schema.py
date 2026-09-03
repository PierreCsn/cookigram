import pytest

from generator.gram import parse_recipe
from generator.schema import RecipeValidationError

VALID_FRONTMATTER = """---
title: Recette de test valide
portions: 4
prep_time: 15 min
total_time: 30 min
tags: [test, plat]
source: https://example.com/recette
author: Chef Test
image: images/lasagnes-moussaka.jpg
image_credit:
  author: Photographe Test
  source: https://example.com/photo
  license: CC-BY
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
---
[preparer | Preparer les ingredients]
- Eplucher les @oignons{2 pieces}.
"""


def test_valid_recipe_passes_contract(tmp_path):
    recipe_file = tmp_path / "valid.gram"
    recipe_file.write_text(VALID_FRONTMATTER, encoding="utf-8")
    recipe = parse_recipe(recipe_file, validate=True)
    assert recipe.title == "Recette de test valide"
    assert len(recipe.steps) == 1


def test_missing_title_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("title: Recette de test valide", "title: ''")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "title"


def test_invalid_portions_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("portions: 4", "portions: 0")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "portions"


def test_missing_steps_raises_validation_error(tmp_path):
    content = """---
title: Sans etape
portions: 4
prep_time: 10 min
total_time: 20 min
tags: [rapide]
source: https://example.com
author: Test
image: images/lasagnes-moussaka.jpg
image_credit:
  author: Test
  source: https://example.com
  license: MIT
scaling:
  enabled: false
  reason: Non scalable
---
# Juste un commentaire sans etape
"""
    recipe_file = tmp_path / "no_steps.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "steps"


def test_missing_image_file_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("images/lasagnes-moussaka.jpg", "images/image-inexistante-xyz.jpg")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "image"


def test_missing_image_credit_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("license: CC-BY", "")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert "image_credit" in exc.value.field


def test_inconsistent_scaling_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("max_portions: 8", "max_portions: 1")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert "scaling" in exc.value.field


def test_missing_scaling_reason_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace(
        "scaling:\n  enabled: true\n  min_portions: 2\n  max_portions: 8\n  step: 1",
        "scaling:\n  enabled: false",
    )
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "scaling.reason"


def test_unknown_ingredient_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("@oignons{2 pieces}", "@ingredient_totalement_inconnu_xyz{100 g}")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "ingredients"
    assert "ingredient_totalement_inconnu_xyz" in str(exc.value)


def test_valid_flavors_and_spiciness_pass_contract(tmp_path):
    content = VALID_FRONTMATTER.replace(
        "scaling:",
        "spiciness: 2\nflavors:\n  pairing:\n  - poulet\n  - citron\n  notes:\n  - acidulé\n  - frais\n  harmony: Un accord vif et léger.\nscaling:",
    )
    recipe_file = tmp_path / "flavored.gram"
    recipe_file.write_text(content, encoding="utf-8")
    recipe = parse_recipe(recipe_file, validate=True)
    assert recipe.metadata["spiciness"] == 2
    assert recipe.metadata["flavors"]["pairing"] == ["poulet", "citron"]
    assert recipe.metadata["flavors"]["notes"] == ["acidulé", "frais"]


def test_invalid_spiciness_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("scaling:", "spiciness: 9\nscaling:")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "spiciness"


def test_malformed_flavors_raises_validation_error(tmp_path):
    content = VALID_FRONTMATTER.replace("scaling:", "flavors:\n  pairing: []\nscaling:")
    recipe_file = tmp_path / "invalid.gram"
    recipe_file.write_text(content, encoding="utf-8")
    with pytest.raises(RecipeValidationError) as exc:
        parse_recipe(recipe_file, validate=True)
    assert exc.value.field == "flavors.pairing"
