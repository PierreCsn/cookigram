import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("public_content_lint", ROOT / "scripts/lint-public-content.py")
LINTER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(LINTER)


class PublicContentLintTests(unittest.TestCase):
    def test_public_corpus_is_deterministically_clean_except_seo_advisories(self) -> None:
        result = LINTER.run(ROOT)
        self.assertEqual(result["files"], 162)
        self.assertEqual(result["summary"]["errors"], 0)
        self.assertGreater(result["summary"]["warnings"], 0)
        self.assertEqual(json.dumps(result, ensure_ascii=False), json.dumps(LINTER.run(ROOT), ensure_ascii=False))
        self.assertTrue(all(not item["path"].startswith("/") for item in result["issues"]))


    def test_duplicate_yaml_key_is_a_blocking_error(self) -> None:
        result = LINTER.run(ROOT / "tests/fixtures/public-content-lint/duplicate")
        self.assertEqual(result["summary"]["errors"], 1)
        self.assertEqual(result["issues"][0]["code"], "E003")


    def test_invalid_date_and_duplicate_tag_are_reported(self) -> None:
        result = LINTER.run(ROOT / "tests/fixtures/public-content-lint/invalid")
        codes = {item["code"] for item in result["issues"]}
        self.assertTrue({"E006", "E007"} <= codes)


if __name__ == "__main__":
    unittest.main()
