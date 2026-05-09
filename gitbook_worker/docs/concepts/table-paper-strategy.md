---
version: 1.0.0
date: 2026-05-09
status: implemented
history:
  - "1.0.0: 2026-05-09 - Editorial best-fit table paper strategy for the Tabellenprofi release."
---

# Editorial Table Paper Strategy

## Release Name

Redaktioneller Name: **Tabellenprofi**.

The name follows the previous `Tabellenfest` release but focuses on professional
layout judgement instead of mere overflow avoidance.

## Goal

Choose the smallest allowed paper format on which a Markdown pipe table remains
readable, comparable by column, and editorially acceptable. The decision must
not only ask whether the unwrapped table fits a width. It must also estimate how
badly cells would wrap on each paper candidate.

## Scope

- Applies to Markdown pipe tables during preprocessing.
- Uses deterministic heuristics before Pandoc/LuaLaTeX runs.
- Keeps the historical column-count heuristic as a lower bound.
- Preserves the oversize fallback for tables wider than every configured
  candidate, but emits a diagnostic decision.
- Supports explicit, reviewable per-table overrides via HTML comments in the
  source Markdown.

## Strategy

For every table, GitBook Worker builds column profiles:

- text width per cell and header,
- longest risky token or script run,
- column kind (`numeric`, `code`, `status`, `label`, `prose`),
- risk flags (`url`, `code`, `cjk`).

Then every candidate paper receives a layout score using:

- usable text width after margins,
- allocated text width per column,
- estimated max cell lines,
- estimated max header lines,
- average row height in lines,
- number of columns below their minimum readable width,
- overflow beyond minimum readable widths,
- unbreakable token overflow.

The selected paper is the first candidate that satisfies the readability
thresholds after the historical column-count lower bound. If no candidate is
fully acceptable, the lowest score is used and the log/report explains why.

## Script And Long-Run Handling

Long words are not a German-only problem. The scorer treats long token and
script runs as a general layout risk. CJK/Hangul/Kana characters are measured as
wide glyphs and counted in line estimates even when there are no spaces. At the
same time, CJK characters are treated as character-level break opportunities so
the algorithm does not falsely classify a natural CJK run as one unbreakable
Latin-style token.

## Configuration

Default behavior is enabled without configuration. Projects can tune the
strategy under `publish[].pdf_options.table_paper_strategy`:

```yaml
pdf_options:
  table_paper_strategy:
    enabled: true
    mode: editorial
    max_cell_lines: 5
    max_header_lines: 3
    preferred_max_avg_row_lines: 2.8
    min_readable_column_width_mm: 14
    unbreakable_overflow_tolerance_mm: 2
    oversize_policy: preserve-column-heuristic
    report: jsonl
    candidates:
      - a4
      - a4-landscape
      - a3
      - a3-landscape
      - a2
      - a2-landscape
      - a1
      - a1-landscape
      - name: customer-wide
        standard: false
        size_mm: [900, 420]
        margins_mm: [20, 15, 20, 15]
```

If `report: jsonl` is set without `report_path`, the publisher writes a report
next to the PDF as `<output-stem>.table-layout.jsonl`.

## Per-Table Override

An explicit source comment can force a reviewed table format:

```markdown
<!-- gbw-table paper=a3-landscape reason="reviewed editorial layout" -->
| Column | Column |
|---|---|
| ... | ... |
```

The override is reviewable in source control and appears in table strategy logs
and JSONL reports.

## Diagnostics

Each decision logs:

- selected paper,
- method,
- reason,
- column count,
- estimated width,
- candidate scores and rejection reasons.

Optional JSONL reports make customer problem cases reproducible without parsing
human-oriented logs.

## Limits

The strategy is still preflight estimation, not exact TeX box measurement. It
does not replace visual PDF QA for high-risk customer releases. It does,
however, turns table paper choice into an explainable editorial decision rather
than a raw width heuristic.