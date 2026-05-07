"""Deterministic bitmap markers for generated fallback coverage glyphs."""

from __future__ import annotations


def codepoint_marker_bitmap(char: str) -> list[str]:
    """Return a light 8x8 bitmap marker derived from the Unicode codepoint.

    The marker is intentionally deterministic and unique enough for coverage
    fonts, but it is not a handwritten type-design substitute. Handcrafted
    bitmaps in the script modules always take precedence.
    """

    codepoint = ord(char)
    mixed = codepoint ^ (codepoint << 7) ^ (codepoint << 17)
    mixed ^= codepoint * 0x45D9F3B
    cells = [["." for _ in range(8)] for _ in range(8)]

    # Open corner brackets make generated coverage glyphs recognizable without
    # resembling a filled missing-glyph box at PDF reading size.
    for row_index, column_index in (
        (0, 1),
        (0, 2),
        (1, 0),
        (2, 0),
        (5, 7),
        (6, 7),
        (7, 5),
        (7, 6),
    ):
        cells[row_index][column_index] = "#"

    for row_index in range(1, 7):
        shift = (row_index - 1) * 5
        column_index = 1 + (((mixed >> shift) & 0x7) % 6)
        cells[row_index][column_index] = "#"

        if (mixed >> (32 + row_index)) & 1:
            mirror_column = 7 - column_index
            if mirror_column != column_index:
                cells[row_index][mirror_column] = "#"

    cells[3][3] = "#"
    cells[4][4] = "#"

    return ["".join(row) for row in cells]
