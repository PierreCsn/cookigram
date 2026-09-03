"""SEO, Schema.org JSON-LD, Open Graph, Sitemap and RSS feed generation for CookiGram."""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generator.models import Recipe

DEFAULT_SITE_URL = "https://pierrecsn.github.io/cookigram"

RECIPE_CUISINES = {
    "asiatique": "Asian",
    "cajun": "Cajun",
    "chinois": "Chinese",
    "espagnol": "Spanish",
    "français": "French",
    "indien": "Indian",
    "italien": "Italian",
    "japonais": "Japanese",
    "mexicain": "Mexican",
    "méditerranéen": "Mediterranean",
    "thaï": "Thai",
}

RECIPE_CATEGORIES = (
    ("dessert", "Dessert"),
    ("gâteau", "Dessert"),
    ("tarte", "Dessert"),
    ("salade", "Salade"),
    ("soupe", "Soupe"),
    ("velouté", "Soupe"),
    ("entrée", "Entrée"),
    ("apéritif", "Apéritif"),
)


def is_thermomix_compatible(recipe: Recipe) -> bool:
    """Return whether a recipe advertises a Thermomix-compatible preparation."""
    if any(str(tag).casefold() == "thermomix" for tag in recipe.tags):
        return True
    appliances = recipe.metadata.get("appliances", {}) if recipe.metadata else {}
    return bool(appliances.get("thermomix")) if isinstance(appliances, dict) else False


def build_recipe_meta_description(recipe: Recipe) -> str:
    """Build a search snippet in the 120–155 character recommendation range."""
    description = " ".join(str(recipe.description or "").split())
    if 120 <= len(description) and len(html.escape(description, quote=True)) <= 155:
        return description

    thermomix_hint = " Préparation guidée au Thermomix." if is_thermomix_compatible(recipe) else ""
    fallback = (
        f"Recette de {recipe.title} : prête en {recipe.total_time or recipe.prep_time or 'quelques étapes'} "
        f"pour {recipe.portions} portions.{thermomix_hint} Ingrédients, étapes détaillées et nutrition sur CookiGram."
    )
    if len(fallback) < 120:
        fallback += " Cuisinez simplement, pas à pas."
    if len(html.escape(fallback, quote=True)) <= 155:
        return fallback

    # Leave room for HTML escaping in rendered attributes (for example, an
    # ampersand becomes ``&amp;`` and adds four characters). Trim on word
    # boundaries so the generated snippet remains readable.
    candidate = fallback
    while len(html.escape(candidate + "...", quote=True)) > 155:
        candidate = candidate.rsplit(" ", 1)[0]
    return candidate.rstrip(".,;:") + "..."


def _duration_seconds(time_str: str | None) -> int | None:
    iso = format_iso_duration(time_str)
    if not iso:
        return None

    def component(pattern: str) -> int:
        match = re.search(pattern, iso)
        return int(match.group(1)) if match else 0

    hours = component(r"(\d+)H")
    minutes = component(r"(\d+)M")
    seconds = component(r"(\d+)S")
    return hours * 3600 + minutes * 60 + seconds


def _seconds_to_iso_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = ["PT"]
    if hours:
        parts.append(f"{hours}H")
    if minutes:
        parts.append(f"{minutes}M")
    if seconds:
        parts.append(f"{seconds}S")
    return "".join(parts) if len(parts) > 1 else "PT0S"


def recipe_cook_time(recipe: Recipe) -> str | None:
    """Return explicit cook time or the positive total-minus-preparation duration."""
    explicit = recipe.metadata.get("cook_time") if recipe.metadata else None
    if explicit and (iso := format_iso_duration(str(explicit))):
        return iso
    total_seconds = _duration_seconds(recipe.total_time)
    prep_seconds = _duration_seconds(recipe.prep_time)
    if total_seconds is None or prep_seconds is None or total_seconds <= prep_seconds:
        return None
    return _seconds_to_iso_duration(total_seconds - prep_seconds)


def recipe_cuisine(recipe: Recipe) -> str | None:
    """Map the first recognized cuisine tag to Schema.org's recipeCuisine value."""
    for tag in recipe.tags:
        if cuisine := RECIPE_CUISINES.get(str(tag).casefold()):
            return cuisine
    return None


def recipe_category(recipe: Recipe) -> str:
    """Map dish-type tags to stable culinary categories instead of raw ingredients."""
    tags = {str(tag).casefold() for tag in recipe.tags}
    for tag, category in RECIPE_CATEGORIES:
        if tag in tags:
            return category
    return "Plat principal"


def recipe_published_date(recipe: Recipe) -> str | None:
    """Get a deterministic ISO publication date from recipe metadata."""
    metadata = recipe.metadata or {}
    date = metadata.get("date") or metadata.get("date_published") or metadata.get("published")
    image_generation = metadata.get("image_generation", {})
    if not date and isinstance(image_generation, dict):
        date = image_generation.get("generated_at")
    if not date:
        return None
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", str(date).strip())
    return match.group(1) if match else None


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

    if iso_cook := recipe_cook_time(recipe):
        schema["cookTime"] = iso_cook

    if cuisine := recipe_cuisine(recipe):
        schema["recipeCuisine"] = cuisine

    if published_date := recipe_published_date(recipe):
        schema["datePublished"] = published_date
        schema["dateModified"] = published_date

    if recipe.tags:
        schema["keywords"] = ", ".join(recipe.tags)
    schema["recipeCategory"] = recipe_category(recipe)

    schema["breadcrumb"] = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{base_url}/"},
            {"@type": "ListItem", "position": 2, "name": "Recettes", "item": f"{base_url}/"},
            {"@type": "ListItem", "position": 3, "name": recipe.title, "item": canonical_url},
        ],
    }

    # Ingredients list formatted cleanly
    ingredients_list = []
    for item in recipe.ingredients:
        if item.quantity:
            ingredients_list.append(f"{item.name} ({item.quantity})")
        else:
            ingredients_list.append(item.name)
    schema["recipeIngredient"] = ingredients_list

    # Step by step instructions (substeps are exposed as HowToDirection items)
    instructions = []
    for i, step in enumerate(recipe.steps, 1):
        step_obj: dict[str, Any] = {
            "@type": "HowToStep",
            "position": i,
            "name": step.action,
        }
        # Substep content is exposed as HowToDirection items; the main text is only
        # included when it is non-empty (substeps already carry the actionable content).
        main_text = (step.text or "").strip()
        directions: list[str] = []
        if main_text:
            directions.append(main_text)
        directions.extend(sub for sub in step.substeps if sub)

        directions_obj: dict[str, Any]
        if len(directions) > 1:
            directions_obj = {
                "@type": "HowToDirection",
                "itemListElement": [
                    {"@type": "HowToDirection", "position": j, "text": text} for j, text in enumerate(directions, 1)
                ],
            }
        else:
            directions_obj = {"@type": "HowToDirection", "text": directions[0] if directions else step.action}

        step_obj["text"] = directions_obj
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

        # Recipe page (canonical, indexable) — cook-mode pages are excluded from
        # the sitemap as they are duplicate, non-indexable application pages.
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
