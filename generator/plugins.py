"""Build-time plugin management for CookiGram recipes.

Allows recipes and variants to be enriched during the build without modifying
the canonical .gram source files. Plugins are loaded once per build session
instead of repeatedly reloading disk modules for every recipe.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Protocol


class RecipeEnricher(Protocol):
    """Formal protocol that recipe plugins should implement."""

    def enrich(self, recipe: Any) -> None:
        """Enrich recipe steps, metadata, or plugins dictionary in place."""
        ...


@dataclass(frozen=True)
class Plugin:
    """Registered recipe plugin instance."""

    name: str
    path: Path
    enrich: Callable[[Any], None]


class PluginManager:
    """Loads plugins once from disk and applies them across a recipe collection."""

    def __init__(self, plugins: list[Plugin] | None = None) -> None:
        self.plugins: list[Plugin] = list(plugins or [])

    @classmethod
    def from_directory(cls, plugin_dir: Path) -> PluginManager:
        """Discovers and imports all valid Python plugin modules in plugin_dir."""
        plugins: list[Plugin] = []
        if not plugin_dir.exists():
            return cls(plugins)

        for path in sorted(plugin_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            spec = spec_from_file_location(f"cookigram_plugin_{path.stem}", path)
            if not spec or not spec.loader:
                continue
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "enrich") and callable(module.enrich):
                plugins.append(Plugin(name=path.stem, path=path, enrich=module.enrich))

        return cls(plugins)

    def apply(self, recipe: Any) -> None:
        """Applies all registered plugins to a recipe and its variants."""
        for plugin in self.plugins:
            plugin.enrich(recipe)
            for variant in getattr(recipe, "variants", []):
                plugin.enrich(variant)


def apply_plugins(recipe: Any, plugin_dir: Path) -> None:
    """Backwards-compatible standalone function for single-recipe enrichment."""
    manager = PluginManager.from_directory(plugin_dir)
    manager.apply(recipe)
