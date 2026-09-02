import json
import re
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


def test_build_precaches_existing_assets(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    sw = (output_dir / "sw.js").read_text(encoding="utf-8")
    precache_match = re.search(r"const PRECACHE = (\[.*?]);", sw, re.DOTALL)
    assert precache_match, "the generated service worker should contain its precache manifest"
    urls = json.loads(precache_match.group(1))
    assert urls, "the service worker should precache at least the home page"

    for url in urls:
        relative = url.removeprefix("./").split("?")[0]
        target = output_dir if not relative else output_dir / relative
        assert target.exists(), f"precache URL '{url}' does not exist in the build"

    assert "./recipes/curry-poulet-noix-coco/" in urls
    assert "./recipes/curry-poulet-noix-coco/cook/" in urls
    assert "./assets/images/curry-poulet-noix-coco.jpg" in urls
    assert "./recipes.json" in urls
    assert any(url.startswith("./assets/app.js?v=") for url in urls)


def test_service_worker_uses_network_first_for_html(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    sw = (output_dir / "sw.js").read_text(encoding="utf-8")
    assert "event.request.mode === 'navigate'" in sw
    assert "networkFirst(event.request)" in sw
    assert "ignoreSearch: true" in sw
    assert "__PRECACHE__" not in sw


def test_build_versions_assets_consistently(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    sw = (output_dir / "sw.js").read_text(encoding="utf-8")
    version_match = re.search(r"cookigram-([0-9a-f]{12})", sw)
    assert version_match, "sw.js should reference the generated asset version"
    version = version_match.group(1)
    assert "__VERSION__" not in sw, "sw.js template placeholder was not substituted"

    index = (output_dir / "index.html").read_text(encoding="utf-8")
    recipe = (output_dir / "recipes" / "curry-poulet-noix-coco" / "index.html").read_text(encoding="utf-8")
    cook = (output_dir / "recipes" / "curry-poulet-noix-coco" / "cook" / "index.html").read_text(encoding="utf-8")

    for html in (index, recipe, cook):
        assert f"assets/app.css?v={version}" in html
        assert f"assets/app.js?v={version}" in html
        assert "assets/app.css?v=23" not in html
