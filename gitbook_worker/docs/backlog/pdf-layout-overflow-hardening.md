---
title: General PDF overflow hardening for URLs, tables, and code-like lines
version: 0.1.0
date: 2026-05-07
status: backlog
priority: P2
labels: [pdf, layout, urls, tables, code]
history:
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

## Verification

- Synthetic URL fixture no longer exceeds page width.
- Synthetic wide-table fixture emits a controlled warning or uses an expected
  mitigation.
- Release QA can report line and block overflow counts with enough context for
  support triage.
