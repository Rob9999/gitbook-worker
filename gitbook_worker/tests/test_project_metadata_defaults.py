from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gitbook_worker.tools.publishing import publisher


def _write_manifest(base: Path, data: dict) -> Path:
    manifest = base / "publish.yml"
    manifest.write_text(yaml.safe_dump(data), encoding="utf-8")
    return manifest


def test_project_metadata_fails_without_license_by_default(tmp_path: Path) -> None:
    manifest = _write_manifest(
        tmp_path,
        {
            "version": "0.1.0",
            "publish": [],
        },
    )

    with pytest.raises(publisher.ProjectMetadataError):
        publisher._resolve_project_metadata(manifest)


def test_project_metadata_warn_policy_allows_placeholder(tmp_path: Path) -> None:
    manifest = _write_manifest(
        tmp_path,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"attribution_policy": "warn"},
        },
    )

    meta = publisher._resolve_project_metadata(manifest)

    assert meta.license == "<MISSING project.license>"
    assert any("project.license" in message for message in meta.warnings)


def test_project_metadata_prefers_manifest_over_book_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = _write_manifest(
        repo,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"name": "Manifest Title", "license": "CC BY 4.0"},
        },
    )
    (repo / "book.json").write_text(
        json.dumps({"title": "Book Title", "author": ["Alice"], "license": "CC0-1.0"}),
        encoding="utf-8",
    )

    meta = publisher._resolve_project_metadata(manifest)

    assert meta.name == "Manifest Title"
    assert meta.authors == ("Alice",)
    assert meta.license == "CC BY 4.0"


def test_project_metadata_date_prefers_manifest_over_book_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = _write_manifest(
        repo,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"license": "CC BY 4.0", "date": "2026-01-08"},
        },
    )
    (repo / "book.json").write_text(
        json.dumps({"title": "Book", "author": ["Alice"], "date": "2024-01-01"}),
        encoding="utf-8",
    )

    meta = publisher._resolve_project_metadata(manifest)

    assert meta.date == "2026-01-08"


def test_project_metadata_date_uses_book_json_when_manifest_missing(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = _write_manifest(
        repo,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"license": "CC BY 4.0"},
        },
    )
    (repo / "book.json").write_text(
        json.dumps({"title": "Book", "author": ["Alice"], "date": "2024-06-01"}),
        encoding="utf-8",
    )

    meta = publisher._resolve_project_metadata(manifest)

    assert meta.date == "2024-06-01"


def test_project_metadata_date_rejects_invalid_value(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = _write_manifest(
        repo,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"license": "CC BY 4.0", "date": "2026-13-40"},
        },
    )

    with pytest.raises(publisher.ProjectMetadataError):
        publisher._resolve_project_metadata(manifest)


def test_project_metadata_uses_repo_placeholders(tmp_path: Path) -> None:
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    manifest = _write_manifest(
        repo,
        {
            "version": "0.1.0",
            "publish": [],
            "project": {"license": "CC BY 4.0", "attribution_policy": "warn"},
        },
    )

    meta = publisher._resolve_project_metadata(manifest, repository="example/owner")

    assert "demo-repo" in meta.name
    assert "repo owner 'example'" in " ".join(meta.authors)
    assert any("project.name" in message for message in meta.warnings)


def test_project_metadata_to_pandoc_metadata() -> None:
    meta = publisher.ProjectMetadata(
        name="Project",
        authors=("Alice",),
        license="CC BY 4.0",
        date="2026-01-08",
        policy="fail",
        warnings=(),
    )

    metadata = meta.as_pandoc_metadata(title_override="Custom Title")

    assert metadata["title"] == ["Custom Title"]
    assert metadata["author"] == ["Alice"]
    assert metadata["rights"] == ["CC BY 4.0"]
    assert metadata["date"] == ["2026-01-08"]
