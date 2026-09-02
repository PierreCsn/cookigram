"""SEO, Schema.org JSON-LD, Open Graph, Sitemap and RSS feed generation for CookiGram."""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generator.models import Recipe

DEFAULT_SITE_URL = "https://pierrecsn.github.io/cookigram"


def format_iso_duration(time_str: str | None) -> str | None:
    """Converts human-readable culinary time strings into ISO 8601 duration format.

    Examples:
        "15 min" -> "PT15M"
        "1 h 15 min" -> "PT1H15M"
        "4 h 35 min" -> "PT4H35M"
        "30 s" -> "PT30S"
    """
    if not time_str:
        return None
    raw = time_str.strip().lower()

    hours, minutes, seconds = 0, 0, 0
    if h_match := re.search(r"(\d+)\s*h(?:eures?)?", raw):
        hours = int(h_match.group(1))
    if m_match := re.search(r"(\d+)\s*min(?:utes?)?", raw):
        minutes = int(m_match.group(1))
    if s_match := re.search(r"(\d+)\s*s(?:ec(?:ondes?)?)?", raw):
        seconds = int(s_match.group(1))

    if not any((hours, minutes, seconds)):
        return None

    parts = ["PT"]
    if hours:
        parts.append(f"{hours}H")
    if minutes:
        parts.append(f"{minutes}M")
    if seconds:
        parts.append(f"{seconds}S")
    return "".join(parts)


def build_recipe_schema(recipe: Recipe, site_url: str = DEFAULT_SITE_URL) -> dict[str, Any]:
    """Builds a Schema.org Recipe JSON-LD representation."""
    base_url = site_url.rstrip("/")
    canonical_url = f"{base_url}/recipes/{recipe.slug}/"

    author = recipe.metadata.get("author")
    description = (
        recipe.description or f"Recette de {recipe.title} préparée en {recipe.total_time or 'quelques étapes'}."
    )

    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe.title,
        "description": description,
        "url": canonical_url,
        "mainEntityOfPage": canonical_url,
        "recipeYield": f"{recipe.portions} portions",
        "inLanguage": "fr-FR",
    }

    if recipe.image:
        schema["image"] = [f"{base_url}/assets/{recipe.image}"]

    if author:
        schema["author"] = {"@type": "Person", "name": author}
    else:
        schema["author"] = {"@type": "Organization", "name": "CookiGram", "url": base_url}

    if iso_prep := format_iso_duration(recipe.prep_time):
        schema["prepTime"] = iso_prep

    if iso_total := format_iso_duration(recipe.total_time):
        schema["totalTime"] = iso_total

    if recipe.tags:
        schema["keywords"] = ", ".join(recipe.tags)
        schema["recipeCategory"] = recipe.tags[0].capitalize()

    # Ingredients list formatted cleanly
    ingredients_list = []
    for item in recipe.ingredients:
        if item.quantity:
            ingredients_list.append(f"{item.name} ({item.quantity})")
        else:
            ingredients_list.append(item.name)
    schema["recipeIngredient"] = ingredients_list

    # Step by step instructions
    instructions = []
    for i, step in enumerate(recipe.steps, 1):
        step_obj: dict[str, Any] = {
            "@type": "HowToStep",
            "position": i,
            "name": step.action,
            "text": step.text or step.action,
            "url": f"{canonical_url}cook/#step-{i}",
        }
        instructions.append(step_obj)
    schema["recipeInstructions"] = instructions

    # Nutrition details if available
    nutrition = recipe.nutrition
    if isinstance(nutrition, dict) and nutrition.get("calories"):
        schema["nutrition"] = {
            "@type": "NutritionInformation",
            "calories": f"{nutrition.get('calories')} calories",
            "proteinContent": f"{nutrition.get('protein', 0)} g",
            "carbohydrateContent": f"{nutrition.get('carbs', 0)} g",
            "fatContent": f"{nutrition.get('fat', 0)} g",
            "servingSize": "1 portion",
        }

    return schema


def build_sitemap_xml(recipes: list[Recipe], site_url: str = DEFAULT_SITE_URL) -> str:
    """Generates an XML sitemap complying with sitemaps.org standards including Google Image extensions."""
    base_url = site_url.rstrip("/")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        "  <url>",
        f"    <loc>{base_url}/</loc>",
        "    <changefreq>weekly</changefreq>",
        "    <priority>1.0</priority>",
        "  </url>",
    ]

    for recipe in recipes:
        recipe_url = f"{base_url}/recipes/{recipe.slug}/"
        cook_url = f"{base_url}/recipes/{recipe.slug}/cook/"

        # Recipe page
        lines.append("  <url>")
        lines.append(f"    <loc>{recipe_url}</loc>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        if recipe.image:
            image_url = f"{base_url}/assets/{recipe.image}"
            safe_title = html.escape(recipe.title, quote=True)
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{image_url}</image:loc>")
            lines.append(f"      <image:title>{safe_title}</image:title>")
            lines.append("    </image:image>")
        lines.append("  </url>")

        # Cook mode page
        lines.append("  <url>")
        lines.append(f"    <loc>{cook_url}</loc>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.5</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots_txt(site_url: str = DEFAULT_SITE_URL) -> str:
    """Generates a standard robots.txt referencing the sitemap."""
    base_url = site_url.rstrip("/")
    return f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""


def build_rss_feed(recipes: list[Recipe], site_url: str = DEFAULT_SITE_URL) -> str:
    """Generates an RSS 2.0 feed listing all available recipes."""
    base_url = site_url.rstrip("/")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        "    <title>CookiGram 🍳</title>",
        f"    <link>{base_url}/</link>",
        "    <description>Carnet de recettes culinaires moderne, guidé et hors ligne.</description>",
        "    <language>fr-FR</language>",
        f'    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml" />',
    ]

    for recipe in recipes:
        recipe_url = f"{base_url}/recipes/{recipe.slug}/"
        safe_title = html.escape(recipe.title)
        desc = recipe.description or f"Recette de {recipe.title} ({recipe.portions} portions)"
        safe_desc = html.escape(desc)

        lines.append("    <item>")
        lines.append(f"      <title>{safe_title}</title>")
        lines.append(f"      <link>{recipe_url}</link>")
        lines.append(f'      <guid isPermaLink="true">{recipe_url}</guid>')
        lines.append(f"      <description>{safe_desc}</description>")
        for tag in recipe.tags:
            lines.append(f"      <category>{html.escape(tag)}</category>")
        lines.append("    </item>")

    lines.append("  </channel>")
    lines.append("</rss>")
    return "\n".join(lines) + "\n"
