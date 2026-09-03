from pathlib import Path


def test_pages_deployment_waits_for_successful_ci():
    workflow = Path(".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "workflow_run:" in workflow
    assert "workflows: [CI]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'" in workflow
    assert "ref: ${{ github.event_name == 'workflow_dispatch' && github.sha || github.event.workflow_run.head_sha }}" in workflow
