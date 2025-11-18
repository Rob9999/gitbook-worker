"""Tests for the appendix layout inspector support tool."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.support.appendix_layout_inspector import inspect_appendix_layout


@pytest.fixture
def book_root(tmp_path: Path) -> Path:
    root = tmp_path / "book"
    root.mkdir()
    (root / "book.json").write_text('{"root": "."}\n', encoding="utf-8")
    (root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")

    def write_markdown(name: str, title: str) -> None:
        (root / name).write_text(f"# {title}\n", encoding="utf-8")

    write_markdown("README.md", "Overview")
    write_markdown("chapter-one.md", "Chapter One")
    write_markdown("appendix-a.md", "Appendix A")
    write_markdown("appendix-b.md", "Appendix B")
    return root


def test_appendices_move_to_end_when_enabled(book_root: Path) -> None:
    report = inspect_appendix_layout(book_root, appendices_last=True)

    assert report.top_level_titles == [
        "Overview",
        "Chapter One",
        "Appendix A",
        "Appendix B",
    ]
    assert report.appendix_titles == ["Appendix A", "Appendix B"]
    assert report.summary_path == book_root / "SUMMARY.md"


def test_appendices_follow_alphabetical_order_when_disabled(book_root: Path) -> None:
    report = inspect_appendix_layout(book_root, appendices_last=False)

    # Without appendix-last the filesystem ordering places appendices before
    # non-appendix markdown files (alphabetical file names).
    assert report.top_level_titles == [
        "Overview",
        "Appendix A",
        "Appendix B",
        "Chapter One",
    ]
    assert report.appendix_titles == ["Appendix A", "Appendix B"]
