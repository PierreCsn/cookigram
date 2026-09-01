from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def apply_plugins(recipe, plugin_dir: Path) -> None:
    """Apply build-time enrichers without modifying the source recipe."""
    for path in sorted(plugin_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        spec = spec_from_file_location(f"cookgram_plugin_{path.stem}", path)
        if not spec or not spec.loader:
            continue
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "enrich"):
            module.enrich(recipe)

