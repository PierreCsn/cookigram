from pathlib import Path

from generator.gram import parse_recipe
from generator.plugins import apply_plugins
from plugins.thermomix import parse_thermomix_settings


def test_parse_thermomix_settings():
    # Vitesse cuillère + sens inverse + température + durée
    res = parse_thermomix_settings(
        "Cuire 10 min à 100 C, sens inverse, vitesse mijotage avec le gobelet",
        [{"label": "10 min", "seconds": 600}],
        ["100°C"],
    )
    assert res is not None
    assert res["time"] == "10 min"
    assert res["temp"] == "100°C"
    assert res["reverse"] is True
    assert res["speed"] == "cuillère"
    assert res["speed_type"] == "spoon"

    # Varoma + vitesse 4
    res2 = parse_thermomix_settings(
        "Cuire 20 min en mode Varoma, vitesse 4",
        [{"label": "20 min", "seconds": 1200}],
        [],
    )
    assert res2 is not None
    assert res2["temp"] == "Varoma"
    assert res2["speed"] == "4"
    assert res2["speed_type"] == "blade"
    assert res2["reverse"] is False


def test_thermomix_badges_rendered_in_templates(render_template):
    risotto = parse_recipe(Path("recipes/risotto-poulet-champignons.gram"))
    apply_plugins(risotto, Path("plugins"))

    rendered_recipe = render_template("recipe.html", recipe=risotto)
    rendered_cook = render_template("cook.html", recipe=risotto)

    # Check presence of Cookomix-style badges and SVG icons
    assert "tmx-badge" in rendered_recipe
    assert "tmx-badge" in rendered_cook
    assert "tmx-spoon" in rendered_recipe
    assert "tmx-blade" in rendered_recipe
    assert "tmx-reverse" in rendered_recipe
    assert "Sens inverse" in rendered_recipe
    assert "Vit. cuillère" in rendered_recipe
