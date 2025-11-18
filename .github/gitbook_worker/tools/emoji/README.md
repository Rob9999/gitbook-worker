# Emoji Utilities

Scripts that inventory emoji usage, report font declarations and inline emoji
assets for GitBook output.

## Commands

| Command | Purpose |
| --- | --- |
| `python -m tools.emoji.scan_emojis` | Scans Markdown sources and emits a JSON report describing all emoji sequences, CLDR names and counts. |
| `python -m tools.emoji.scan_fonts` | Reports CSS `font-family` declarations to detect regressions in the harness. |
| `python -m tools.emoji.inline_emojis` | Replaces emoji glyphs in HTML output with inline SVG/PNG assets (prefers Twemoji, falls back to OpenMoji). |
| `python -m tools.emoji.report` | Groups emoji usage by Unicode block and exports a Markdown summary. |

## Typical workflow

1. Run `scan_emojis` and `scan_fonts` before publishing to refresh the reports
   consumed by the harness templates.
2. Use `inline_emojis` when building HTML snapshots where vector emoji assets are
   preferred over system fonts.
3. Share reports in `.github/gitbook_worker/project/docs/reviews` so editors can
   track coverage over time.

## Development notes

* Ensure CLI scripts accept `--help` and provide meaningful exit codes for the
  workflow orchestrator.
* Keep font assets referenced by `inline_emojis.py` in sync with the ones baked
  into the publishing Docker image.
