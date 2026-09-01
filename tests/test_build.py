import json
from pathlib import Path

from generator.build import build


def test_build_generates_complete_static_site(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    assert (output_dir / "index.html").is_file()
    assert (output_dir / "sw.js").is_file()
    assert (output_dir / ".nojekyll").is_file()
    assert (output_dir / "manifest.webmanifest").is_file()
    assert (output_dir / "recipes.json").is_file()

    # Verify recipes.json structure
    recipes_data = json.loads((output_dir / "recipes.json").read_text(encoding="utf-8"))
    assert len(recipes_data) >= 3
    slugs = {r["slug"] for r in recipes_data}
    assert "risotto-poulet-champignons" in slugs
    assert "curry-poulet-noix-coco" in slugs

    # Verify recipe and cook page existence
    risotto_dir = output_dir / "recipes" / "risotto-poulet-champignons"
    assert (risotto_dir / "index.html").is_file()
    assert (risotto_dir / "cook" / "index.html").is_file()

    # Re-run build to verify clean overwrite
    build(output_dir)
    assert (output_dir / "index.html").is_file()
