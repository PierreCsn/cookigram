#!/usr/bin/env python3
"""Find recipe illustrations that are still stranded behind a placeholder.

The audit deliberately lives in the content repository so it also works when
the private CookiGram engine is unavailable (for example on fork pull
requests).  ``--check`` is intended for CI and exits non-zero for every
actionable image/prompt mismatch.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


PLACEHOLDER = "images/placeholder-recipe.jpg"


@dataclass(frozen=True)
class Finding:
    recipe: str
    image: str
    prompt_file: str
    status: str
    message: str


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    _, _, body = text.partition("\n")
    frontmatter, separator, _ = body.partition("\n---")
    if not separator:
        return {}
    data = yaml.safe_load(frontmatter) or {}
    return data if isinstance(data, dict) else {}


def audit(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    recipes_dir = root / "recipes"

    for recipe_path in sorted(recipes_dir.glob("*.gram")):
        metadata = _frontmatter(recipe_path)
        generation = metadata.get("image_generation")
        if not isinstance(generation, dict):
            continue

        prompt = generation.get("prompt_file")
        if not isinstance(prompt, str) or not prompt.strip():
            continue

        image = metadata.get("image")
        image = image.strip() if isinstance(image, str) else ""
        prompt_path = root / prompt
        image_path = root / "static" / image if image else None

        if image == PLACEHOLDER:
            findings.append(
                Finding(
                    recipe=recipe_path.relative_to(root).as_posix(),
                    image=image,
                    prompt_file=prompt,
                    status="placeholder",
                    message="prompt présent mais image encore sur le placeholder",
                )
            )
        elif image_path is None or not image_path.is_file():
            findings.append(
                Finding(
                    recipe=recipe_path.relative_to(root).as_posix(),
                    image=image,
                    prompt_file=prompt,
                    status="missing-image",
                    message="prompt présent mais fichier image introuvable",
                )
            )

        if not prompt_path.is_file():
            findings.append(
                Finding(
                    recipe=recipe_path.relative_to(root).as_posix(),
                    image=image,
                    prompt_file=prompt,
                    status="missing-prompt",
                    message="fichier de prompt introuvable",
                )
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="racine du dépôt (défaut: répertoire courant)")
    parser.add_argument("--json", action="store_true", help="produire un inventaire JSON")
    parser.add_argument("--check", action="store_true", help="échouer si un cas à traiter est détecté")
    args = parser.parse_args(argv)

    try:
        findings = audit(args.root.resolve())
    except (OSError, yaml.YAMLError) as exc:
        print(f"Erreur pendant l'audit des images : {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"{item.status}: {item.recipe} — {item.message} ({item.image or 'image non déclarée'})")
        print(f"{len(findings)} anomalie(s) d'image détectée(s).", file=sys.stderr)
    else:
        print("Aucune recette avec prompt stranded détectée.")

    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
