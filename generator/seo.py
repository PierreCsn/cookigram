"""SEO, Schema.org JSON-LD, Open Graph, Sitemap and RSS feed generation for CookiGram."""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generator.models import Recipe

DEFAULT_SITE_URL = "https://pierrecsn.github.io/cookigram"


def is_thermomix_compatible(recipe: Recipe) -> bool:
    """Return whether a recipe advertises a Thermomix-compatible preparation."""
    if any(str(tag).casefold() == "thermomix" for tag in recipe.tags):
        return True
    appliances = recipe.metadata.get("appliances", {}) if recipe.metadata else {}
    return bool(appliances.get("thermomix")) if isinstance(appliances, dict) else False


def build_recipe_meta_description(recipe: Recipe) -> str:
    """Build a search snippet in the 120–155 character recommendation range.

    The length is measured on the HTML-escaped form (as rendered into a
    ``<meta>`` tag), so the encoded output never overflows the recommendation
    even when the copy contains apostrophes or quotes.
    """
    description = " ".join(str(recipe.description or "").split())
    if len(description) >= 120:
        return _fit_meta(description)

    thermomix_hint = " Préparation guidée au Thermomix." if is_thermomix_compatible(recipe) else ""
    fallback = (
        f"Recette de {recipe.title} : prête en {recipe.total_time or recipe.prep_time or 'quelques étapes'} "
        f"pour {recipe.portions} portions.{thermomix_hint} Ingrédients, étapes détaillées et nutrition sur CookiGram."
    )
    if len(fallback) < 120:
        fallback += " Cuisinez simplement, pas à pas."
    return _fit_meta(fallback)


def _escaped_len(text: str) -> int:
    """Length of the text once HTML-escaped, as emitted in a <meta> tag."""
    return len(html.escape(text))


def _fit_meta(text: str) -> str:
    """Truncate copy so its HTML-escaped form stays at most 155 characters.

    The caller guarantees the raw text is already at least 120 characters, so
    the escaped length (which is always >= the raw length) stays within the
    recommended search-snippet range.
    """
    if _escaped_len(text) <= 155:
        return text

    words = text.split()
    candidate = text
    while words and _escaped_len(candidate) > 155:
        words = words[:-1]
        candidate = " ".join(words).rstrip(".,;:")
    if candidate != text and words:
        candidate = candidate.rstrip(".,;:") + "..."
    while _escaped_len(candidate) > 155 and len(candidate) > 60:
        candidate = candidate[:-1]
    return candidate


# Tags that are too generic to convey thematic similarity; they must not
# dominate the related-recipes scoring ("réconfort", "rapide", ...).
GENERIC_TAGS = {"rapide", "réconfort", "traditionnel", "thermomix"}


def _ingredient_families(recipe: Recipe) -> set[str]:
    """Normalized ingredient families (main protein/produce) used for topical matches."""
    families = set()
    for item in recipe.ingredients:
        name = item.name.casefold().strip()
        for family in (
            "poulet",
            "porc",
            "boeuf",
            "poisson",
            "saumon",
            "crevettes",
            "gambas",
            "lentilles",
            "pomme de terre",
            "carotte",
            "potiron",
            "butternut",
            "asperge",
            "pois",
            "pates",
            "riz",
        ):
            if family in name:
                families.add(family)
    return families


def compute_similar_recipes(recipe: Recipe, all_recipes: list[Recipe], limit: int = 4) -> list[Recipe]:
    """Deterministically rank the most topically-related recipes.

    Scoring is based on shared meaningful tags (weight 3), overlapping
    ingredient families (weight 2) and Thermomix compatibility (weight 1).
    A reciprocal tiebreak prefers candidates whose own broader selection also
    features this recipe, keeping the internal-linking mesh balanced and
    bidirectional. The result is stable across builds (score desc, then
    reciprocity, then slug asc).
    """
    candidates = [other for other in all_recipes if other.slug != recipe.slug]
    own_tags = {str(tag).casefold() for tag in recipe.tags}
    own_families = _ingredient_families(recipe)
    own_tmx = is_thermomix_compatible(recipe)

    scored: list[tuple[int, str, Recipe]] = []
    for other in candidates:
        score = _similarity_score(recipe, other, own_tags, own_families, own_tmx)
        if score > 0:
            scored.append((score, other.slug, other))

    scored.sort(key=lambda item: (-item[0], item[1]))

    if len(scored) <= limit:
        return [item[2] for item in scored]

    # Favour candidates that already rank this recipe in their own top-K, so
    # the mesh is reciprocated (bidirectional) rather than one-way. Based purely
    # on the symmetric score, it is deterministic and independent of the order
    # recipes are processed in.
    wider_window = limit + 2
    reciprocal_pool: set[str] = set()
    for other in candidates:
        other_tags = {str(tag).casefold() for tag in other.tags}
        other_families = _ingredient_families(other)
        other_tmx = is_thermomix_compatible(other)
        ranked: list[tuple[int, str]] = []
        for candidate in all_recipes:
            if candidate.slug == other.slug:
                continue
            s = _similarity_score(other, candidate, other_tags, other_families, other_tmx)
            if s > 0:
                ranked.append((s, candidate.slug))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        top = {slug for _, slug in ranked[:wider_window]}
        if recipe.slug in top:
            reciprocal_pool.add(other.slug)

    ordered = [(score, 0 if slug in reciprocal_pool else 1, slug, other) for score, slug, other in scored]
    ordered.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [item[3] for item in ordered[:limit]]


def _similarity_score(
    a: Recipe,
    b: Recipe,
    a_tags: set[str] | None = None,
    a_families: set[str] | None = None,
    a_tmx: bool | None = None,
) -> int:
    """Raw symmetric topical-similarity score between two recipes."""
    a_tag_set = a_tags if a_tags is not None else {str(tag).casefold() for tag in a.tags}
    b_tag_set = {str(tag).casefold() for tag in b.tags}
    meaningful_shared = len((a_tag_set & b_tag_set) - GENERIC_TAGS)
    a_family_set = a_families if a_families is not None else _ingredient_families(a)
    shared_families = len(a_family_set & _ingredient_families(b))
    a_is_tmx = a_tmx if a_tmx is not None else is_thermomix_compatible(a)
    shared_tmx = 1 if a_is_tmx and is_thermomix_compatible(b) else 0
    return meaningful_shared * 3 + shared_families * 2 + shared_tmx


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
