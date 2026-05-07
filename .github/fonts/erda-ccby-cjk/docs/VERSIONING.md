---
title: ERDA CC-BY font versioning
version: 1.3.0
date: 2026-05-07
history:
  - version: 1.3.0
    date: 2026-05-07
    description: Updates the current ERDA font-family version to 1.4.1.
  - version: 1.2.0
    date: 2026-05-07
    description: Updates the current ERDA font-family version to 1.4.0.
  - version: 1.1.0
    date: 2026-05-07
    description: Updates the current ERDA font-family version to 1.3.0.
  - version: 1.0.0
    date: 2026-05-07
    description: Documents the independent ERDA font-family version introduced for v1.2.0.
---

# ERDA CC-BY Font Versioning

The ERDA generated fallback fonts have their own semantic version that is
independent from the GitBook Worker package version. GitBook Worker may release
as `2.5.0`, while the bundled ERDA generated font family can release as
`1.4.1`.

## Current Font Version

| Font family | Current version | Scope |
|---|---:|---|
| `ERDA CC-BY CJK` | `1.4.1` | CJK, Kana, Hangul, full long-text section and shared fallback coverage |
| `ERDA CC-BY Indic` | `1.4.1` | Devanagari/Hindi fallback coverage |
| `ERDA CC-BY Ethiopic` | `1.4.1` | Ethiopic fallback coverage |

The version is defined once in `generator/font_version.py` as
`ERDA_FONT_VERSION`. The package-level `fonts.yml` entries mirror this value so
attribution, reproducibility checks and release notes can cite a stable font
version.

## OpenType Version String

Each generated TTF uses this name-table format:

```text
Version 1.4.1+YYYYMMDD.HHMMSS
```

The `1.4.1` part is the semantic font-family version. The timestamp is build
metadata used as a cache-busting component for Windows, LuaTeX, browser and PDF
reader font caches. The timestamp is not treated as a new semantic release by
itself.

## When To Bump

| Change | Version bump |
|---|---|
| New glyph coverage, new generated subfont, or materially expanded Unicode target | Minor |
| Fix to glyph shape, metrics, metadata, cache behavior, or docs-only correction | Patch |
| Rename family, remove supported coverage, change license, or break downstream configuration | Major |

## Release History

| Version | Date | Summary |
|---|---|---|
| `1.4.1` | 2026-05-07 | Raises generated marker ink to 0.90-cell for stronger PDF readability. |
| `1.4.0` | 2026-05-07 | Adds full long-text section CJK target coverage and increases marker ink contrast for PDF readability. |
| `1.3.0` | 2026-05-07 | Adds CJK long-sample block coverage targets and replaces filled generated markers with lighter open-corner markers. |
| `1.2.0` | 2026-05-07 | Staged 3000+ Han/Hangul coverage, full Kana targets, full Devanagari and Ethiopic supported block targets, and TTF stats gate. |
| `1.1.0` | 2025-11-08 | Added Devanagari/Hindi support and modular subfont work. |
| `1.0.0` | 2025-11-08 | First modular production generator baseline. |

## Verification

From `generator/`:

```powershell
python build_all.py
python font_cli.py stats --fail-on-targets
```

Expected v1.4.1 signals:

- every ERDA generated font reports a version beginning with `Version 1.4.1+`,
- `erda-ccby-cjk.ttf` passes Han, Hangul, Hiragana, Katakana, CJK long-sample block and complete long-text section targets,
- `erda-ccby-indic.ttf` passes Devanagari main and extended targets,
- `erda-ccby-ethiopic.ttf` passes Ethiopic main, supplement, extended,
  extended-A and extended-B targets.