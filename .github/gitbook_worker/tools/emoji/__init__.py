"""Emoji processing utilities for the ERDA workflow suite."""

from .emoji_utils import (
    EmojiRecord,
    emoji_cldr_name,
    emoji_to_display_codepoints,
    emoji_to_slug,
    iter_emoji_sequences,
    summarize_emojis,
)
from .inline_emojis import inline_file
from .report import emoji_report
from .scan_emojis import main as scan_emojis_main

__all__ = [
    "EmojiRecord",
    "emoji_cldr_name",
    "emoji_to_display_codepoints",
    "emoji_to_slug",
    "iter_emoji_sequences",
    "summarize_emojis",
    "inline_file",
    "emoji_report",
    "scan_emojis_main",
]
