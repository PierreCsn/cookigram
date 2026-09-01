import argparse
import json
import shutil
from dataclasses import asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .gram import parse_recipe
from .plugins import apply_plugins

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ROOT / "static", output / "assets")
    shutil.copy2(ROOT / "static" / "sw.js", output / "sw.js")

    recipes = [parse_recipe(path) for path in sorted((ROOT / "recipes").glob("*.gram"))]
    for recipe in recipes:
        apply_plugins(recipe, ROOT / "plugins")

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
        ),
        encoding="utf-8",
    )

    for recipe in recipes:
        recipe_dir = output / "recipes" / recipe.slug
        cook_dir = recipe_dir / "cook"
        cook_dir.mkdir(parents=True)
        (recipe_dir / "index.html").write_text(env.get_template("recipe.html").render(recipe=recipe), encoding="utf-8")
        (cook_dir / "index.html").write_text(env.get_template("cook.html").render(recipe=recipe), encoding="utf-8")

    payload = [asdict(recipe) for recipe in recipes]
    (output / "recipes.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = json.loads((output / "assets" / "manifest.webmanifest").read_text(encoding="utf-8"))
    manifest["start_url"] = "./"
    (output / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    build(parser.parse_args().output.resolve())
