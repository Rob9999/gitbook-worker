---
title: ERDA CC-BY coverage matrix
version: 1.0.0
date: 2026-05-07
history:
  - version: 1.0.0
    date: 2026-05-07
    description: Captures the v1.2.0 generated TTF coverage matrix.
---

# ERDA CC-BY Coverage Matrix

This matrix documents the real TTF coverage targets for ERDA generated fallback
font version `1.2.0`. It is intentionally based on `fontTools.ttLib.TTFont`
statistics from the finished `.ttf` files, not on sample text length.

## Version 1.2.0 Targets

| Font | Required target | v1.2.0 measured result |
|---|---:|---:|
| `erda-ccby-cjk.ttf` | >= 3000 CJK Unified Ideographs | 3156 |
| `erda-ccby-cjk.ttf` | >= 3000 Hangul syllables | 3103 |
| `erda-ccby-cjk.ttf` | all assigned Hiragana in U+3040-U+309F | 93/93 |
| `erda-ccby-cjk.ttf` | all assigned Katakana in U+30A0-U+30FF | 96/96 |
| `erda-ccby-indic.ttf` | all assigned Devanagari main codepoints | 128/128 |
| `erda-ccby-indic.ttf` | all assigned Devanagari Extended codepoints | 32/32 |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic main codepoints | 358/358 |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic supplement codepoints | 26/26 |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic extended codepoints | 79/79 |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic extended-A codepoints | 32/32 |
| `erda-ccby-ethiopic.ttf` | all assigned Ethiopic extended-B codepoints | 28/28 |

## Current TTF Stats

| Font | ERDA font version | maxp.numGlyphs | cmap codepoints |
|---|---|---:|---:|
| `erda-ccby-cjk.ttf` | `1.2.0` | 6824 | 6823 |
| `erda-ccby-indic.ttf` | `1.2.0` | 162 | 161 |
| `erda-ccby-ethiopic.ttf` | `1.2.0` | 525 | 524 |

## Quality Boundary

The generated marker glyphs are licensed, visible fallback glyphs. They are not
a substitute for a professionally designed CJK, Indic or Ethiopic text typeface.
Handcrafted bitmaps still take precedence, and future full-quality work should
cover glyph design, metrics, shaping, hinting and layout regression gates.