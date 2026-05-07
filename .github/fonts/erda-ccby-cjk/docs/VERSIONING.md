---
title: ERDA CC-BY font versioning
version: 1.0.0
date: 2026-05-07
history:
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
`1.3.0`.

## Current Font Version

| Font family | Current version | Scope |
|---|---:|---|
| `ERDA CC-BY CJK` | `1.3.0` | CJK, Kana, Hangul, CJK long-sample blocks and shared fallback coverage |
| `ERDA CC-BY Indic` | `1.3.0` | Devanagari/Hindi fallback coverage |
| `ERDA CC-BY Ethiopic` | `1.3.0` | Ethiopic fallback coverage |

The version is defined once in `generator/font_version.py` as
`ERDA_FONT_VERSION`. The package-level `fonts.yml` entries mirror this value so
attribution, reproducibility checks and release notes can cite a stable font
version.

## OpenType Version String

Each generated TTF uses this name-table format:

```text
Version 1.3.0+YYYYMMDD.HHMMSS
```

The `1.3.0` part is the semantic font-family version. The timestamp is build
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

Expected v1.3.0 signals:

- every ERDA generated font reports a version beginning with `Version 1.3.0+`,
- `erda-ccby-cjk.ttf` passes Han, Hangul, Hiragana, Katakana and CJK long-sample block targets,
- `erda-ccby-indic.ttf` passes Devanagari main and extended targets,
- `erda-ccby-ethiopic.ttf` passes Ethiopic main, supplement, extended,
  extended-A and extended-B targets.