---
title: ERDA font coverage matrix
version: 1.0.0
date: 2026-05-07
history:
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