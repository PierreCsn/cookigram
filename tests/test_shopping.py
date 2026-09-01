from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe
from generator.shopping import clean_shopping_quantity, evaluate_recipe_shopping


def test_clean_shopping_quantity():
    assert clean_shopping_quantity("400 g, sans peau, en morceaux de 2 cm") == "400 g"
    assert clean_shopping_quantity("1 c. à café, sur 1 1/2 c. à café au total") == "1 c. à café"
    assert clean_shopping_quantity("3, épluchées et coupées en deux") == "3 pièces"
    assert clean_shopping_quantity("1 pièce, émiettée") == "1 pièce"
    assert clean_shopping_quantity("3") == "3 pièces"


def test_evaluate_recipe_shopping_curry():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    evaluated = evaluate_recipe_shopping(curry)

    # Tap water should be excluded
    all_slugs = [it["slug"] for aisle in evaluated["aisles"].values() for it in aisle]
    all_slugs += [it["slug"] for it in evaluated["staples"]]
    assert "eau" not in all_slugs

    # Staples should be isolated
    staple_slugs = [it["slug"] for it in evaluated["staples"]]
    assert "sel" in staple_slugs
    assert "poivre-moulu" in staple_slugs
    assert "huile-vegetale" in staple_slugs

    # Main ingredients to buy
    to_buy_slugs = [it["slug"] for aisle in evaluated["aisles"].values() for it in aisle]
    assert "filet-de-poulet" in to_buy_slugs
    assert "riz-basmati" in to_buy_slugs
    assert "lait-de-coco" in to_buy_slugs
    assert "poivron" in to_buy_slugs
    assert "courgette" in to_buy_slugs


def test_shopping_modal_rendered():
    curry = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=curry)

    assert "open-shopping-modal" in rendered
    assert "shopping-modal" in rendered
    assert "À acheter au supermarché" in rendered
    assert "Fond de placard" in rendered
    assert "to-buy-cb" in rendered
    assert "staple-cb" in rendered
