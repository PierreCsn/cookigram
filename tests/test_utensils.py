from generator.utensils import resolve_utensil_icon


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
