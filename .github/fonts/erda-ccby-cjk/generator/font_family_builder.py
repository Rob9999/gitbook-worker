"""Shared bitmap font builder for ERDA CC BY family fonts."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.O_S_2f_2 import Panose

from character_index import CharacterInfo, get_character_index
from config import get_config
from font_logger import FontBuildLogger

CONFIG = get_config()
EM = CONFIG.grid.em
PIXELS = CONFIG.grid.pixels
CELL = CONFIG.grid.cell
MARGIN = CONFIG.grid.margin


def _draw_rect(pen: TTGlyphPen, x: int, y: int, w: int, h: int) -> None:
    pen.moveTo((x, y))
    pen.lineTo((x + w, y))
    pen.lineTo((x + w, y + h))
    pen.lineTo((x, y + h))
    pen.closePath()


def glyph_from_bitmap(bitmap: List[str]) -> Tuple[object, int]:
    pen = TTGlyphPen(None)
    rows = len(bitmap)
    cols = len(bitmap[0]) if rows else 0
    for row_index, row in enumerate(bitmap):
        for col_index, bit in enumerate(row):
            if bit != "#":
                continue
            x = MARGIN + col_index * CELL
            y = MARGIN + (rows - 1 - row_index) * CELL
            _draw_rect(pen, x, y, CELL, CELL)
    glyph = pen.glyph()
    width = (cols + 2) * CELL
    return glyph, width


def build_bitmap_font(
    font_family: str,
    output: Path,
    required_chars: Iterable[str],
    info_lookup: Callable[[str], CharacterInfo | None],
    logger: FontBuildLogger,
) -> None:
    glyph_order = [".notdef", "space"]
    glyphs: Dict[str, object] = {}
    advance_widths: Dict[str, Tuple[int, int]] = {}
    cmap: Dict[int, str] = {32: "space"}

    notdef_glyph, notdef_width = glyph_from_bitmap(["########"] * PIXELS)
    glyphs[".notdef"] = notdef_glyph
    advance_widths[".notdef"] = (notdef_width, 0)

    space_glyph, space_width = glyph_from_bitmap(["........"] * PIXELS)
    glyphs["space"] = space_glyph
    advance_widths["space"] = (space_width, 0)

    for char in required_chars:
        info = info_lookup(char)
        if info is None:
            logger.track_missing(char)
            continue
        glyph, width = glyph_from_bitmap(info.bitmap)
        name = f"uni{ord(char):04X}"
        glyph_order.append(name)
        glyphs[name] = glyph
        advance_widths[name] = (width, 0)
        cmap[ord(char)] = name
        logger.track_character(char, info.source)

    fb = FontBuilder(EM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(advance_widths)
    fb.setupHorizontalHeader(ascent=PIXELS * CELL, descent=-PIXELS * CELL)
    fb.setupOS2(
        sTypoAscender=PIXELS * CELL,
        sTypoDescender=-PIXELS * CELL,
        usWinAscent=PIXELS * CELL,
        usWinDescent=PIXELS * CELL,
        panose=Panose(bFamilyType=2, bSerifStyle=11, bProportion=9),
    )
    fb.setupNameTable(
        {
            "familyName": font_family,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"{font_family}-Regular",
            "fullName": f"{font_family} Regular",
            "psName": f"{font_family.replace(' ', '')}-Regular",
            "designer": "Robert Alexander Massinger",
            "designerURL": "https://github.com/rob9999/gitbook-worker",
            "copyright": "Copyright (c) 2025-2026 Robert Alexander Massinger, Munich, Bavaria, Germany.",
            "version": "Version 1.0",
            "manufacturer": "ERDA",
        }
    )
    fb.setupPost()
    fb.setupMaxp()

    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(output))
    logger.log_build_complete(str(output), output.stat().st_size)


def resolve_bitmap(char: str) -> CharacterInfo | None:
    index = get_character_index()
    return index.lookup(char)
