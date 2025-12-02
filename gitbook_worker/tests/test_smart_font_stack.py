from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

import yaml

from gitbook_worker.tools.publishing import fonts_cli
from gitbook_worker.tools.publishing.smart_font_stack import prepare_runtime_font_loader


def _write_fonts_config(path: Path, fonts: Dict[str, Dict[str, object]]) -> Path:
    data = {"version": "1.0.0", "fonts": fonts}
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)
    return path


def test_prepare_runtime_font_loader_resolves_existing_files(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    fonts_dir = repo_root / ".github" / "fonts"
    fonts_dir.mkdir(parents=True)
    font_file = fonts_dir / "demo-font.ttf"
    font_file.write_bytes(b"font-data")

    config_path = _write_fonts_config(
        repo_root / "fonts.yml",
        {
            "EMOJI": {
                "name": "Demo Emoji",
                "paths": [".github/fonts/demo-font.ttf"],
                "license": "Test",
                "license_url": "https://example.com",
            }
        },
    )

    result = prepare_runtime_font_loader(
        config_path=config_path,
        repo_root=repo_root,
        extra_search_paths=[fonts_dir],
    )

    resolved_paths = result.loader.get_font_paths("EMOJI")
    assert len(resolved_paths) == 1
    assert Path(resolved_paths[0]) == font_file.resolve()
    assert result.downloads == 0


def test_prepare_runtime_font_loader_downloads_missing_font(tmp_path):
    repo_root = tmp_path / "repo2"
    repo_root.mkdir()

    source_font = tmp_path / "TwemojiMozilla.ttf"
    source_font.write_bytes(b"twemoji")
    checksum = hashlib.sha256(source_font.read_bytes()).hexdigest()

    config_path = _write_fonts_config(
        repo_root / "fonts.yml",
        {
            "EMOJI": {
                "name": "Twitter Color Emoji",
                "paths": [],
                "download_url": source_font.as_uri(),
                "license": "CC BY 4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "sha256": checksum,
            }
        },
    )

    cache_dir = tmp_path / "cache"
    result = prepare_runtime_font_loader(
        config_path=config_path,
        repo_root=repo_root,
        cache_dir=cache_dir,
    )

    resolved_paths = result.loader.get_font_paths("EMOJI")
    assert len(resolved_paths) == 1
    cached_font = Path(resolved_paths[0])
    assert cached_font.exists()
    assert cached_font.parent.parent == cache_dir.resolve()
    assert result.downloads == 1


def test_fonts_cli_sync(tmp_path):
    repo_root = tmp_path / "repo3"
    repo_root.mkdir()
    font_dir = repo_root / "fonts"
    font_dir.mkdir()
    font_file = font_dir / "cli-font.ttf"
    font_file.write_bytes(b"cli-font")

    config_path = _write_fonts_config(
        repo_root / "fonts.yml",
        {
            "SERIF": {
                "name": "CLI Serif",
                "paths": ["fonts/cli-font.ttf"],
                "license": "Test",
                "license_url": "https://example.com",
            }
        },
    )

    exit_code = fonts_cli.main(
        [
            "sync",
            "--config",
            str(config_path),
            "--repo-root",
            str(repo_root),
            "--search-path",
            str(font_dir),
        ]
    )

    assert exit_code == 0
