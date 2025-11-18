from tools.emoji import report


def test_emoji_report_counts(tmp_path):
    md = tmp_path / "file.md"
    md.write_text("Hello 😊 world 🚀", encoding="utf-8")
    counts, table = report.emoji_report(md)

    assert counts.get("Emoticons") == 1
    assert counts.get("Transport and Map Symbols") == 1
    assert "| Unicode Block |" in table
    assert "Transport and Map Symbols" in table


def test_render_table_for_empty_counts():
    table = report.render_table({})
    assert "(keine)" in table
