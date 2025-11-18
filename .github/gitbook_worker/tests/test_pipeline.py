from __future__ import annotations

from pathlib import Path

import pytest

from tools.publishing import pipeline


@pytest.fixture()
def publish_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "publish.yml"
    manifest.write_text("publish: []\n", encoding="utf-8")
    return manifest


def test_resolve_options_defaults(monkeypatch: pytest.MonkeyPatch, publish_manifest: Path) -> None:
    monkeypatch.chdir(publish_manifest.parent)
    args = pipeline.parse_args([])
    options = pipeline._resolve_options(args)
    assert options.root == publish_manifest.parent.resolve()
    assert options.manifest == publish_manifest.resolve()


def test_run_pipeline_executes_all_steps(
    monkeypatch: pytest.MonkeyPatch, publish_manifest: Path
) -> None:
    calls: list[str] = []

    def fake_set(opts: pipeline.PipelineOptions) -> None:
        calls.append("set")
        assert opts.manifest == publish_manifest.resolve()

    def fake_gitbook(opts: pipeline.PipelineOptions) -> None:
        calls.append("gitbook")

    def fake_publish(opts: pipeline.PipelineOptions) -> None:
        calls.append("publisher")

    monkeypatch.setattr(pipeline, "_run_set_publish_flag", fake_set)
    monkeypatch.setattr(pipeline, "_run_gitbook_steps", fake_gitbook)
    monkeypatch.setattr(pipeline, "_run_publisher", fake_publish)

    options = pipeline.PipelineOptions(
        root=publish_manifest.parent,
        manifest=publish_manifest.resolve(),
        commit="abc",
        base="def",
        reset_others=False,
        run_set_flag=True,
        run_gitbook_rename=True,
        run_gitbook_summary=True,
        run_publisher=True,
        gitbook_use_git=True,
        publisher_args=(),
        dry_run=False,
    )
    pipeline.run_pipeline(options)
    assert calls == ["set", "gitbook", "publisher"]


def test_pipeline_dry_run_skips_steps(
    monkeypatch: pytest.MonkeyPatch, publish_manifest: Path
) -> None:
    def fail(*_: object, **__: object) -> None:  # pragma: no cover - should not run
        raise AssertionError("Step should not execute during dry run")

    monkeypatch.setattr(pipeline, "_run_set_publish_flag", fail)
    monkeypatch.setattr(pipeline, "_run_gitbook_steps", fail)
    monkeypatch.setattr(pipeline, "_run_publisher", fail)

    options = pipeline.PipelineOptions(
        root=publish_manifest.parent,
        manifest=publish_manifest.resolve(),
        commit=None,
        base=None,
        reset_others=False,
        run_set_flag=True,
        run_gitbook_rename=True,
        run_gitbook_summary=True,
        run_publisher=True,
        gitbook_use_git=True,
        publisher_args=(),
        dry_run=True,
    )
    pipeline.run_pipeline(options)


def test_parse_publisher_args() -> None:
    args = pipeline.parse_args([
        "--publisher-args=--keep-combined",
        "--publisher-args=--paper-format=a4",
        "--publisher-args=--landscape",
    ])
    assert args.publisher_args == (
        "--keep-combined",
        "--paper-format=a4",
        "--landscape",
    )
