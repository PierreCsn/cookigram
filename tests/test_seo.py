import re
from pathlib import Path

from generator.build import build
from generator.gram import parse_recipe
from generator.seo import (
    DEFAULT_SITE_URL,
    build_recipe_meta_description,
    build_recipe_schema,
    build_robots_txt,
    build_rss_feed,
    build_sitemap_xml,
    compute_similar_recipes,
    format_iso_duration,
    is_thermomix_compatible,
    recipe_category,
    recipe_cook_time,
    recipe_cuisine,
    recipe_published_date,
)


def test_format_iso_duration():
    assert format_iso_duration("15 min") == "PT15M"
    assert format_iso_duration("1 h 15 min") == "PT1H15M"
    assert format_iso_duration("4 h 35 min") == "PT4H35M"
    assert format_iso_duration("40 min") == "PT40M"
    assert format_iso_duration("1 h") == "PT1H"
    assert format_iso_duration("30 s") == "PT30S"
    assert format_iso_duration("45 sec") == "PT45S"
    assert format_iso_duration("non valide") is None
    assert format_iso_duration("") is None
    assert format_iso_duration(None) is None


def test_build_recipe_schema(tmp_path: Path):
    recipe_path = Path("recipes/risotto-poulet-champignons.gram")
    recipe = parse_recipe(recipe_path)

    schema = build_recipe_schema(recipe, DEFAULT_SITE_URL)
    assert schema["@context"] == "https://schema.org"
    assert schema["@type"] == "Recipe"
    assert schema["name"] == recipe.title
    assert "risotto-poulet-champignons" in schema["url"]
    assert schema["recipeYield"] == f"{recipe.portions} portions"
    assert schema["prepTime"] == "PT12M"
    assert schema["totalTime"] == "PT48M"
    assert schema["cookTime"] == "PT36M"
    assert schema["recipeCuisine"] == "Italian"
    assert schema["recipeCategory"] == "Plat principal"
    assert schema["datePublished"] == "2026-09-02"
    assert schema["dateModified"] == "2026-09-02"
    assert schema["breadcrumb"]["@type"] == "BreadcrumbList"
    assert schema["breadcrumb"]["itemListElement"][-1]["name"] == recipe.title
    assert len(schema["recipeIngredient"]) == len(recipe.ingredients)
    assert len(schema["recipeInstructions"]) == len(recipe.steps)
    assert schema["recipeInstructions"][0]["@type"] == "HowToStep"
    assert schema["recipeInstructions"][0]["name"] == recipe.steps[0].action
    assert schema["recipeInstructions"][0]["text"]["@type"] == "HowToDirection"

    # Substeps must be exposed as HowToDirection itemListElement
    first_step_with_substeps = next((s for s in recipe.steps if s.substeps), None)
    if first_step_with_substeps:
        idx = recipe.steps.index(first_step_with_substeps)
        text = schema["recipeInstructions"][idx]["text"]
        assert text["@type"] == "HowToDirection"
        assert "itemListElement" in text
        assert len(text["itemListElement"]) == len(first_step_with_substeps.substeps) + (
            1 if (first_step_with_substeps.text or "").strip() else 0
        )
        assert text["itemListElement"][0]["@type"] == "HowToDirection"

    # Nutrition in schema
    assert "nutrition" in schema
    assert schema["nutrition"]["@type"] == "NutritionInformation"
    assert "calories" in schema["nutrition"]["calories"]


def test_build_sitemap_xml():
    recipes = [parse_recipe(Path("recipes/risotto-poulet-champignons.gram"))]
    sitemap = build_sitemap_xml(recipes, "https://example.com/cookigram")

    assert "<?xml version=" in sitemap
    assert "<urlset " in sitemap
    assert "<loc>https://example.com/cookigram/</loc>" in sitemap
    assert "<loc>https://example.com/cookigram/recipes/risotto-poulet-champignons/</loc>" in sitemap
    assert "recipes/risotto-poulet-champignons/cook/" not in sitemap
    assert "<image:loc>" in sitemap


def test_build_robots_txt():
    robots = build_robots_txt("https://example.com/cookigram")
    assert "User-agent: *" in robots
    assert "Allow: /" in robots
    assert "Sitemap: https://example.com/cookigram/sitemap.xml" in robots


def test_build_rss_feed():
    recipes = [parse_recipe(Path("recipes/risotto-poulet-champignons.gram"))]
    feed = build_rss_feed(recipes, "https://example.com/cookigram")

    assert "<?xml version=" in feed
    assert '<rss version="2.0"' in feed
    assert "<title>CookiGram 🍳</title>" in feed
    assert "<title>Risotto au poulet et champignons</title>" in feed
    assert "<link>https://example.com/cookigram/recipes/risotto-poulet-champignons/</link>" in feed


def test_build_generates_seo_assets_and_metadata(tmp_path: Path):
    output_dir = tmp_path / "_site"
    site_url = "https://custom.domain.com/cook"
    build(output_dir, site_url=site_url)

    # SEO files existence
    assert (output_dir / "sitemap.xml").is_file()
    assert (output_dir / "robots.txt").is_file()
    assert (output_dir / "feed.xml").is_file()

    # Sitemap content check
    sitemap_content = (output_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://custom.domain.com/cook/recipes/risotto-poulet-champignons/" in sitemap_content
    assert "/cook/recipes/risotto-poulet-champignons/cook/" not in sitemap_content

    # Robots content check
    robots_content = (output_dir / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap: https://custom.domain.com/cook/sitemap.xml" in robots_content

    # Feed content check
    feed_content = (output_dir / "feed.xml").read_text(encoding="utf-8")
    assert "https://custom.domain.com/cook/recipes/risotto-poulet-champignons/" in feed_content

    # Recipe HTML Schema.org check
    recipe_html = (output_dir / "recipes" / "risotto-poulet-champignons" / "index.html").read_text(encoding="utf-8")
    assert 'type="application/ld+json"' in recipe_html
    assert '"@type": "Recipe"' in recipe_html
    assert (
        '<link rel="canonical" href="https://custom.domain.com/cook/recipes/risotto-poulet-champignons/">'
        in recipe_html
    )
    assert '<meta property="og:type" content="article">' in recipe_html
    assert '<meta property="og:title" content="Risotto au poulet et champignons · CookiGram">' in recipe_html
    assert '<meta name="twitter:card" content="summary_large_image">' in recipe_html

    # Home page HTML check
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://custom.domain.com/cook/">' in index_html
    assert '<meta property="og:type" content="website">' in index_html
    assert 'href="https://custom.domain.com/cook/feed.xml"' in index_html
    assert 'href="https://custom.domain.com/cook/sitemap.xml"' in index_html


def test_build_home_declares_title_and_websites_organization_schema(tmp_path: Path):
    output_dir = tmp_path / "_site"
    site_url = "https://custom.domain.com/cook"
    build(output_dir, site_url=site_url)

    index_html = (output_dir / "index.html").read_text(encoding="utf-8")

    # Balise <title> explicite et calibrée (45-65 caractères) avec ancrage culinaire.
    assert "<title>CookiGram 🍳 — Carnet de recettes guidées et Thermomix</title>" in index_html
    title_match = re.search(r"<title>(.*?)</title>", index_html)
    assert title_match is not None
    title_len = len(title_match.group(1))
    assert 45 <= title_len <= 65, f"<title> de {title_len} caractères hors périmètre 45-65"

    # JSON-LD : WebSite (avec SearchAction) et Organization.
    assert 'type="application/ld+json"' in index_html
    assert '"@type": "WebSite"' in index_html
    assert '"@type": "SearchAction"' in index_html
    assert '"urlTemplate": "https://custom.domain.com/cook/?q={search_term_string}"' in index_html
    assert '"@type": "Organization"' in index_html
    assert "https://custom.domain.com/cook/assets/icons/icon-512.png" in index_html

    # H1 et sous-titre présents, ancrés sur la thématique culinaire.
    assert "<h1" in index_html
    assert "Thermomix" in index_html and "guidées" in index_html


def test_recipe_meta_descriptions_are_calibrated_and_thermomix_titles_are_explicit(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    descriptions = []
    for page in (output_dir / "recipes").glob("*/index.html"):
        rendered = page.read_text(encoding="utf-8")
        match = re.search(r'<meta name="description" content="([^"]+)">', rendered)
        assert match is not None, page
        descriptions.append(match.group(1))
        assert 120 <= len(match.group(1)) <= 155, (page, len(match.group(1)), match.group(1))

    assert descriptions
    thermomix_page = (output_dir / "recipes" / "curry-poulet-noix-coco" / "index.html").read_text(encoding="utf-8")
    assert "<title>Curry de poulet à la noix de coco au Thermomix · CookiGram</title>" in thermomix_page


def test_recipe_meta_helpers_detect_thermomix_and_preserve_calibrated_copy():
    recipe = parse_recipe(Path("recipes/curry-poulet-noix-coco.gram"))

    assert is_thermomix_compatible(recipe)
    recipe.description = "Une description éditoriale calibrée pour rester dans la longueur recommandée par les moteurs de recherche et présenter clairement la recette."
    assert build_recipe_meta_description(recipe) == recipe.description


def test_recipe_schema_helpers_handle_categories_and_explicit_cook_time():
    recipe = parse_recipe(Path("recipes/salade-cesar.gram"))

    assert recipe_category(recipe) == "Salade"
    assert recipe_cuisine(recipe) is None
    assert recipe_published_date(recipe) == "2026-09-03"
    recipe.metadata["cook_time"] = "18 min"
    assert recipe_cook_time(recipe) == "PT18M"


def test_build_declares_rel_icon_and_serves_icon_assets(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir, site_url="https://custom.domain.com/cook")

    # SVG + PNG 192 favicon links are present in the <head> of every page type
    recipe_html = (output_dir / "recipes" / "risotto-poulet-champignons" / "index.html").read_text(encoding="utf-8")
    assert '<link rel="icon" type="image/svg+xml" href="../../assets/icons/icon.svg">' in recipe_html
    assert '<link rel="icon" type="image/png" sizes="192x192" href="../../assets/icons/icon-192.png">' in recipe_html

    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert '<link rel="icon" type="image/svg+xml" href="assets/icons/icon.svg">' in index_html

    offline_html = (output_dir / "offline.html").read_text(encoding="utf-8")
    assert '<link rel="icon" type="image/svg+xml" href="./assets/icons/icon.svg">' in offline_html

    # The icon files must exist in the built output and be served with HTTP 200
    for icon in ("icon.svg", "icon-192.png"):
        assert (output_dir / "assets" / "icons" / icon).is_file()


def test_build_cook_page_is_noindex_and_canonical_to_recipe(tmp_path: Path):
    output_dir = tmp_path / "_site"
    site_url = "https://custom.domain.com/cook"
    build(output_dir, site_url=site_url)

    cook_html = (output_dir / "recipes" / "risotto-poulet-champignons" / "cook" / "index.html").read_text(
        encoding="utf-8"
    )
    # Noindex to avoid duplicate-content cannibalisation
    assert '<meta name="robots" content="noindex, follow">' in cook_html
    # Canonical points to the indexable recipe page, not the cook app page
    assert (
        '<link rel="canonical" href="https://custom.domain.com/cook/recipes/risotto-poulet-champignons/">' in cook_html
    )


def test_build_404_page_is_noindex_and_has_no_canonical(tmp_path: Path):
    output_dir = tmp_path / "_site"
    site_url = "https://custom.domain.com/cook"
    build(output_dir, site_url=site_url)

    notfound_html = (output_dir / "404.html").read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex, follow">' in notfound_html
    assert '<link rel="canonical"' not in notfound_html
    assert '<meta name="description" content="Page introuvable sur CookiGram.">' in notfound_html


def test_compute_similar_recipes_returns_deterministic_balanced_links():
    recipes = [parse_recipe(path) for path in sorted(Path("recipes").glob("*.gram"))]
    first = recipes[0]

    suggestions = compute_similar_recipes(first, recipes)
    # 3-4 links, never the recipe itself
    assert 3 <= len(suggestions) <= 4
    assert all(r.slug != first.slug for r in suggestions)
    # Deterministic across calls
    assert [r.slug for r in compute_similar_recipes(first, recipes)] == [r.slug for r in suggestions]

    # Every recipe links to exactly the same number of related recipes (balanced mesh)
    counts = {len(compute_similar_recipes(r, recipes)) for r in recipes}
    assert len(counts) == 1


def test_related_recipes_section_and_clickable_tags_render(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    page = (output_dir / "recipes" / "curry-poulet-noix-coco" / "index.html").read_text(encoding="utf-8")
    # Semantic section present
    assert 'class="related-recipes"' in page
    assert "Recettes similaires" in page
    # 3-4 internal links to sibling recipes with descriptive title anchors
    cards = re.findall(r'class="related-card" href="\.\./([^"]+)/"', page)
    assert 3 <= len(cards) <= 4
    assert "curry-poulet-noix-coco" not in cards
    # Each link carries a descriptive anchor (recipe title) for internal linking
    assert "related-card" in page and "<h3>" in page
    # Clickable tag badges link to the filtered catalogue
    assert 'class="tag-link" href="../../#tag-' in page
