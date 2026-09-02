from pathlib import Path

import yaml

from generator.gram import parse_recipe


def test_ingredient_database_has_valid_minimal_entries():
    payload = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))
    ingredients = payload["ingredients"]

    assert ingredients
    for slug, ingredient in ingredients.items():
        assert slug == slug.casefold()
        assert " " not in slug
        assert ingredient["name"].strip()
        assert len(ingredient.get("aliases", [])) == len(set(ingredient.get("aliases", [])))


def test_curry_recipe_is_covered_by_database():
    payload = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))
    poulet = payload["ingredients"]["filet-de-poulet"]

    assert "filet de poulet" in poulet["aliases"]


def test_all_recipe_ingredients_are_covered_by_database():
    database = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))["ingredients"]
    known_names = {
        value.casefold()
        for ingredient in database.values()
        for value in [ingredient["name"], *ingredient.get("aliases", [])]
    }

    for path in Path("recipes").glob("*.gram"):
        recipe = parse_recipe(path)
        missing = {item.name for item in recipe.ingredients if item.name.casefold() not in known_names}
        assert not missing, f"{path}: ingrédients absents de la base : {sorted(missing)}"


def test_provenance_covers_database_and_uses_known_statuses():
    database = yaml.safe_load(Path(".gram/ingredients.yaml").read_text(encoding="utf-8"))["ingredients"]
    provenance = yaml.safe_load(Path(".gram/ingredient-provenance.yaml").read_text(encoding="utf-8"))["ingredients"]
    assert set(database) == set(provenance)
    assert {item["status"] for item in provenance.values()} <= {"incomplete", "estimated", "verified", "manual"}


def test_recipe_images_exist_and_have_no_orphans():
    referenced = set()
    for path in Path("recipes").glob("*.gram"):
        recipe = parse_recipe(path)
        if recipe.image:
            referenced.add(recipe.image)
            assert Path("static", recipe.image).is_file(), f"{path}: image introuvable : {recipe.image}"
        if generation := recipe.metadata.get("image_generation"):
            prompt_file = Path(generation["prompt_file"])
            assert prompt_file.is_file(), f"{path}: prompt d'image introuvable : {prompt_file}"
            assert recipe.metadata["image_credit"]["author"] == "CookiGram"

    available = {path.relative_to("static").as_posix() for path in Path("static/images").iterdir() if path.is_file()}
    assert referenced == available, f"images orphelines : {sorted(available - referenced)}"
