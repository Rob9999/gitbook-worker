---
title: ERDA CC-BY coverage matrix
version: 1.3.0
date: 2026-05-07
history:
  - version: 1.3.0
    date: 2026-05-07
    description: Updates current stats wording for v1.4.1 0.90 marker ink.
  - version: 1.2.0
    date: 2026-05-07
    description: Adds v1.4.0 full long-text section target and stronger marker contrast.
  - version: 1.1.0
    date: 2026-05-07
    description: Adds v1.3.0 long-sample block target and marker quality boundary.
  - version: 1.0.0
    date: 2026-05-07
    description: Captures the v1.2.0 generated TTF coverage matrix.
---

# ERDA CC-BY Coverage Matrix

This matrix documents the real TTF coverage targets for ERDA generated fallback
font version `1.4.1`. It is intentionally based on `fontTools.ttLib.TTFont`
statistics from the finished `.ttf` files, not on sample text length.

## Version 1.4.1 Targets

| Font | Required target | v1.4.1 measured result |
|---|---:|---:|
| `erda-ccby-cjk.ttf` | >= 3000 CJK Unified Ideographs | 3242 |
| `erda-ccby-cjk.ttf` | >= 3000 Hangul syllables | 3130 |
| `erda-ccby-cjk.ttf` | all assigned Hiragana in U+3040-U+309F | 93/93 |
| `erda-ccby-cjk.ttf` | all assigned Katakana in U+30A0-U+30FF | 96/96 |
| `erda-ccby-cjk.ttf` | all CJK-family codepoints in ZH-Hant/JA/KO long sample blocks | 141/141 |
| `erda-ccby-cjk.ttf` | all CJK-family codepoints in the complete long-text section | 308/308 |
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
| `erda-ccby-cjk.ttf` | `1.4.1` | 6937 | 6936 |
| `erda-ccby-indic.ttf` | `1.4.1` | 162 | 161 |
| `erda-ccby-ethiopic.ttf` | `1.4.1` | 525 | 524 |

## Quality Boundary

The generated marker glyphs are licensed, visible fallback glyphs. They are not
a substitute for a professionally designed CJK, Indic or Ethiopic text typeface.
Since v1.4.1, generated markers must stay sparse and avoid filled black-box
contours that can be mistaken for missing-glyph rectangles, while using 0.90-cell
ink to remain readable in the PDF long-text checks.
Handcrafted bitmaps still take precedence, and future full-quality work should
cover glyph design, metrics, shaping, hinting and layout regression gates.