from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.tools.publishing import pipeline


@pytest.fixture()
def publish_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "publish.yml"
    manifest.write_text(
        """
publish:
    - name: default
project:
    license: CC BY-SA 4.0
""",
        encoding="utf-8",
    )
    return manifest


def test_resolve_options_defaults(
    monkeypatch: pytest.MonkeyPatch, publish_manifest: Path
) -> None:
    monkeypatch.chdir(publish_manifest.parent)
    args = pipeline.parse_args([])
    options = pipeline._resolve_options(args)
    assert options.root == publish_manifest.parent.resolve()
    assert options.manifest == publish_manifest.resolve()
    assert options.language_id == "default"


def test_preflight_requires_project_license(tmp_path: Path) -> None:
    manifest = tmp_path / "publish.yml"
    manifest.write_text("publish: []\n", encoding="utf-8")
    args = pipeline.parse_args(["--root", str(tmp_path), "--manifest", str(manifest)])
    with pytest.raises(pipeline.CommandError):
        pipeline._resolve_options(args)


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
        run_frontmatter_check=False,
        publisher_args=(),
        dry_run=False,
        language_id="default",
        language_env={
            "GITBOOK_CONTENT_ID": "default",
            "GITBOOK_CONTENT_ROOT": str(publish_manifest.parent),
        },
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
        run_frontmatter_check=False,
        publisher_args=(),
        dry_run=True,
        language_id="default",
        language_env={
            "GITBOOK_CONTENT_ID": "default",
            "GITBOOK_CONTENT_ROOT": str(publish_manifest.parent),
        },
    )
    pipeline.run_pipeline(options)


def test_parse_publisher_args() -> None:
    args = pipeline.parse_args(
        [
            "--publisher-args=--keep-combined",
            "--publisher-args=--paper-format=a4",
            "--publisher-args=--landscape",
        ]
    )
    assert args.publisher_args == (
        "--keep-combined",
        "--paper-format=a4",
        "--landscape",
    )


# --- _should_skip_rename tests ---


class TestShouldSkipRename:
    """Tests for the _should_skip_rename() auto-detect / explicit key logic."""

    def test_explicit_false_skips_rename(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\ngitbook_rename: false\n"
            "project:\n  license: MIT\npublish:\n  - path: ./a.md\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is True

    def test_explicit_true_keeps_rename(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\ngitbook_rename: true\n"
            "project:\n  license: MIT\npublish:\n  - path: ./a.md\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is False

    def test_auto_detect_all_file_entries(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\nproject:\n  license: MIT\n"
            "publish:\n"
            "  - path: ./a.md\n    source_type: file\n"
            "  - path: ./b.md\n    source_type: file\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is True

    def test_mixed_entries_no_skip(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\nproject:\n  license: MIT\n"
            "publish:\n"
            "  - path: ./a.md\n    source_type: file\n"
            "  - path: ./content\n    source_type: folder\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is False

    def test_no_source_type_no_skip(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\nproject:\n  license: MIT\n"
            "publish:\n  - path: ./content\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is False

    def test_empty_publish_no_skip(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\nproject:\n  license: MIT\npublish: []\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is False

    def test_explicit_overrides_auto_detect(self, tmp_path: Path) -> None:
        """Explicit gitbook_rename: true should keep rename even with all file entries."""
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            "version: 0.1.1\ngitbook_rename: true\n"
            "project:\n  license: MIT\n"
            "publish:\n  - path: ./a.md\n    source_type: file\n",
            encoding="utf-8",
        )
        assert pipeline._should_skip_rename(manifest) is False
