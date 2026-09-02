from pathlib import Path

from generator.build import build
from generator.gram import parse_recipe
from generator.seo import (
    DEFAULT_SITE_URL,
    build_recipe_schema,
    build_robots_txt,
    build_rss_feed,
    build_sitemap_xml,
    format_iso_duration,
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
