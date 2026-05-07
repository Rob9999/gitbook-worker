---
title: Anonymized v2.4.2 PDF customer feedback
version: 0.1.0
date: 2026-05-07
status: triaged
priority: high
labels: [customer-feedback, pdf, fonts, layout, windows]
history:
  - version: 0.1.0
    date: 2026-05-07
    description: Initial anonymized intake of v2.4.2 PDF follow-up findings.
---

# Anonymized v2.4.2 PDF Customer Feedback

## Privacy Boundary

This file intentionally stores only anonymized Worker-relevant facts. It does
not preserve customer repository names, branches, local project paths, package
hashes, or full raw customer logs. Concrete examples below are reduced to the
minimum needed for Worker reproduction and triage.

## Acceptance Signals

A customer-side upgrade to `gitbook_worker 2.4.2` was operationally completed in
a DE/EN book repository:

- The Worker wheel and sdist were vendored and referenced by the customer build.
- DE and EN PDFs were rebuilt with the repository virtual environment.
- Both PDFs embed `TwemojiMozilla` and `ERDACCbyCJK-Regular`.
- Japanese, Korean, and Traditional Chinese text is extractable from both PDFs.
- CJK line bounding boxes on the inspected license pages remain inside the PDF
  page box. The earlier CJK margin overlap is no longer reproducible in this
  verification point.

## Prioritized Follow-ups

### P0: Windows stale ERDA font stubs can abort the build

A Windows environment contained 5-byte ERDA Indic/Ethiopic font stub files under
the user font directory. `luaotfload-tool --find` resolved the configured ERDA
script font names to these corrupt files. During PDF header evaluation,
`\IfFontExistsTF{ERDA CC-BY Indic}` failed inside luaotfload before the document
could render.

Expected Worker hardening:

- Optional script-font macros should only emit `\IfFontExistsTF` when the Worker
  has found a valid managed font file, or when the check is known safe.
- Font candidates should be minimally validated before use: non-trivial size,
  readable SFNT/TTF signature, and, when feasible, expected internal family
  metadata.
- Corrupt ERDA stubs in user font directories should either be ignored in favor
  of managed fonts or produce a clear pre-LaTeX diagnostic.
- Reproducible builds should prefer repository/manifest-managed font locations
  over historic user font directories.
- Consider an official font sandbox switch for local Windows builds.

Backlog: [windows-font-stub-hardening.md](windows-font-stub-hardening.md)

### P1: H4 headings render as run-in headings in PDF

Pandoc maps Markdown `####` headings to LaTeX `\paragraph{...}`. Standard LaTeX
renders `\paragraph` as a run-in heading, so the first following paragraph starts
on the same line. Customer sources intentionally keep a repeated emphasis line
after the heading, so the repeated text must remain; only the heading layout
should become block-style.

Expected Worker hardening:

- Redefine `\paragraph` and likely `\subparagraph` as block headings in the PDF
  header layer.
- Keep numbering and table-of-contents behavior unchanged.
- Apply consistently for DE and EN.
- Add regression coverage with an anonymized `9.6.1.1`-style heading fixture.

Backlog: [pdf-block-headings-for-h4.md](pdf-block-headings-for-h4.md)

### P1: CJK overflow appears fixed, add a regression gate

The v2.4.2 customer PDF check confirmed CJK font embedding, extractability, and
in-page CJK bounding boxes. Treat the customer-visible CJK margin issue as fixed,
but automate a stable regression so the behavior does not drift.

Expected Worker hardening:

- Add release/CI regression around CJK license/sample pages.
- Combine `pdffonts` verification for `ERDACCbyCJK-Regular` with bounding-box
  checks for CJK lines.

Backlog: [cjk-linebreaking-and-font-metrics.md](cjk-linebreaking-and-font-metrics.md)

### P2: General PDF overflow remains for URLs, tables, and template/code lines

A full PDF bounding-box scan still found small non-CJK overflows, mostly from
long URLs, wide tables, and template/code-like lines. This is not part of the
CJK fix but should be tracked as general PDF layout hardening.

Expected Worker hardening:

- Improve URL and code break rules, for example via `xurl`/`url` settings or
  Pandoc/LaTeX header rules.
- Explore strategies for wide Markdown tables: smaller table font, longtable
  tuning, or opt-in landscape handling.

Backlog: [pdf-layout-overflow-hardening.md](pdf-layout-overflow-hardening.md)

### P3: Local Poppler display-font warnings are environment noise

`pdffonts` can emit local display-font warnings for fonts such as narrow Arial or
Book Antiqua aliases while still listing all embedded PDF fonts correctly. Track
as a support note, not as a build blocker.
