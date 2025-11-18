from __future__ import annotations

from pathlib import Path

import pytest

from tools.utils import smart_manage_publish_flags as spf


def test_get_entry_type_prefers_source_type():
    entry = {"source_type": "FOLDER", "type": "file"}
    assert spf.get_entry_type(entry) == "folder"


def test_resolve_entry_path_for_root_manifest(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "chapters").mkdir()

    resolved = spf.resolve_entry_path("chapters", str(repo_root), str(repo_root))
    assert resolved == "chapters"


def test_resolve_entry_path_for_nested_manifest(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    manifest_dir = repo_root / "docs" / "public"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "chapters").mkdir()

    resolved = spf.resolve_entry_path("chapters", str(manifest_dir), str(repo_root))
    assert resolved == "docs/public/chapters"


@pytest.mark.parametrize(
    "entry_type, entry_path, changed",  # noqa: E231 - compact parametrisation
    [
        ("folder", "chapters", "chapters/intro.md"),
        ("file", "README.md", "README.md"),
    ],
)
def test_is_match_handles_relative_paths(
    entry_type: str, entry_path: str, changed: str
):
    # Function renamed to is_path_match in smart module
    assert spf.is_path_match(entry_path, entry_type, changed) is True


def test_git_changed_files_falls_back_when_base_missing(monkeypatch):
    """Test that git_changed_files from smart_git handles fallbacks."""
    from tools.utils import smart_git

    calls: list[list[str]] = []

    def fake_run_git(cmd: list[str]) -> tuple[int, str, str]:
        calls.append(cmd)
        if "diff" in cmd and "--name-only" in cmd:
            # Simulate failed diff command
            return (128, "", "fatal: bad revision 'base'")
        # Fallback to diff-tree
        if "diff-tree" in cmd:
            return (0, "docs/example.md\n", "")
        return (0, "", "")

    monkeypatch.setattr(smart_git, "run_git_command", fake_run_git)

    # Use smart_git.get_changed_files directly (this is what spf uses internally)
    files = smart_git.get_changed_files("commit", base="base")

    assert files == ["docs/example.md"]
    assert len(calls) >= 2  # Should have tried diff and fallen back to diff-tree
