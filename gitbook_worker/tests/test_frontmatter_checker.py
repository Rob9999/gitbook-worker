from pathlib import Path

from gitbook_worker.tools.validators.frontmatter_checker import (
    check_file,
    check_frontmatter_tree,
    FRONTMATTER_EXIT_CODE,
)


def test_frontmatter_valid(tmp_path: Path) -> None:
    path = tmp_path / "good.md"
    path.write_text(
        """---
title: Ok
version: 1.0
doc_type: example
---
Body
""",
        encoding="utf-8",
    )

    assert check_file(path) == []


def test_frontmatter_invalid_line(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text(
        """---
version: 1.0doc_type: example
---
""",
        encoding="utf-8",
    )

    issues = check_file(path)
    assert len(issues) == 1
    issue = issues[0]
    assert issue.path == path
    assert issue.line >= 2
    assert "mapping values" in issue.message


def test_frontmatter_tree_skips_publish(tmp_path: Path) -> None:
    publish_dir = tmp_path / "publish"
    publish_dir.mkdir()
    (publish_dir / "skip.md").write_text(
        "---\nversion: 1.0doc_type: example\n---\n", encoding="utf-8"
    )

    valid = tmp_path / "ok.md"
    valid.write_text("---\ntitle: ok\n---\n", encoding="utf-8")

    assert check_frontmatter_tree(tmp_path) == []


def test_frontmatter_tree_collects_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("---\nversion: 1.0doc_type: example\n---\n", encoding="utf-8")

    issues = check_frontmatter_tree(tmp_path)
    assert len(issues) == 1
    assert issues[0].path == bad


__all__ = ["FRONTMATTER_EXIT_CODE"]
