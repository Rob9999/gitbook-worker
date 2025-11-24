from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.tools.utils.smart_content import ContentEntry, load_content_config


def test_load_content_config_uses_defaults_when_missing(tmp_path: Path) -> None:
    config = load_content_config(cwd=tmp_path, repo_root=tmp_path)
    assert config.default_id == "default"
    entry = config.get(None)
    assert entry.uri == "./"
    assert entry.is_local


def test_load_content_config_parses_yaml_styles(tmp_path: Path) -> None:
    content_file = tmp_path / "content.yaml"
    content_file.write_text(
        """
version: 1.0.0
default: en
contents:
  - id: de
    uri: de/
    description: German
  - en:
      uri: ./
      description: English
""",
        encoding="utf-8",
    )
    config = load_content_config(cwd=tmp_path, repo_root=tmp_path)
    assert config.default_id == "en"
    de_entry = config.get("de")
    assert de_entry.description == "German"
    assert de_entry.uri == "de/"
    en_entry = config.get(None)
    assert en_entry.id == "en"
    assert en_entry.uri == "./"


def test_content_entry_resolve_path(tmp_path: Path) -> None:
    entry = ContentEntry(id="de", uri="./books/de", type="local")
    resolved = entry.resolve_path(tmp_path)
    assert resolved == (tmp_path / "books" / "de").resolve()


def test_resolve_non_local_entry_raises(tmp_path: Path) -> None:
    entry = ContentEntry(id="remote", uri="git@example", type="git")
    with pytest.raises(ValueError):
        entry.resolve_path(tmp_path)
