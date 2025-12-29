---
title: Appendix – Emoji & font coverage
description: Evidence of suitable fonts for all scripts and coloured emojis used in the sample content.
date: 2024-06-05
version: 1.0doc_type: appendix
appendix_id: "B"
category: "technical"history:
  - version: 1.0
    date: 2024-06-05
    changes: Initial version with font matrix and testing notes.
---

# Appendix – Emoji & font coverage

This overview summarises the fonts that cover all writing systems used in the sample texts as well as all emoji sets. All fonts meet the licensing requirements from `AGENTS.md` and the `LICENSE-FONTS` file.

## Font matrix

| Category | Font | Licence | Source | Coverage |
| --- | --- | --- | --- | --- |
| Serif/Sans/Mono | DejaVu Serif · DejaVu Sans · DejaVu Sans Mono (v2.37) | Bitstream Vera License + public-domain additions | `gitbook_worker/defaults/fonts.yml` · `publish/ATTRIBUTION.md` | Latin, Greek, Cyrillic, plus technical symbols for tables and code |
| CJK & additional BMP glyphs | ERDA CC-BY CJK | CC BY 4.0 **or** MIT | `.github/fonts/erda-ccby-cjk` · `LICENSE-FONTS` | Chinese, Japanese, Korean, plus additional Unicode blocks from the multilingual templates |
| Coloured emojis | Twemoji Color Font v15.1.0 | CC BY 4.0 | https://github.com/13rac1/twemoji-color-font/releases/tag/v15.1.0 · `publish/ATTRIBUTION.md` | All emoji categories including skin tones, ZWJ sequences and flags |

## Practical use

1. **Text sections** – The DejaVu family serves as the standard for body text (`SERIF`), UI elements (`SANS`) and code (`MONO`). This covers all European languages in `content/templates/multilingual-neutral-text.md`.
2. **CJK** – As soon as chapters or example pages use characters such as 日, 学 or 정보, the build system should embed the ERDA-CC-BY-CJK file from `.github/fonts/erda-ccby-cjk/true-type/`. This happens automatically via the `CJK` section in `gitbook_worker/defaults/fonts.yml`.
3. **Emoji colour** – The new emoji example pages use the Twemoji colour font. `gitbook_worker/defaults/fonts.yml` references the download URL so CI builds can fetch the TTF automatically.

## Testing notes

- Run `pytest -k emoji` to ensure the font scanning does not report unknown fonts.
- Check PDF exports with at least one page from each emoji category (smileys, nature, activities, objects) to test Twemoji alongside CJK text.
- Document any new fonts in `publish/ATTRIBUTION.md` and `LICENSE-FONTS` if additional writing systems are added.
