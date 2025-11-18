# Converter Utilities

Transforms CSV assets referenced by `publish.yml` into Markdown tables and, when
possible, charts.  The scripts are designed to run both as standalone helpers
and as part of the publishing pipeline.

## Commands

### `python -m tools.converter.convert_assets`

* Discovers `assets/csvs/` folders next to each manifest entry selected for
  publishing.
* Generates Markdown tables under `assets/tables/` and saves charts to
  `assets/diagrams/` when numeric data is detected.
* Applies optional Jinja2 templates stored under `assets/templates/` alongside
  the source entry.

### `python -m tools.converter.csv2md_and_chart`

* Converts a single CSV file to Markdown and optionally renders a PNG chart.
* Useful when testing custom templates or iterating on CSV formatting.

## Key flags

* `--title-level` – adjust the heading depth of the generated table title.
* `--wide {A3,A2,A1}` – wrap the table in the LaTeX macros `\WideStartAthree`,
  `\WideStartAtwo`, or `\WideStartAone` followed by `\WideEnd`, enabling
  landscape pages in larger paper sizes without altering the font.
* `--manifest` – restrict `convert_assets` to the subset of manifest entries that
  changed since the last publishing run.

## Tips

1. Activate the `.github` virtual environment and install dependencies before
   running the converter so Pandas and Matplotlib are available.
2. Use `--dry-run` together with verbose logging to verify which CSV files are
   discovered without writing artefacts.
3. Keep the README updated when adding new CLI options or template discovery
   mechanisms; the publishing pipeline imports this module directly.
