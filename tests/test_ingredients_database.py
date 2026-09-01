from pathlib import Path

import yaml


def test_ingredient_database_has_valid_minimal_entries():
    payload = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))
    ingredients = payload["ingredients"]

    assert ingredients
    for slug, ingredient in ingredients.items():
        assert slug == slug.casefold()
        assert " " not in slug
        assert ingredient["name"].strip()
        assert len(ingredient.get("aliases", [])) == len(set(ingredient.get("aliases", [])))


def test_magret_recipe_is_covered_by_database():
    payload = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))
    magret = payload["ingredients"]["magret-de-canard"]

    assert "magrets de canard" in magret["aliases"]


def test_provenance_covers_database_and_uses_known_statuses():
    database = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))["ingredients"]
    provenance = yaml.safe_load(Path(".gram/ingredient-provenance.yaml").read_text(encoding="utf-8"))["ingredients"]
    assert set(database) == set(provenance)
    assert {item["status"] for item in provenance.values()} <= {"incomplete", "estimated", "verified", "manual"}
