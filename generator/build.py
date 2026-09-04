import argparse
import hashlib
import json
import shutil
from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .gram import parse_recipe
from .ingredient_icons import IngredientIconResolver, attach_ingredient_icons
from .plugins import PluginManager
from .seo import (
    DEFAULT_SITE_URL,
    build_recipe_meta_description,
    build_recipe_schema,
    build_recipe_seo_title,
    build_robots_txt,
    build_rss_feed,
    build_sitemap_xml,
    compute_similar_recipes,
    is_thermomix_compatible,
)
from .utensils import resolve_utensil_icon

ROOT = Path(__file__).resolve().parents[1]


ASSETS_TO_VERSION = ("app.css", "app.js")


def compute_asset_version(assets_path: Path) -> str:
    """Content-hash of every static asset, used for cache-busting.

    Any change to an asset, including a recipe image, changes the hash. This
    bumps the frontend URLs and the service worker cache name so an installed
    PWA never keeps an old image under an unchanged URL.
    """
    digest = hashlib.sha256()
    for path in sorted(item for item in assets_path.rglob("*") if item.is_file()):
        digest.update(path.relative_to(assets_path).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def build_precache_urls(output: Path, version: str) -> list[str]:
    """Return every user-facing build resource with its actual request URL."""
    urls = []
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(output)
        if relative.as_posix() in {".nojekyll", "sw.js", "sitemap.xml", "robots.txt", "feed.xml"}:
            continue
        if relative.name == "index.html":
            parent = relative.parent.as_posix()
            url = "./" if parent == "." else f"./{parent}/"
        elif relative.parts[0] == "assets" and relative.name in ASSETS_TO_VERSION:
            url = f"./{relative.as_posix()}?v={version}"
        else:
            url = f"./{relative.as_posix()}"
        urls.append(url)
    return list(dict.fromkeys(urls))


CSS_SOURCES = (
    "variables.css",
    "base.css",
    "topbar.css",
    "catalogue.css",
    "recipe.css",
    "ingredients.css",
    "modal.css",
    "cook.css",
    "timers.css",
    "thermomix.css",
)

# Standalone component stylesheets shipped at the `static/` root (portion and
# variant pickers, recipe images). They are folded into the single app.css so the
# pages no longer issue separate render-blocking CSS requests.
ROOT_CSS_SOURCES = ("scaling.css", "variants.css", "images.css")


def compile_css(css_dir: Path, output_file: Path) -> None:
    """Concatenates modular CSS source files into a unified production stylesheet."""
    if not css_dir.exists():
        return
    parts = []
    for filename in CSS_SOURCES:
        file_path = css_dir / filename
        if file_path.exists():
            parts.append(f"/* === {filename} === */\n" + file_path.read_text(encoding="utf-8").strip())
    for filename in ROOT_CSS_SOURCES:
        file_path = css_dir.parent / filename
        if file_path.exists():
            parts.append(f"/* === {filename} === */\n" + file_path.read_text(encoding="utf-8").strip())
    if parts:
        bundled = "\n\n".join(parts) + "\n"
        output_file.write_text(bundled, encoding="utf-8")


def build(output: Path, site_url: str = DEFAULT_SITE_URL) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ROOT / "static", output / "assets")

    # Compile modular CSS sources into a unified app.css
    compile_css(ROOT / "static" / "css", output / "assets" / "app.css")
    compile_css(ROOT / "static" / "css", ROOT / "static" / "app.css")

    # The root component stylesheets are now merged into app.css; drop the
    # redundant copies so they are neither served nor precached separately.
    for extra_css in ROOT_CSS_SOURCES:
        (output / "assets" / extra_css).unlink(missing_ok=True)

    # Keep the site root as the single, correct service worker location.
    # static/sw.js acts as a template rendered with the build version.
    (output / "assets" / "sw.js").unlink(missing_ok=True)

    recipes = [parse_recipe(path) for path in sorted((ROOT / "recipes").glob("*.gram"))]
    plugin_manager = PluginManager.from_directory(ROOT / "plugins")
    icon_resolver = IngredientIconResolver(ROOT)
    for recipe in recipes:
        plugin_manager.apply(recipe)
        attach_ingredient_icons(recipe, icon_resolver)

    version = compute_asset_version(output / "assets")
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape())
    env.globals["recipe_meta_description"] = build_recipe_meta_description
    env.globals["recipe_seo_title"] = build_recipe_seo_title
    env.globals["is_thermomix_compatible"] = is_thermomix_compatible
    env.filters["utensil_icon"] = resolve_utensil_icon
    PRIMARY_THEMES = [
        "pâtes",
        "soupe",
        "mijoté",
        "curry",
        "gratin",
        "volaille",
        "viande",
        "poisson",
        "porc",
        "one-pot",
        "risotto",
    ]
    all_tags = sorted({tag for recipe in recipes for tag in recipe.tags})
    primary_tags = [tag for tag in PRIMARY_THEMES if any(tag in r.tags for r in recipes)]
    advanced_tags = sorted({tag for tag in all_tags if tag not in PRIMARY_THEMES and tag != "thermomix"})

    clean_site_url = site_url.rstrip("/")

    (output / "index.html").write_text(
        env.get_template("index.html").render(
            recipes=recipes,
            all_tags=all_tags,
            primary_tags=primary_tags,
            advanced_tags=advanced_tags,
            asset_version=version,
            site_url=clean_site_url,
            canonical_url=f"{clean_site_url}/",
        ),
        encoding="utf-8",
    )

    (output / "offline.html").write_text(
        env.get_template("offline.html").render(
            asset_version=version,
            site_url=clean_site_url,
        ),
        encoding="utf-8",
    )

    (output / "404.html").write_text(
        env.get_template("404.html").render(
            asset_version=version,
            site_url=clean_site_url,
        ),
        encoding="utf-8",
    )

    for recipe in recipes:
        recipe_dir = output / "recipes" / recipe.slug
        cook_dir = recipe_dir / "cook"
        cook_dir.mkdir(parents=True, exist_ok=True)

        schema_data = build_recipe_schema(recipe, clean_site_url)
        schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)

        (recipe_dir / "index.html").write_text(
            env.get_template("recipe.html").render(
                recipe=recipe,
                related_recipes=compute_similar_recipes(recipe, recipes),
                asset_version=version,
                site_url=clean_site_url,
                schema_json=schema_json,
            ),
            encoding="utf-8",
        )
        (cook_dir / "index.html").write_text(
            env.get_template("cook.html").render(
                recipe=recipe,
                asset_version=version,
                site_url=clean_site_url,
            ),
            encoding="utf-8",
        )

    payload = [asdict(recipe) for recipe in recipes]
    (output / "recipes.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = json.loads((output / "assets" / "manifest.webmanifest").read_text(encoding="utf-8"))
    manifest["start_url"] = "./"
    (output / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / ".nojekyll").touch()

    # Generate sitemap, robots.txt, and RSS feed
    (output / "sitemap.xml").write_text(build_sitemap_xml(recipes, clean_site_url), encoding="utf-8")
    (output / "robots.txt").write_text(build_robots_txt(clean_site_url), encoding="utf-8")
    (output / "feed.xml").write_text(build_rss_feed(recipes, clean_site_url), encoding="utf-8")

    precache_urls = build_precache_urls(output, version)
    sw_source = (ROOT / "static" / "sw.js").read_text(encoding="utf-8")
    rendered_sw = sw_source.replace("__VERSION__", version).replace(
        "__PRECACHE__", json.dumps(precache_urls, ensure_ascii=False, indent=2)
    )
    (output / "sw.js").write_text(rendered_sw, encoding="utf-8")

    cov_path = ROOT / "coverage.json"
    if cov_path.exists():
        try:
            cov_data = json.loads(cov_path.read_text(encoding="utf-8"))
            cov_pct = int(round(float(cov_data["totals"]["percent_covered_display"])))
            color = "brightgreen" if cov_pct >= 80 else "yellow" if cov_pct >= 60 else "red"
            (output / "coverage.json").write_text(
                json.dumps(
                    {"schemaVersion": 1, "label": "coverage", "message": f"{cov_pct}%", "color": color}, indent=2
                ),
                encoding="utf-8",
            )
        except Exception:
            pass
    elif (ROOT / "static" / "coverage.json").exists():
        shutil.copy(ROOT / "static" / "coverage.json", output / "coverage.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--site-url", type=str, default=DEFAULT_SITE_URL)
    args = parser.parse_args()
    build(args.output.resolve(), site_url=args.site_url)
