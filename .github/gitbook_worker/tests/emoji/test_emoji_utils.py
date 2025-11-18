from tools.emoji import emoji_utils


def test_emoji_record_summary():
    records = emoji_utils.summarize_emojis(["🙂", "🙂", "🚀"])
    assert records[0].glyph == "🙂"
    assert records[0].count == 2
    assert records[0].asset_slug == "1f642"
    assert emoji_utils.emoji_to_display_codepoints("🚀") == "U+1F680"
    assert emoji_utils.emoji_cldr_name("🚀") == "rocket"
    assert emoji_utils.emoji_cldr_name("A") == "A"
