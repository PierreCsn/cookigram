#!/usr/bin/env python3
"""Deterministic, dependency-light linter for CookiGram public recipe metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATE_KEYS = {"date", "created_at", "updated_at", "generated_at"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$")
REQUIRED = {"title": str, "description": str, "tags": list}


class DuplicateKeyError(yaml.YAMLError):
    def __init__(self, key: Any, line: int):
        super().__init__(f"duplicate key {key!r}")
        self.key = key
        self.line = line


class NoDuplicateLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mappings instead of silently overwriting."""


def _mapping(loader: NoDuplicateLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise DuplicateKeyError(key, key_node.start_mark.line + 1)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


NoDuplicateLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping
)


def issue(path: Path, line: int | None, code: str, level: str, message: str) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "line": line,
        "code": code,
        "level": level,
        "message": message,
    }


def frontmatter(path: Path) -> tuple[str | None, int | None, list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, [issue(path, 1, "E001", "error", "frontmatter YAML absent")]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, None, [issue(path, 1, "E001", "error", "frontmatter YAML non fermé")]
    return "\n".join(lines[1:end]), 2, []


def is_date_key(key: str) -> bool:
    lower = key.lower()
    return lower in DATE_KEYS or lower.endswith("_date") or lower.endswith("_at")


def lint_recipe(path: Path) -> list[dict[str, Any]]:
    raw, start_line, problems = frontmatter(path)
    if raw is None:
        return problems
    try:
        data = yaml.load(raw, Loader=NoDuplicateLoader)
    except DuplicateKeyError as exc:
        return [issue(path, (start_line or 1) + exc.line - 1, "E003", "error", str(exc))]
    except yaml.YAMLError as exc:
        return [issue(path, start_line, "E002", "error", f"YAML invalide: {exc.__class__.__name__}")]
    if not isinstance(data, dict):
        return [issue(path, start_line, "E004", "error", "frontmatter YAML doit être un mapping")]

    found: list[dict[str, Any]] = []
    for key, expected in REQUIRED.items():
        value = data.get(key)
        if key not in data or value is None or (isinstance(value, str) and not value.strip()):
            found.append(issue(path, start_line, "E004", "error", f"champ requis absent ou vide: {key}"))
        elif not isinstance(value, expected):
            found.append(issue(path, start_line, "E005", "error", f"type invalide pour {key}: attendu {expected.__name__}"))

    title = data.get("title")
    if isinstance(title, str) and not 30 <= len(title.strip()) <= 60:
        found.append(issue(path, start_line, "W001", "warning", "title hors de la plage SEO indicative 30–60 caractères"))
    description = data.get("description")
    if isinstance(description, str) and not 70 <= len(description.strip()) <= 160:
        found.append(issue(path, start_line, "W002", "warning", "description hors de la plage SEO indicative 70–160 caractères"))

    tags = data.get("tags")
    if isinstance(tags, list):
        if not tags:
            found.append(issue(path, start_line, "E006", "error", "tags ne doit pas être vide"))
        if any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            found.append(issue(path, start_line, "E006", "error", "tags doit contenir uniquement des chaînes non vides"))
        normalized = [tag.casefold().strip() for tag in tags if isinstance(tag, str)]
        if len(normalized) != len(set(normalized)):
            found.append(issue(path, start_line, "E006", "error", "tags contient un doublon"))

    def dates(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                dates(child_value, str(child_key))
        elif isinstance(value, list):
            for child_value in value:
                dates(child_value, key)
        elif is_date_key(key):
            if not isinstance(value, str) or not ISO_DATE.fullmatch(value) or _invalid_iso(value):
                found.append(issue(path, start_line, "E007", "error", f"date non ISO 8601 pour {key}"))

    dates(data)
    return found


def _invalid_iso(value: str) -> bool:
    try:
        dt.date.fromisoformat(value[:10])
        if "T" in value or " " in value:
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return False
    except ValueError:
        return True


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = sorted(root.glob("recipes/*.gram"))
    problems = [problem for path in files for problem in lint_recipe(path)]
    for problem in problems:
        problem["path"] = Path(problem["path"]).resolve().relative_to(root).as_posix()
    errors = sum(problem["level"] == "error" for problem in problems)
    warnings = sum(problem["level"] == "warning" for problem in problems)
    return {
        "version": "1",
        "tool": "cookigram-public-content-lint",
        "root": ".",
        "files": len(files),
        "summary": {"errors": errors, "warnings": warnings, "status": "fail" if errors else "pass"},
        "issues": problems,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="racine du dépôt (défaut: dépôt courant du script)")
    parser.add_argument("--mode", choices=("warning", "blocking"), default="warning", help="warning: code 0; blocking: code 1 si une erreur est trouvée")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    result = run(args.root.resolve())
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{result['summary']['status']}: {result['summary']['errors']} erreur(s), {result['summary']['warnings']} avertissement(s)")
        for item in result["issues"]:
            location = f"{item['path']}:{item['line']}" if item["line"] else item["path"]
            print(f"{location}: {item['code']} [{item['level']}] {item['message']}")
    return 1 if args.mode == "blocking" and result["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
