---
title: General PDF overflow hardening for URLs, tables, and code-like lines
version: 0.3.0
date: 2026-05-07
status: partial
priority: P2
labels: [pdf, layout, urls, tables, code]
history:
  - version: 0.3.0
    date: 2026-05-07
    description: Hardened fvextra code-fence wrapping for Pandoc token groups such as highlighted URL lines.
  - version: 0.2.1
    date: 2026-05-07
    description: Added DE/EN URL-in-code-fence stress samples for PDF wrapping investigation.
  - version: 0.2.0
    date: 2026-05-07
    description: Implemented global PDF code-fence wrapping via pdf_options.code_block_wrap; URLs and wide tables remain open.
  - version: 0.1.0
    date: 2026-05-07
    description: Initial anonymized P2 backlog for remaining non-CJK PDF overflows.
---

# General PDF Overflow Hardening for URLs, Tables, and Code-like Lines

## Problem

After the v2.4.2 CJK fix, a customer-side full PDF bounding-box scan still found
small non-CJK overflows. The worst cases were long URLs, wide tables, and
code/template-like lines. These are not regressions of the CJK fix, but they
remain relevant for print-quality PDFs.

## Impact

- Severity: P2.
- Affected content can exceed the right page boundary by a small amount.
- Typical causes are long unbreakable URL tokens, wide tabular content, and
  fixed-width/code-like strings.

## Desired Behavior

- Improve URL break behavior in the LaTeX/Pandoc PDF header, for example using
  `xurl` or stronger `url` break settings.
- Improve code/template line break behavior where safe.
- Provide strategy for wide Markdown tables:
  - table font-size tuning,
  - longtable configuration,
  - optional landscape/wide-table mode,
  - or preflight diagnostics that explain which table is too wide.
- Add a reusable PDF bounding-box layout scanner to release QA once stable.

## Implemented Slice

- `pdf_options.code_block_wrap` enables `fvextra`-based wrapping for Pandoc
  `Highlighting` and plain `verbatim` code environments.
- Highlighted Pandoc token groups such as `\NormalTok{...}` are wrapped with
  `breaknonspaceingroup=true` when the installed `fvextra` version supports it.
- Default is `true`; entries can opt out with `code_block_wrap: false`.
- DE/EN sample content now includes one semantically wrapped folded YAML scalar
  and one deliberately unwrapped long code-fence line as a regression sample.
- DE/EN sample content also includes one deliberately long URL inside a text
  code fence to study URL-token behavior without changing customer content.

## Verification

- Synthetic URL fixture no longer exceeds page width.
- Synthetic wide-table fixture emits a controlled warning or uses an expected
  mitigation.
- Release QA can report line and block overflow counts with enough context for
  support triage.
