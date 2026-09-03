from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from generator.seo import build_recipe_meta_description, is_thermomix_compatible

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def render_template():
    """Jinja renderer configured like generator.build, so templates that rely
    on the SEO globals (e.g. recipe_meta_description) can be rendered directly
    in unit tests without re-implementing the global registration."""

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(),
    )
    env.globals["recipe_meta_description"] = build_recipe_meta_description
    env.globals["is_thermomix_compatible"] = is_thermomix_compatible

    def _render(template_name: str, **kwargs: Any) -> str:
        kwargs.setdefault("related_recipes", [])
        return env.get_template(template_name).render(**kwargs)

    return _render
