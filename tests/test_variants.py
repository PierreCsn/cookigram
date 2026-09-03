from pathlib import Path

import pytest

from generator.gram import parse_recipe

ROAST = Path("recipes/roti-de-porc-sauce-echalote.gram")


def _write(tmp_path: Path, frontmatter: str, body: str = "[base | Base] Utiliser @sel{1 pincée}.") -> Path:
    path = tmp_path / "variant.gram"
    path.write_text(f"---\ntitle: Test\n{frontmatter}\n---\n{body}\n", encoding="utf-8")
    return path


def test_historical_recipe_without_variants_is_unchanged():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    assert recipe.variants == []
    assert recipe.steps


def test_recipe_has_two_variants_and_declared_default():
    recipe = parse_recipe(ROAST)
    assert [variant.id for variant in recipe.variants] == ["thermomix-varoma", "sous-vide-four"]
    assert next(variant.id for variant in recipe.variants if variant.default) == "thermomix-varoma"


def test_variant_changes_ingredients_steps_equipment_and_times():
    recipe = parse_recipe(ROAST)
    sous_vide = next(variant for variant in recipe.variants if variant.id == "sous-vide-four")
    assert "jus de cuisson sous vide" in {item.name for item in sous_vide.ingredients}
    assert "eau" not in {item.name for item in sous_vide.ingredients}
    assert sous_vide.steps[1].id == "sous-vide-cook"
    assert "thermoplongeur" in sous_vide.equipment
    assert sous_vide.total_time == "4 h 35 min"


def test_parallel_operations_are_structured():
    recipe = parse_recipe(ROAST)
    step = next(step for step in recipe.variants[1].steps if step.id == "finish-in-parallel")
    assert [(item.id, item.label) for item in step.parallel] == [("oven", "Four"), ("thermomix", "Thermomix")]
    assert step.parallel[0].timers


def test_variant_references_must_exist(tmp_path):
    path = _write(
        tmp_path,
        """variants:
  - id: broken
    name: Cassée
    steps:
      remove: [missing]""",
    )
    with pytest.raises(ValueError, match="unknown step"):
        parse_recipe(path)


@pytest.mark.parametrize(
    ("frontmatter", "message"),
    [
        ("variants: [{id: same, name: A}, {id: same, name: B}]", "unique"),
        ("variants: [{id: one, name: A, default: true}, {id: two, name: B, default: true}]", "only one"),
    ],
)
def test_variant_validation(tmp_path, frontmatter, message):
    with pytest.raises(ValueError, match=message):
        parse_recipe(_write(tmp_path, frontmatter))


def test_variant_selector_and_direct_link_hooks_are_rendered(render_template):
    recipe = parse_recipe(ROAST)
    recipe_html = render_template("recipe.html", recipe=recipe)
    cook_html = render_template("cook.html", recipe=recipe)
    assert 'data-default-variant="thermomix-varoma"' in recipe_html
    assert 'data-variant="sous-vide-four"' in recipe_html
    assert "variant-select" in recipe_html
    assert "parallel-operation" in cook_html
