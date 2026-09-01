from pathlib import Path

from generator.gram import parse_recipe


def test_example_recipe_is_parsed():
    recipe = parse_recipe(Path("recipes/magret-rose.gram"))
    assert recipe.title == "Magret de canard rosé"
    assert len(recipe.steps) == 6
    assert recipe.steps[2].timers[0]["seconds"] == 420
    assert recipe.steps[0].temperatures == ["180 C"]
    assert any(item.name == "magrets de canard" for item in recipe.ingredients)

