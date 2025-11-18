"""Tests for the Markdown link audit command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from gitbook_worker.tools.quality import link_audit


def test_main_discovers_markdown_files_from_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    markdown_file = docs_dir / "sample.md"
    markdown_file.write_text("# Sample\n", encoding="utf-8")

    captured_md_files: List[Path] = []

    def fake_check_http_links(
        md_files: List[Path],
        report_csv: Path,
        *,
        timeout: float,
        show_progress: bool,
    ) -> tuple[list[object], list[object]]:
        captured_md_files.extend(md_files)
        return [], []

    monkeypatch.setattr(link_audit, "check_http_links", fake_check_http_links)

    exit_code = link_audit.main(
        [
            "--root",
            str(tmp_path),
            "--http-report",
            str(tmp_path / "report.csv"),
            "--format",
            "log",
        ]
    )

    assert exit_code == 0
    assert captured_md_files == [markdown_file]
