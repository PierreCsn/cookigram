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
    assert resolve_utensil_icon("Bol Thermomix") == "saladier"
    assert resolve_utensil_icon("Cul-de-poule") == "saladier"
    assert resolve_utensil_icon("Spatule") == "spatule"
    assert resolve_utensil_icon("Spatule en bois") == "spatule"
    assert resolve_utensil_icon("Maryse") == "spatule"
    assert resolve_utensil_icon("Planche à découper") == "planche"
    assert resolve_utensil_icon("Plat à gratin") == "plat-gratin"
    assert resolve_utensil_icon("Plat à rôtir ou plat à gratin profond") == "plat-gratin"
    assert resolve_utensil_icon("Plat de service") == "plat-gratin"
    assert resolve_utensil_icon("Thermomix TM6") == "thermomix"
    assert resolve_utensil_icon("Thermomix TM31, TM5, TM6 ou TM7") == "thermomix"
    assert resolve_utensil_icon("Robot cuiseur") == "thermomix"
    assert resolve_utensil_icon("Moule à charnière de 16 cm") == "moule"
    assert resolve_utensil_icon("Moule à flan allant au four") == "moule"
    assert resolve_utensil_icon("Panier cuisson") == "panier-vapeur"
    assert resolve_utensil_icon("Varoma avec plateau vapeur") == "panier-vapeur"
    assert resolve_utensil_icon("Économe") == "econome"
    assert resolve_utensil_icon("Épluche-légumes") == "econome"


def test_resolve_utensil_fallback_none():
    assert resolve_utensil_icon("Four") is None
    assert resolve_utensil_icon("Papier aluminium et papier sulfurisé") is None
    assert resolve_utensil_icon("") is None
    assert resolve_utensil_icon(None) is None  # type: ignore[arg-type]


def test_attach_utensil_icons():
    recipe = SimpleNamespace(
        metadata={
            "required_equipment": ["Couteau de chef", "Plat à gratin", "Four"],
        }
    )
    attach_utensil_icons(recipe)
    items = recipe.metadata["equipment_items"]
    assert len(items) == 3
    assert items[0] == {"name": "Couteau de chef", "icon": "couteau"}
    assert items[1] == {"name": "Plat à gratin", "icon": "plat-gratin"}
    assert items[2] == {"name": "Four", "icon": None}


def test_utensil_assets_exist():
    utensils_dir = Path("static/icons/utensils")
    assert utensils_dir.is_dir()
    for name in [
        "couteau",
        "casserole",
        "poele",
        "fouet",
        "saladier",
        "spatule",
        "planche",
        "plat-gratin",
        "thermomix",
        "moule",
        "panier-vapeur",
        "econome",
    ]:
        assert (utensils_dir / f"{name}.webp").is_file(), f"Missing {name}.webp"
        assert (utensils_dir / f"{name}.png").is_file(), f"Missing {name}.png"
