---
title: ERDA font coverage matrix
version: 1.1.0
date: 2026-05-10
history:
  - version: 1.1.0
    date: 2026-05-10
    description: Adds v2.10.0 ERDA Emoji, per-script baseline and erda-ccby-fonts rename direction.
  - version: 1.0.0
    date: 2026-05-07
    description: Documents the v2.5.0 staged coverage targets and TTF statistics workflow.
---

# ERDA Font Coverage Matrix

This page defines the release-target distinction between sample text length and
real TTF glyph coverage. The long language samples may contain 3000 or more
script characters per language, but that does not imply 3000 unique glyphs in a
font file.

## v2.5.0 Targets

| Font | Target | Rationale |
|---|---:|---|
| `erda-ccby-cjk.ttf` | >= 3000 CJK Unified Ideographs | Staged Han fallback coverage for Chinese and Japanese Han/Kanji text. |
| `erda-ccby-cjk.ttf` | >= 3000 Hangul syllables | Staged Korean fallback coverage using the existing algorithmic Hangul generator. |
| `erda-ccby-cjk.ttf` | all assigned Hiragana and Katakana in the standard blocks | Japanese kana coverage is finite and should be complete. |
| `erda-ccby-indic.ttf` | all assigned Devanagari main and Devanagari Extended codepoints | The supported Indic slice is Devanagari/Hindi; these Unicode blocks contain fewer than 3000 assigned codepoints. |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic main, supplement, extended, extended-A and extended-B codepoints | Ethiopic Unicode coverage is finite and contains fewer than 3000 assigned codepoints. |

## Quality Boundary

The v2.5.0 coverage expansion is a fallback-font hardening step. Handcrafted
bitmap glyphs remain the highest-quality source and always take precedence.
When no handcrafted bitmap exists, the generator creates deterministic
codepoint-marker glyphs so LuaLaTeX can embed a visible, licensed ERDA glyph
instead of producing missing glyph boxes.

These marker glyphs are intentionally not represented as a full-quality CJK,
Indic or Ethiopic typeface. A future full text-quality font would still need
proper glyph design, metrics, hinting, kerning, shaping validation and wider
linebreaking regression coverage.

## v2.5.0 Build Statistics

The rebuilt v2.5.0 TTF artifacts report these values through
`font_cli.py stats --fail-on-targets`:

| Font | maxp.numGlyphs | cmap codepoints | Release status |
|---|---:|---:|---|
| `erda-ccby-cjk.ttf` | 6824 | 6823 | PASS: 3156 Han, 3103 Hangul, 93 Hiragana, 96 Katakana |
| `erda-ccby-indic.ttf` | 162 | 161 | PASS: 128 Devanagari main, 32 Devanagari Extended |
| `erda-ccby-ethiopic.ttf` | 525 | 524 | PASS: 358 main, 26 supplement, 79 extended, 32 extended-A, 28 extended-B |

## Verification Commands

From `.github/fonts/erda-ccby-cjk/generator`:

```powershell
python build_all.py
python font_cli.py stats --fail-on-targets
```

From the repository root:

```powershell
C:/gitbook-worker/.venv/Scripts/python.exe -m pytest gitbook_worker/tests/test_erda_font_coverage_stats.py
```

The `stats` command reads the finished TTF files with `fontTools.ttLib.TTFont`
and reports `maxp.numGlyphs`, glyph-order length, mapped Unicode codepoints,
per-range counts and release-target pass/fail status.

## v2.10.0 Direction

The font family is no longer only a CJK fallback. The historical
`.github/fonts/erda-ccby-cjk/` path should be migrated to
`.github/fonts/erda-ccby-fonts/` in a dedicated compatibility-aware rename.

Policy boundary:

- DejaVu remains the configured primary Latin/mono family.
- Every additional project font and emoji font must be CC BY 4.0 licensed.
- Noto fonts are explicitly forbidden for fallback coverage.

Planned v2.10.0 expansion:

| Font family area | Target |
|---|---|
| ERDA Emoji | Customer-required emoji coverage missing from Twemoji Mozilla, with CC BY 4.0 provenance and LuaLaTeX embedding proof. |
| ERDA per-script baselines | Up to 5000 glyphs per script where useful; complete assigned block coverage for smaller declared script scopes. |
| ERDA CJK/Indic/Ethiopic | Keep existing validated targets and move paths only during the explicit rename step. |

ERDA Emoji must not appear in `fonts.yml` until a real font artifact exists and
has passed PDF embedding, attribution and editorial-quality validation.
