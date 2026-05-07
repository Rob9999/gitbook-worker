"""Deterministic bitmap markers for generated fallback coverage glyphs."""

from __future__ import annotations


def codepoint_marker_bitmap(char: str) -> list[str]:
    """Return an 8x8 bitmap marker derived from the Unicode codepoint.

    The marker is intentionally deterministic and unique enough for coverage
    fonts, but it is not a handwritten type-design substitute. Handcrafted
    bitmaps in the script modules always take precedence.
    """

    codepoint = ord(char)
    mixed = codepoint ^ (codepoint << 7) ^ (codepoint << 17)
    mixed ^= codepoint * 0x45D9F3B
    rows: list[str] = []

    for row_index in range(8):
        if row_index in (0, 7):
            rows.append("########")
            continue

        cells = ["#", ".", ".", ".", ".", ".", ".", "#"]
        for column_index in range(1, 7):
            bit_index = (row_index - 1) * 6 + (column_index - 1)
            cells[column_index] = "#" if (mixed >> bit_index) & 1 else "."

        if row_index == 3:
            cells[3] = "#"
        if row_index == 4:
            cells[4] = "#"

        rows.append("".join(cells))

    return rows
