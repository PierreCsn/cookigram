import argparse
import hashlib
import json
import shutil
from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .gram import parse_recipe
from .plugins import apply_plugins

ROOT = Path(__file__).resolve().parents[1]

ASSETS_TO_VERSION = ("app.css", "scaling.css", "variants.css", "images.css", "app.js")


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
        if relative.as_posix() in {".nojekyll", "sw.js"}:
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


def build(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ROOT / "static", output / "assets")

    # Keep the site root as the single, correct service worker location.
    # static/sw.js acts as a template rendered with the build version.
    (output / "assets" / "sw.js").unlink(missing_ok=True)

    recipes = [parse_recipe(path) for path in sorted((ROOT / "recipes").glob("*.gram"))]
    for recipe in recipes:
        apply_plugins(recipe, ROOT / "plugins")

    version = compute_asset_version(output / "assets")
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape())
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

    (output / "index.html").write_text(
        env.get_template("index.html").render(
            recipes=recipes,
            all_tags=all_tags,
            primary_tags=primary_tags,
            advanced_tags=advanced_tags,
            asset_version=version,
        ),
        encoding="utf-8",
    )

    for recipe in recipes:
        recipe_dir = output / "recipes" / recipe.slug
        cook_dir = recipe_dir / "cook"
        cook_dir.mkdir(parents=True)
        (recipe_dir / "index.html").write_text(
            env.get_template("recipe.html").render(recipe=recipe, asset_version=version), encoding="utf-8"
        )
        (cook_dir / "index.html").write_text(
            env.get_template("cook.html").render(recipe=recipe, asset_version=version), encoding="utf-8"
        )

    payload = [asdict(recipe) for recipe in recipes]
    (output / "recipes.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = json.loads((output / "assets" / "manifest.webmanifest").read_text(encoding="utf-8"))
    manifest["start_url"] = "./"
    (output / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / ".nojekyll").touch()

    precache_urls = build_precache_urls(output, version)
    sw_source = (ROOT / "static" / "sw.js").read_text(encoding="utf-8")
    rendered_sw = sw_source.replace("__VERSION__", version).replace(
        "__PRECACHE__", json.dumps(precache_urls, ensure_ascii=False, indent=2)
    )
    (output / "sw.js").write_text(rendered_sw, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    build(parser.parse_args().output.resolve())
