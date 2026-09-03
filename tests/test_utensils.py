from pathlib import Path
from types import SimpleNamespace

from generator.utensils import attach_utensil_icons, resolve_utensil_icon


def test_resolve_utensil_icon_standard():
    assert resolve_utensil_icon("Couteau") == "couteau"
    assert resolve_utensil_icon("Couteau de chef") == "couteau"
    assert resolve_utensil_icon("Casserole") == "casserole"
    assert resolve_utensil_icon("Grande casserole") == "casserole"
    assert resolve_utensil_icon("Faitout") == "casserole"
    assert resolve_utensil_icon("Poêle") == "poele"
    assert resolve_utensil_icon("Grande poêle") == "poele"
    assert resolve_utensil_icon("Sauteuse") == "poele"
    assert resolve_utensil_icon("Fouet") == "fouet"
    assert resolve_utensil_icon("Fouet de cuisine") == "fouet"
    assert resolve_utensil_icon("Saladier") == "saladier"
    assert resolve_utensil_icon("Grand saladier") == "saladier"
    assert resolve_utensil_icon("Cul-de-poule") == "saladier"
    assert resolve_utensil_icon("Spatule") == "spatule"
    assert resolve_utensil_icon("Spatule en bois") == "spatule"
    assert resolve_utensil_icon("Maryse") == "spatule"


def test_resolve_utensil_fallback_none():
    assert resolve_utensil_icon("Thermomix TM6") is None
    assert resolve_utensil_icon("Plat à gratin") is None
    assert resolve_utensil_icon("Four") is None
    assert resolve_utensil_icon("") is None
    assert resolve_utensil_icon(None) is None  # type: ignore[arg-type]


def test_attach_utensil_icons():
    recipe = SimpleNamespace(
        metadata={
            "required_equipment": ["Couteau de chef", "Plat à gratin", "Grande poêle"],
        }
    )
    attach_utensil_icons(recipe)
    items = recipe.metadata["equipment_items"]
    assert len(items) == 3
    assert items[0] == {"name": "Couteau de chef", "icon": "couteau"}
    assert items[1] == {"name": "Plat à gratin", "icon": None}
    assert items[2] == {"name": "Grande poêle", "icon": "poele"}


def test_utensil_assets_exist():
    utensils_dir = Path("static/icons/utensils")
    assert utensils_dir.is_dir()
    for name in ["couteau", "casserole", "poele", "fouet", "saladier", "spatule"]:
        assert (utensils_dir / f"{name}.webp").is_file(), f"Missing {name}.webp"
        assert (utensils_dir / f"{name}.png").is_file(), f"Missing {name}.png"
