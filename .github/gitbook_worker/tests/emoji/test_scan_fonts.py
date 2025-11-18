import sys

from tools.emoji import scan_fonts


def test_collect_fonts(tmp_path):
    css_file = tmp_path / "styles.css"
    css_file.write_text(
        "body { font-family: 'DejaVu Serif', serif; }\n"
        "code { font-family: 'DejaVu Sans Mono'; }",
        encoding="utf-8",
    )

    files = [css_file]
    usage = scan_fonts.collect_fonts(files)
    assert "DejaVu Serif" in usage
    assert usage["DejaVu Serif"][str(css_file)] == 1

    report = scan_fonts.build_report(usage, files)
    assert any(entry["font"] == "DejaVu Serif" for entry in report["fonts"])


def test_discover_files_and_normalize(tmp_path):
    css_dir = tmp_path / "css"
    css_dir.mkdir()
    css_file = css_dir / "style.css"
    css_file.write_text("body{font-family:\n 'Source Serif', serif;}", encoding="utf-8")
    md_file = tmp_path / "note.md"
    md_file.write_text("`code`", encoding="utf-8")

    files = scan_fonts.discover_files([str(tmp_path)], [".css", ".md"])
    assert css_file in files and md_file in files
    families = scan_fonts.normalize_family("'Source Serif', serif")
    assert families[0] == "Source Serif"


def test_scan_fonts_main(tmp_path, monkeypatch):
    css_file = tmp_path / "style.css"
    css_file.write_text("body{font-family:'Test Font';}", encoding="utf-8")
    output = tmp_path / "fonts.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scan_fonts.py",
            "--sources",
            str(tmp_path),
            "--extensions",
            ".css",
            "--output",
            str(output),
        ],
    )
    scan_fonts.main()
    assert output.exists()
