# Workflow Tool Suite

This package contains the Python-based automation that powers the repository's
GitHub Actions workflows.  Treat `.github` as an isolated project: create a
local virtual environment, install the pinned dependencies declared in
`pyproject.toml`/`requirements.txt`, and run the tools with `python -m …` so the
same entry points work in CI and locally.

## Environment setup

### Windows PowerShell

```powershell
cd .github
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### macOS / Linux

```bash
cd .github
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### Tests & smoke checks

```bash
cd .github
pytest -q
python -m tools.workflow_orchestrator --profile default --dry-run
```

Use the orchestrator as the preferred entry point; it reads `publish.yml`,
resolves profiles and orchestrates the remaining tools.  When Docker is
available you can build the CI image for parity tests via:

```bash
docker build -f .github/gitbook_worker/tools/docker/Dockerfile -t erda-workflow-tools .
```

## Tool index

| Module | Purpose | Primary docs |
| --- | --- | --- |
| `workflow_orchestrator/` | High-level CLI that executes the configured publishing and QA steps. | [README](workflow_orchestrator/README.md) |
| `publishing/` | Incremental manifest handling and PDF/GitBook publishing helpers. | [README](publishing/README.md) |
| `converter/` | CSV → Markdown/diagram converters used during publishing. | [README](converter/README.md) |
| `quality/` | Markdown QA utilities such as link audits and reference repair. | [README](quality/README.md) |
| `emoji/` | Emoji/font reporting and inline asset helpers. | [README](emoji/README.md) |
| `support/` | Lightweight debugging helpers for GitBook configuration. | [README](support/README.md) |
| `utils/` | Shared subprocess, Docker and venv helpers. | [README](utils/README.md) |
| `docker/` | Dockerfiles that reproduce the CI environment. | [README](docker/README.md) |

## Module overview

### `workflow_orchestrator/`

The orchestrator mirrors the GitHub workflow chain and is the preferred entry
point for automated runs:

* `orchestrator.py` resolves command-line arguments into an
  `OrchestratorConfig` by reading `publish.yml`, expanding profile templates and
  deriving runtime options such as repository visibility.  It then invokes the
  configured steps in order while exporting a consistent environment for
  subprocesses.
* Available steps include:
  * `check_if_to_publish` – run `publishing/set_publish_flag.py` to compute which
    manifest entries changed between two Git SHAs and should be rebuilt.
  * `ensure_readme` – create placeholder `readme.md` files for directories that
    would otherwise break GitBook navigation.
  * `update_citation` – keep `docs/public/publish/citation.cff` in sync with the
    current date.
  * `converter` – call `publishing/dump_publish.py` followed by the CSV asset
    converter to refresh derived tables and charts.
  * `engineering-document-formatter` – ensure Markdown engineering documents
    carry the expected YAML front matter.
  * `publisher` – delegate to `publishing/pipeline.py` for the heavy lifting.
* `__main__.py` exposes `python -m tools.workflow_orchestrator` as the CLI entry
  point.

### `publishing/`

Implements the selective publishing flow used by Actions jobs:

* `pipeline.py` orchestrates the end-to-end run.  It resolves the manifest,
  optionally toggles publish flags, normalises GitBook assets via
  `gitbook_style.py`, and forwards custom options to the PDF publisher.  Each
  helper is executed as a subprocess to ensure identical CLI behaviour inside
  GitHub Actions and local runs.
* `publisher.py` reads the manifest entries flagged for publishing and renders
  PDFs.  It combines Markdown sources, applies optional landscape helpers,
  injects fonts and LaTeX macros, honours per-entry asset directories from
  `publish.yml` when constructing Pandoc's resource path so images stay
  available, runs Pandoc and resets build flags through `reset_publish_flag.py`
  when successful.  The CLI exposes `--emoji-color` to use Twemoji (CC BY 4.0)
  color fonts, `--emoji-report`/`--emoji-report-dir` to emit
  Markdown emoji usage summaries, and supports overriding Pandoc defaults via the
  `ERDA_PANDOC_DEFAULTS_JSON` or `ERDA_PANDOC_DEFAULTS_FILE` environment
  variables.
* `gitbook_style.py` contains two subcommands: `rename`, which applies GitBook
  naming conventions, and `summary`, which rebuilds `SUMMARY.md` from
  `book.json`.  Both support running with or without Git metadata.
* `preprocess_md.py`, `markdown_combiner.py` and `table_pdf.py` provide the PDF
  pre-processing pipeline, handling wide tables, landscape sections and paper
  size escalation.
* `set_publish_flag.py`, `reset_publish_flag.py` and `dump_publish.py` manage
  manifest state for incremental builds.
* The `fonts/`, `lua/` and `texmf/` subfolders ship the assets required by
  Pandoc and LaTeX when running headless inside CI.

### `converter/`

Utilities that transform CSV inputs referenced by the manifest into user-facing
artefacts:

* `convert_assets.py` discovers `assets/csvs/` folders next to manifest entries,
  converts each CSV into a Markdown table under `assets/tables/`, applies an
  optional template from `assets/templates/`, and renders charts into
  `assets/diagrams/` when numeric data is present.
* `csv2md_and_chart.py` holds the reusable helpers for rendering Markdown tables
  and matplotlib charts.  They are imported by the converter and exposed for
  ad-hoc use.

### `quality/`

Quality assurance tooling that inspects Markdown sources for regressions:

* `sources.py` extracts "Quellen"/"Sources" sections from Markdown files into a
  CSV report to help maintain bibliographies.  Run it with
  `python -m tools.quality.sources --help` for usage information.
* `link_audit.py` validates external links, image references, heading reuse and
  TODO markers, emitting CSV or log summaries depending on the selected CLI
  flags (`python -m tools.quality.link_audit --help`).
* `ai_references.py` validates and repairs bibliography entries with the help of
  large language models.  It derives the Markdown scope from `SUMMARY.md`,
  submits each reference to the configured AI backend, updates confirmed fixes on
  disk, and emits a structured JSON report for downstream tooling.
* `staatenprofil_links.py` scans Markdown files matching `*staatenprofil*.md`
  and writes a CSV report listing failing HTTP checks so editors can repair the
  profiles without combing through the book manually (`python -m
  tools.quality.staatenprofil_links --help`).

### `emoji/`

Emoji-specific utilities shared by the harness and publishing workflows:

* `scan_emojis.py` inventories all emoji sequences used across the Markdown
  sources and emits JSON artefacts consumed by the harness templates.
* `scan_fonts.py` reports font-family declarations so the harness can detect
  regressions and forbidden fallbacks.
* `inline_emojis.py` replaces emoji glyphs in HTML output with inline SVG/PNG
  assets using Twemoji (CC BY 4.0) exclusively as per AGENTS.md license policy.
* `report.py` groups emoji usage by Unicode block to highlight coverage gaps,
  providing a lightweight monitoring hook for editors and CI.

### `support/`

Lightweight helpers that assist with manual debugging and testing outside the
core publishing pipeline.  See [`support/README.md`](support/README.md) for CLI
examples.

### `utils/`

Developer-focused helpers that make it easier to execute the workflows on
heterogeneous machines:

* `run.py` wraps `subprocess.run`, standardising logging, error handling and
  environment merging.
* `docker_runner.py` builds (if necessary) and launches Docker containers with a
  bind-mounted workspace, automatically attempting to start Docker Desktop on
  Windows and the daemon on Linux.
* `python_workspace_runner.py` bootstraps a `.venv` for a given workspace,
  installs dependencies via `pip`, `requirements.txt` files or the optional `uv`
  installer, and executes a provided command/module inside that environment.
* `__init__.py` exports convenience imports for the utils package.

### `docker/`

Contains Dockerfiles used by CI jobs.  `Dockerfile.python` provides a base image
with LaTeX tooling, fonts and Pandoc for the publishing pipeline, while the
multi-stage `Dockerfile` is geared towards building and testing the workflow
suite itself.  The accompanying README documents usage patterns.

## Code review – outstanding follow-ups

The latest pass over the toolchain surfaced a few improvements that remain on
our radar:

1. **Documentation consistency** – With the consolidated guide inlined here,
   keep module READMEs focused on actionable usage while cross-linking back to
   this index for shared setup instructions.
2. **Setup automation** – Adding lightweight helper scripts (e.g.
   `.github/setup-dev.sh` and `.ps1`) would make onboarding even smoother.
3. **Secret naming** – Several workflow docs still reference historical secret
   names.  Replace them with placeholders or repo-specific annotations the next
   time those workflows are updated.
4. **Test coverage** – Expand `pytest` coverage around the orchestrator profiles
   and converter edge cases (wide tables with custom templates) to lock in the
   behaviour described above.

## Development conventions

* Format code with `black` and `isort`, lint with `flake8`, and keep type hints
  up to date.
* When adding new scripts, include docstrings or README updates so their purpose
  is discoverable from this document.
* Whenever you change the behaviour of an existing tool, update the relevant
  module README so it remains accurate.
