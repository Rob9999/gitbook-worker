import logging
from pathlib import Path

import pytest

from gitbook_worker.tools.workflow_orchestrator.orchestrator import (
    DockerSettings,
    OrchestratorConfig,
    OrchestratorProfile,
    STEP_HANDLERS,
    run,
    validate_manifest,
)


@pytest.fixture()
def manifest_file(tmp_path: Path) -> Path:
    manifest = tmp_path / "publish.yml"
    manifest.write_text(
        """
version: 0.1.0
profiles:
  default:
    steps:
      - publisher
""",
        encoding="utf-8",
    )
    return manifest


def test_validate_manifest_accepts_known_steps(manifest_file: Path):
    ok, errors = validate_manifest(
        root=manifest_file.parent,
        manifest=manifest_file,
        profile="default",
        all_profiles=False,
        repo_visibility="auto",
        repository=None,
    )

    assert ok
    assert errors == []


def test_validate_manifest_flags_unknown_steps(manifest_file: Path):
    manifest_file.write_text(
        """
version: 0.1.0
profiles:
  default:
    steps:
      - unknown-step
""",
        encoding="utf-8",
    )

    ok, errors = validate_manifest(
        root=manifest_file.parent,
        manifest=manifest_file,
        profile="default",
        all_profiles=False,
        repo_visibility="auto",
        repository=None,
    )

    assert not ok
    assert any("unknown-step" in err for err in errors)


def test_run_logs_failure_analytics(monkeypatch, caplog, manifest_file: Path):
    failing_step = "__failing_step__"

    def _fail(_ctx):
        raise RuntimeError("boom")

    caplog.set_level(logging.ERROR)
    monkeypatch.setitem(STEP_HANDLERS, failing_step, _fail)
    docker_settings = DockerSettings(use_registry=False, image=None, cache=False)
    profile = OrchestratorProfile(
        name="default",
        steps=(failing_step,),
        docker=docker_settings,
    )
    config = OrchestratorConfig(
        root=manifest_file.parent,
        manifest=manifest_file,
        profile=profile,
        repo_visibility="public",
        repository=None,
        commit=None,
        base=None,
        reset_others=False,
        publisher_args=(),
        dry_run=False,
    )

    with pytest.raises(RuntimeError):
        run(config)

    analytics_logs = [rec.message for rec in caplog.records if "analytics" in rec.message]
    assert analytics_logs, "expected analytics log entry when step fails"

    STEP_HANDLERS.pop(failing_step, None)
