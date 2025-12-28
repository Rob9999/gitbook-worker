from __future__ import annotations

from pathlib import Path

from gitbook_worker.tools.utils.asset_copy import copy_assets_to_temp


def test_copy_gitbook_assets_directory(tmp_path: Path):
    project = tmp_path / "project"
    assets_dir = project / ".gitbook" / "assets"
    assets_dir.mkdir(parents=True)
    src = assets_dir / "img.png"
    src.write_bytes(b"data")

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    tmp_md = work_dir / "tmp.md"
    tmp_md.write_text("placeholder", encoding="utf-8")

    copy_assets_to_temp(tmp_md, project, [{"path": ".gitbook/assets"}])

    copied = work_dir / ".gitbook" / "assets" / "img.png"
    assert copied.exists()
    assert copied.read_bytes() == b"data"


def test_copy_single_content_file(tmp_path: Path):
    project = tmp_path / "project"
    content_dir = project / "content"
    content_dir.mkdir(parents=True)
    src = content_dir / "figure" / "pic.jpg"
    src.parent.mkdir(parents=True)
    src.write_bytes(b"bin")

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    tmp_md = work_dir / "tmp.md"
    tmp_md.write_text("placeholder", encoding="utf-8")

    copy_assets_to_temp(tmp_md, project, [{"path": src}])

    copied = work_dir / "figure" / "pic.jpg"
    assert copied.exists()
    assert copied.read_bytes() == b"bin"
