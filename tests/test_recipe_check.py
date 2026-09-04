from pathlib import Path

from generator.recipe_check import check_recipe, main


def test_recipe_check_passes_on_valid_recipe():
    path = Path("recipes/butter-chicken.gram")
    errors = check_recipe(path)
    assert errors == []


def test_recipe_check_detects_nonexistent_file(tmp_path):
    path = tmp_path / "inexistant.gram"
    errors = check_recipe(path)
    assert len(errors) == 1
    assert "n'existe pas" in errors[0]


def test_recipe_check_detects_invalid_extension(tmp_path):
    path = tmp_path / "recette.txt"
    path.write_text("dummy", encoding="utf-8")
    errors = check_recipe(path)
    assert len(errors) == 1
    assert "extension .gram" in errors[0]


def test_recipe_check_main_cli_success(capsys):
    ret = main(["recipes/butter-chicken.gram"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CONFORME" in captured.out


def test_recipe_check_main_cli_failure(tmp_path, capsys):
    fake_recipe = tmp_path / "fake.gram"
    fake_recipe.write_text("invalid gram syntax without frontmatter", encoding="utf-8")
    ret = main([str(fake_recipe)])
    assert ret == 1
    captured = capsys.readouterr()
    assert "NON CONFORME" in captured.out
