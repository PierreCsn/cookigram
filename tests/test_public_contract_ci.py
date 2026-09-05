from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ci_does_not_use_the_old_yaml_fallback() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "safe_load" not in workflow
    assert "Contrôle YAML de secours" not in workflow
    assert "Contrat public non publié" in workflow


def test_public_contract_docs_describe_the_current_blocker() -> None:
    docs = (ROOT / "docs/PUBLIC-CONTRACT.md").read_text(encoding="utf-8")

    assert "cookigram-core/docs/CONTRACT.md" in docs
    assert "`1.0`" in docs
    assert "CORE_SSH_KEY" in docs
    assert "recette invalide" in docs
