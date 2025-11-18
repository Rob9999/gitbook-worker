import sys

from tools.emoji import scan_emojis


def test_collect_and_render(tmp_path):
    md_one = tmp_path / "chapter.md"
    md_one.write_text("Willkommen 🙂🚀", encoding="utf-8")
    md_two = tmp_path / "appendix.md"
    md_two.write_text("Fallback ⚙ und 🙂", encoding="utf-8")

    files = [md_one, md_two]
    per_file = scan_emojis.collect_emojis(files)
    records = scan_emojis.build_records(per_file)

    assert any(record.glyph == "🙂" for record in records)
    totals = sum(record.count for record in records)
    assert totals == 4

    table = scan_emojis.render_inventory_table(records)
    assert "CLDR-Name" in table
    assert "🙂" in table

    samples = scan_emojis.pick_samples(records, limit=2)
    assert len(samples) == 2
    assert samples[0] == "🙂"


def test_render_inventory_table_empty():
    table = scan_emojis.render_inventory_table([])
    assert "(keine)" in table
    assert "0" in table


def test_discover_and_report(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    file_path = nested / "chapter.md"
    file_path.write_text("Emoji 🙂🙂", encoding="utf-8")

    files = scan_emojis.discover_markdown_files([str(tmp_path)])
    assert file_path in files

    per_file = scan_emojis.collect_emojis(files)
    records = scan_emojis.build_records(per_file)
    report = scan_emojis.build_report(records, per_file, files)
    assert report["totals"]["unique"] >= 1
    assert report["emojis"][0]["files"][0]["path"].endswith("chapter.md")


def test_pick_samples_default():
    samples = scan_emojis.pick_samples([], limit=3)
    assert samples == ["🙂", "🚀", "⚙"]


def test_scan_emojis_main(tmp_path, monkeypatch):
    md_file = tmp_path / "doc.md"
    md_file.write_text("Hallo 🙂", encoding="utf-8")
    output = tmp_path / "report.json"
    samples = tmp_path / "samples.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scan_emojis.py",
            "--sources",
            str(tmp_path),
            "--output",
            str(output),
            "--samples-output",
            str(samples),
        ],
    )
    scan_emojis.main()
    assert output.exists() and samples.exists()
