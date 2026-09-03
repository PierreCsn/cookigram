from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.gram import parse_recipe


def test_recipe_page_contains_share_button():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "share-btn" in rendered
    assert "recipe-actions" in rendered
    assert "Partager" in rendered


def test_recipe_page_contains_shopping_checklist_and_export():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(
        loader=FileSystemLoader(Path("templates")),
        autoescape=select_autoescape(),
    )
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "checklist" in rendered
    assert "copy-list" in rendered
    assert "keep-list" in rendered
    assert "share-list" in rendered
    assert "reset-checklist" in rendered
    assert "ingredient-checkbox" in rendered
    assert "toast" in rendered


def test_recipe_page_distinguishes_source_and_human_appliance_compatibility():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "Matériel indispensable" in rendered
    assert "Thermomix TM31, TM5, TM6 ou TM7" in rendered
    assert "TM31 · compatibilité testée par un humain sur 6 portions" in rendered
    assert "Illustration :" in rendered
    assert "Illustration générée par IA pour CookiGram" in rendered


def test_recipe_illustration_is_present_in_heading_with_lcp_hint():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert 'class="plate"' in rendered
    assert 'fetchpriority="high"' in rendered
    # Explicit dimensions preserve the 16:9 ratio to avoid CLS; informative alt for image SEO
    assert 'width="1280" height="720"' in rendered
    assert 'alt="Illustration de Curry de poulet à la noix de coco"' in rendered
    # The image credit must be visually attached to the plate (inside the heading)
    heading = rendered.split('<section class="recipe-heading">', 1)[1].split("</section>", 1)[0]
    assert "image-credit" in heading


def test_shopping_toolbar_is_pared_down_but_export_remains_in_modal():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    toolbar = rendered.split('class="shopping-toolbar"', 1)[1].split("</div>", 1)[0]
    # Only the main evaluation + reset buttons remain in the compact toolbar
    assert "open-shopping-modal" in toolbar
    assert "reset-checklist" in toolbar
    assert "copy-list" not in toolbar
    assert "keep-list" not in toolbar
    assert "share-list" not in toolbar

    # The modal still hosts the secondary export actions
    modal = rendered.split('id="shopping-modal"', 1)[1]
    assert "copy-list" in modal
    assert "keep-list" in modal
    assert "share-list" in modal


def test_recipe_page_renders_flavor_panel_when_present():
    recipe = parse_recipe(Path("recipes/porc-au-caramel.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "flavor-panel" in rendered
    assert "Saveurs & accord" in rendered
    assert "flavor-pairing" in rendered
    assert "échine de porc" in rendered
    assert "flavor-notes" in rendered
    assert "sucré-salé" in rendered
    assert "flavor-harmony" in rendered
    assert "flavor-spice" in rendered


def test_recipe_page_omits_flavor_panel_when_absent():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))
    env = Environment(loader=FileSystemLoader(Path("templates")), autoescape=select_autoescape())
    rendered = env.get_template("recipe.html").render(recipe=recipe)

    assert "flavor-panel" not in rendered
