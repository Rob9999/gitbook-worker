from __future__ import annotations

import json

from tools.publishing.gitbook_style import (
    ensure_clean_summary,
    get_summary_layout,
    rename_to_gitbook_style,
)


def test_rename_to_gitbook_style(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (root / "My File.txt").write_text("content", encoding="utf-8")
    nested = root / "Sub Dir"
    nested.mkdir()
    (nested / "Another File.MD").write_text("data", encoding="utf-8")
    (nested / "ignore.py").write_text("print('hi')", encoding="utf-8")

    rename_to_gitbook_style(root, use_git=False)

    assert not (root / "My File.txt").exists()
    assert (root / "my-file.txt").read_text(encoding="utf-8") == "content"
    assert (root / "sub-dir").is_dir()
    assert (root / "sub-dir" / "another-file.md").read_text(encoding="utf-8") == "data"
    # Python files should not be renamed.
    assert (root / "sub-dir" / "ignore.py").exists()


def test_ensure_clean_summary(tmp_path):
    base = tmp_path / "book"
    base.mkdir()
    (base / "README.md").write_text("# Root Title", encoding="utf-8")
    section = base / "Section One"
    section.mkdir()
    (section / "README.md").write_text("# Section Intro", encoding="utf-8")
    (section / "Topic.md").write_text("# Topic Title", encoding="utf-8")

    summary_path = base / "summary.md"
    summary_path.write_text("outdated", encoding="utf-8")

    changed = ensure_clean_summary(base, run_git=False)
    assert changed is True

    expected = "\n".join(
        [
            "# Summary",
            "",
            "* [Root Title](README.md)",
            "* [Section Intro](Section One/README.md)",
            "  * [Topic Title](Section One/Topic.md)",
            "",
        ]
    )

    assert summary_path.read_text(encoding="utf-8") == expected

    # Second invocation should be idempotent.
    assert ensure_clean_summary(base, run_git=False) is False


def test_get_summary_layout_resolves_uppercase(tmp_path):
    base = tmp_path / "book"
    base.mkdir()
    (base / "book.json").write_text(
        json.dumps(
            {
                "title": "Demo",
                "root": ".",
                "structure": {"summary": "SUMMARY.md"},
            }
        ),
        encoding="utf-8",
    )
    (base / "SUMMARY.md").write_text("", encoding="utf-8")

    layout = get_summary_layout(base)
    assert layout.summary_path == (base / "SUMMARY.md").resolve()
    assert layout.root_dir == base.resolve()


def test_summary_flattens_directories_without_readme(tmp_path):
    base = tmp_path / "docs"
    base.mkdir()
    (base / "README.md").write_text("# Root", encoding="utf-8")
    readme_dir = base / "readme"
    readme_dir.mkdir()
    (readme_dir / "vorwort.md").write_text("# Vorwort", encoding="utf-8")

    summary_path = get_summary_layout(base).summary_path
    ensure_clean_summary(base, run_git=False)

    expected_lines = [
        "# Summary",
        "",
        "* [Root](README.md)",
        "  * [Vorwort](readme/vorwort.md)",
        "",
    ]
    assert summary_path.read_text(encoding="utf-8") == "\n".join(expected_lines)


def test_gitbook_mode_uses_natural_sorting(tmp_path):
    base = tmp_path / "docs"
    base.mkdir()
    (base / "README.md").write_text("# Start", encoding="utf-8")

    chapter_dir = base / "2.3-post-demokratische-zivilisation"
    chapter_dir.mkdir()
    (chapter_dir / "README.md").write_text("# 2.3 Kapitel", encoding="utf-8")
    (chapter_dir / "2.3.1-dystopie.md").write_text("# 2.3.1 Dystopie", encoding="utf-8")

    (base / "2.4-schluss.md").write_text("# 2.4 Schluss", encoding="utf-8")
    (base / "2.10-anhang.md").write_text("# 2.10 Anhang", encoding="utf-8")

    summary_path = get_summary_layout(base).summary_path
    ensure_clean_summary(base, run_git=False)

    content = summary_path.read_text(encoding="utf-8").splitlines()
    assert content[2] == "* [Start](README.md)"
    assert content[3] == "* [2.3 Kapitel](2.3-post-demokratische-zivilisation/README.md)"
    # Child entry should stay beneath its parent and maintain indentation
    assert content[4] == "  * [2.3.1 Dystopie](2.3-post-demokratische-zivilisation/2.3.1-dystopie.md)"
    # Natural sorting keeps 2.4 before 2.10
    assert content[5] == "* [2.4 Schluss](2.4-schluss.md)"
    assert content[6] == "* [2.10 Anhang](2.10-anhang.md)"


def test_manifest_reorders_entries(tmp_path):
    base = tmp_path / "docs"
    base.mkdir()
    (base / "README.md").write_text("# Root", encoding="utf-8")
    (base / "alpha.md").write_text("# Alpha", encoding="utf-8")
    (base / "beta.md").write_text("# Beta", encoding="utf-8")

    manifest_path = tmp_path / "order.yaml"
    manifest_path.write_text("- beta.md\n- alpha.md\n", encoding="utf-8")

    summary_path = get_summary_layout(base).summary_path
    ensure_clean_summary(
        base,
        run_git=False,
        summary_mode="manifest",
        summary_order_manifest=manifest_path,
    )

    lines = summary_path.read_text(encoding="utf-8").splitlines()
    assert lines[2] == "* [Root](README.md)"
    assert lines[3] == "* [Beta](beta.md)"
    assert lines[4] == "* [Alpha](alpha.md)"
