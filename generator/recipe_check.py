"""Atomic, ultra-fast validation tool for CookiGram .gram recipes."""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from .gram import parse_recipe
from .ingredient_icons import IngredientIconResolver
from .schema import ROOT, RecipeValidationError


def check_recipe(path: Path, root: Path = ROOT) -> list[str]:
    """Validate a single .gram recipe file and its data dependencies."""
    errors: list[str] = []

    # 1. Existence and extension
    if not path.is_file():
        return [f"Le fichier '{path}' n'existe pas."]
    if path.suffix != ".gram":
        return [f"Le fichier '{path}' doit avoir l'extension .gram."]

    # 2. Schema and Gram syntax parsing
    try:
        recipe = parse_recipe(path, validate=True, root=root)
    except RecipeValidationError as err:
        return [f"Erreur de contrat de données ({err.field}) : {err.message}"]
    except Exception as err:
        return [f"Erreur de syntaxe Gram ou de parsing : {err}"]

    # 3. Ingredients database check
    db_path = root / ".gram" / "ingredients.yaml"
    prov_path = root / ".gram" / "ingredient-provenance.yaml"

    if db_path.is_file():
        db_data: dict[str, Any] = yaml.safe_load(db_path.read_text(encoding="utf-8")) or {}
        ingredients_db: dict[str, Any] = db_data.get("ingredients", {})
        known_names: set[str] = set()
        for item in ingredients_db.values():
            if "name" in item:
                known_names.add(item["name"].strip().casefold())
            for alias in item.get("aliases", []):
                known_names.add(alias.strip().casefold())

        all_ingredients = list(recipe.ingredients)
        for variant in recipe.variants:
            all_ingredients.extend(variant.ingredients)

        missing_db = [item.name for item in all_ingredients if item.name.strip().casefold() not in known_names]
        if missing_db:
            errors.append(f"Ingrédients absents de .gram/ingredients.yaml : {', '.join(sorted(set(missing_db)))}")

        if prov_path.is_file():
            prov_data: dict[str, Any] = yaml.safe_load(prov_path.read_text(encoding="utf-8")) or {}
            prov_db: dict[str, Any] = prov_data.get("ingredients", {})
            missing_prov = [slug for slug in ingredients_db if slug not in prov_db]
            if missing_prov:
                errors.append(
                    f"Entrées manquantes dans .gram/ingredient-provenance.yaml : {', '.join(sorted(missing_prov))}"
                )

    # 4. Timers validation (scalar and non-empty)
    for step in recipe.steps:
        for timer in step.timers:
            seconds = timer.get("seconds", 0)
            if not isinstance(seconds, (int, float)) or seconds <= 0:
                errors.append(
                    f"Étape '{step.id}' : durée de minuteur invalide ou non positive ({timer.get('label', '')})"
                )

    # 5. Icon resolution check
    resolver = IngredientIconResolver(root)
    missing_icons: list[str] = []
    for item in recipe.ingredients:
        if not resolver.resolve(item.name, item.quantity):
            missing_icons.append(item.name)
    if missing_icons:
        errors.append(
            f"Icône introuvable (aucun SVG ni fallback catégoriel) pour : {', '.join(sorted(set(missing_icons)))}"
        )

    # 6. Image prompt check if image_generation is declared
    generation = recipe.metadata.get("image_generation")
    if generation and isinstance(generation, dict):
        prompt_path_str = generation.get("prompt_file")
        if prompt_path_str:
            prompt_file = root / prompt_path_str
            if not prompt_file.is_file():
                errors.append(f"Fichier de prompt d'image introuvable : '{prompt_file}'")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Contrôle atomique et ultra-rapide de conformité pour recettes CookiGram (.gram)."
    )
    parser.add_argument(
        "recipes",
        nargs="+",
        type=Path,
        help="Chemin(s) vers le ou les fichiers .gram à valider",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Racine du dépôt (par défaut détectée automatiquement)",
    )
    args = parser.parse_args(argv)

    total_files = len(args.recipes)
    failed_count = 0

    print(f"🔍 Validation CookiGram de {total_files} recette(s)...\n")

    for path in args.recipes:
        recipe_path = path.resolve()
        errors = check_recipe(recipe_path, root=args.root.resolve())
        if errors:
            failed_count += 1
            print(f"❌ {path} : NON CONFORME ({len(errors)} erreur(s))")
            for err in errors:
                print(f"   • {err}")
        else:
            try:
                rec = parse_recipe(recipe_path, validate=False, root=args.root.resolve())
                title = rec.title
                ing_count = len(rec.ingredients)
                prep = rec.metadata.get("prep_time", "?")
                tot = rec.metadata.get("total_time", "?")
                print(f"✅ {path} : CONFORME")
                print(
                    f"   « {title} » | {rec.portions} portions | Prep: {prep} | Total: {tot} | {ing_count} ingrédients"
                )
            except Exception:
                print(f"✅ {path} : CONFORME")

    print("\n" + ("=" * 50))
    if failed_count == 0:
        print(f"✨ Toutes les recettes ({total_files}) satisfont le contrat CookiGram !")
        return 0
    else:
        print(f"⚠️ {failed_count} recette(s) sur {total_files} présentent des erreurs de contrat.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
