---
title: PDF block headings for Markdown H4 and deeper
version: 0.1.0
date: 2026-05-07
status: backlog
priority: P1
labels: [pdf, latex, headings, layout]
history:
  - version: 0.1.0
    date: 2026-05-07
    description: Initial anonymized P1 backlog for Pandoc H4 run-in heading behavior.
---

# PDF Block Headings for Markdown H4 and Deeper

## Problem

Pandoc maps Markdown `####` headings to LaTeX `\paragraph{...}`. Standard LaTeX
renders `\paragraph` as a run-in heading, so the first following paragraph starts
on the same line as the heading.

In customer book sources, a repeated emphasized line after the H4 heading is an
intentional style element and must remain. The Worker should therefore fix the
PDF heading layout, not remove source content.

## Impact

- Severity: P1.
- DE and EN PDFs can show heading text and the following emphasized line as a
  single visual line in text extraction and visual layout.
- This affects readability and review quality for deeply nested sections.

## Desired Behavior

- Render `\paragraph` and likely `\subparagraph` as block headings in PDFs.
- Preserve numbering and table-of-contents behavior.
- Keep behavior consistent across languages.
- Avoid source-level content rewrites.

## Implementation Notes

- Add a LaTeX header snippet in the publisher-generated header layer.
- Prefer a minimal `titlesec`-based configuration if compatible with existing
  templates; otherwise use a local `\makeatletter` sectioning redefinition.
- Add a regression fixture with anonymized `9.6.1.1`-style H4 content followed
  by an emphasized repeated line and a list item.

## Verification

- Unit/header test: generated PDF header contains block-heading definitions for
  `\paragraph` and `\subparagraph`.
- Text/PDF integration fixture: heading and following emphasized paragraph do not
  appear as a run-in line.
- DE/EN sample build remains stable.
