from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.tools.quality import profile_link_audit, staatenprofil_links


class _Response:
    status_code = 404
    reason = "Not Found"


def test_iter_profile_files_uses_configurable_filename_patterns(tmp_path: Path) -> None:
    profile = tmp_path / "country-profile.md"
    state_profile = tmp_path / "staatenprofil-de.md"
    other = tmp_path / "chapter.md"
    for path in (profile, state_profile, other):
        path.write_text("# Title\n", encoding="utf-8")

    assert list(profile_link_audit.iter_profile_files(tmp_path)) == [profile]
    assert list(
        profile_link_audit.iter_profile_files(
            tmp_path, filename_patterns=("*staatenprofil*.md",)
        )
    ) == [state_profile]


def test_profile_link_audit_writes_broken_http_report(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = tmp_path / "country-profile.md"
    markdown.write_text("[Broken](https://example.invalid/missing)\n", encoding="utf-8")
    output = tmp_path / "report.csv"

    monkeypatch.setattr(
        profile_link_audit.requests, "head", lambda *args, **kwargs: _Response()
    )

    exit_code = profile_link_audit.main(
        ["--root", str(tmp_path), "--output", str(output)]
    )

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "country-profile.md" in report
    assert "404" in report


def test_staatenprofil_links_keeps_legacy_pattern(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_profile = tmp_path / "staatenprofil-de.md"
    state_profile.write_text(
        "[Broken](https://example.invalid/missing)\n", encoding="utf-8"
    )
    output = tmp_path / "legacy.csv"

    monkeypatch.setattr(
        profile_link_audit.requests, "head", lambda *args, **kwargs: _Response()
    )

    exit_code = staatenprofil_links.main(
        ["--root", str(tmp_path), "--output", str(output)]
    )

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "staatenprofil-de.md" in report
    assert "404" in report
