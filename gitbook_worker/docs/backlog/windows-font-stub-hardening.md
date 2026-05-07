---
title: Windows font stub hardening for optional ERDA script fonts
version: 0.2.0
date: 2026-05-07
status: implemented
priority: P0
labels: [fonts, windows, pdf, luatex, hardening]
history:
  - version: 0.1.0
    date: 2026-05-07
    description: Initial anonymized P0 backlog for corrupt user-font stubs breaking optional ERDA script font checks.
  - version: 0.2.0
    date: 2026-05-07
    description: Implemented managed font-file validation and removed unsafe family-name existence checks for ERDA script helpers.
---

# Windows Font Stub Hardening for Optional ERDA Script Fonts

## Problem

On Windows, corrupt or stale user-font stub files can shadow configured ERDA font
families. A customer-side local build found 5-byte ERDA Indic/Ethiopic stubs in
the Windows user-font directory. `luaotfload-tool --find` resolved the ERDA
family names to those invalid files.

The current PDF header can emit optional script font checks such as:

```tex
\IfFontExistsTF{ERDA CC-BY Indic}{...}{...}
```

In the affected environment, the existence check itself failed inside
`luaotfload` before the PDF could render.

## Impact

- Severity: P0.
- A local Windows publisher build can abort before PDF creation.
- The issue is environmental, but the Worker can harden optional font handling to
  avoid letting invalid user-font stubs crash LaTeX.

## Desired Behavior

- Prefer repository/manifest-managed font files for configured ERDA fonts.
- Validate candidate font files before they influence generated LaTeX:
  - size is above a small safety threshold,
  - file starts with a plausible SFNT/TTF/OTF signature,
  - optional internal family-name validation when cheap and reliable.
- Do not emit optional `\IfFontExistsTF` checks for script fonts when the Worker
  has evidence that the configured font family resolves only to invalid files.
- If all candidates are invalid and the content requires the script font, fail
  before LaTeX with a clear diagnostic and healing steps.
- Consider a documented local font sandbox switch for reproducible Windows
  builds that should ignore historic user-font directories.

## Implementation Notes

- Implemented in `gitbook_worker.tools.publishing.publisher` for the generated
  ERDA script helper macros:
  - invalid `luaotfload-tool --find` resolved files are rejected when they are
    too small or do not start with a plausible TTF/OTF/TTC signature,
  - configured ERDA script fonts are loaded via validated managed font files and
    explicit fontspec `Path=...` file references,
  - optional script helpers remain no-op when no valid managed font file exists,
    instead of probing the family name with `\IfFontExistsTF`.
- Start with the publisher header path that builds `\erdaIndic{...}` and
  `\erdaEthiopic{...}` helpers.
- The first safe slice can avoid optional `\IfFontExistsTF` macros unless a valid
  managed font path is known, while preserving no-op fallbacks for documents that
  do not need those scripts.
- Add unit tests with synthetic invalid font candidates instead of checking real
  user font directories.

## Verification

- Unit test: invalid 5-byte font candidate is ignored or diagnosed before LaTeX.
- Unit test: valid configured ERDA script font still emits script routing helper.
- Smoke: DE/EN sample PDFs still embed ERDA CJK, Indic, Ethiopic, and Twemoji.
