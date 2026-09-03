import json
import re
import shutil
from pathlib import Path

from generator.build import build, compute_asset_version


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
    assert (output_dir / "assets" / "icons" / "ingredients" / "ail.svg").is_file()

    recipe_html = (risotto_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="ingredient-icon ingredient-icon--standard"' in recipe_html
    assert "icons/ingredients/" in recipe_html

    # Re-run build to verify clean overwrite
    build(output_dir)
    assert (output_dir / "index.html").is_file()


def test_image_change_bumps_service_worker_version(tmp_path: Path):
    assets = tmp_path / "assets"
    shutil.copytree("static", assets)
    (assets / "sw.js").unlink()

    before = compute_asset_version(assets)
    image = assets / "images" / "curry-poulet-noix-coco.jpg"
    image.write_bytes(image.read_bytes() + b"changed")

    assert compute_asset_version(assets) != before


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


def test_compile_css_assembles_modular_stylesheets(tmp_path: Path):
    from generator.build import compile_css

    css_dir = tmp_path / "css"
    css_dir.mkdir()
    (css_dir / "variables.css").write_text(":root { --test-var: 1; }")
    (css_dir / "base.css").write_text("body { margin: 0; }")

    out_file = tmp_path / "bundled.css"
    compile_css(css_dir, out_file)

    content = out_file.read_text(encoding="utf-8")
    assert "/* === variables.css === */" in content
    assert "--test-var: 1" in content
    assert "/* === base.css === */" in content
    assert "body { margin: 0; }" in content


def test_compile_css_folds_root_component_stylesheets_into_bundle(tmp_path: Path):
    from generator.build import compile_css

    css_dir = tmp_path / "css"
    css_dir.mkdir()
    (css_dir / "variables.css").write_text(":root { --test-var: 1; }")
    (tmp_path / "scaling.css").write_text(".portion-picker { display: grid; }")
    (tmp_path / "variants.css").write_text(".variant-picker { margin: 26px 0; }")
    (tmp_path / "images.css").write_text(".plate img { object-fit: cover; }")

    out_file = tmp_path / "bundled.css"
    compile_css(css_dir, out_file)

    content = out_file.read_text(encoding="utf-8")
    assert "/* === variables.css === */" in content
    assert "/* === scaling.css === */" in content
    assert ".portion-picker" in content
    assert "/* === variants.css === */" in content
    assert "/* === images.css === */" in content
    assert ".plate img" in content


def test_single_css_bundle_no_separate_root_stylesheets(tmp_path: Path):
    output_dir = tmp_path / "_site"
    build(output_dir)

    index = (output_dir / "index.html").read_text(encoding="utf-8")
    recipe = (output_dir / "recipes" / "curry-poulet-noix-coco" / "index.html").read_text(encoding="utf-8")
    cook = (output_dir / "recipes" / "curry-poulet-noix-coco" / "cook" / "index.html").read_text(encoding="utf-8")

    for html in (index, recipe, cook):
        assert html.count('rel="stylesheet"') == 1
        assert "assets/app.css" in html
        assert "scaling.css" not in html
        assert "variants.css" not in html
        assert "images.css" not in html

    # The separate stylesheets are no longer emitted in the build output.
    assert not (output_dir / "assets" / "scaling.css").exists()
    assert not (output_dir / "assets" / "variants.css").exists()
    assert not (output_dir / "assets" / "images.css").exists()

    # Component rules are actually present in the single compiled bundle.
    app_css = (output_dir / "assets" / "app.css").read_text(encoding="utf-8")
    assert ".portion-picker" in app_css
    assert ".variant-picker" in app_css
    assert ".plate img" in app_css
