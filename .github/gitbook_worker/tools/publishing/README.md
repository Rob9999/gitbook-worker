# Publishing Tools

Scripts that implement the incremental publishing flow used by the GitHub
Actions workflows and the local developer harness.  The package reads
`publish.yml`, toggles publish flags, refreshes GitBook artefacts and renders
PDFs via Pandoc.

## Entry points

| Script | Purpose |
| --- | --- |
| `pipeline.py` | Orchestrates the entire publishing workflow and shells out to the helpers listed below so CI and local runs behave identically. |
| `publisher.py` | Builds PDFs for entries flagged in `publish.yml`, injects LaTeX helpers and emoji fonts, and resets flags on success. |
| `set_publish_flag.py` | Marks manifest entries for rebuilding when their sources change between two commits. |
| `reset_publish_flag.py` | Clears publish flags after a successful run. |
| `dump_publish.py` | Emits the manifest entries as JSON for downstream tools (for example, the converter). |
| `gitbook_style.py` | Provides `rename`/`summary` subcommands that align assets with GitBook naming conventions and regenerate `SUMMARY.md` from `book.json`. |

## Typical workflows

Refresh the manifest flags and perform a dry-run PDF build:

```bash
python -m tools.publishing.set_publish_flag --manifest publish.yml --base-ref HEAD^ --head-ref HEAD
python -m tools.publishing.publisher --manifest publish.yml --dry-run
```

Run the legacy pipeline wrapper (used by CI) which coordinates all helper
scripts and the converter:

```bash
python .github/gitbook_worker/tools/publishing/pipeline.py --manifest publish.yml
```

Generate emoji coverage reports while building PDFs:

```bash
python -m tools.publishing.publisher \
  --manifest publish.yml \
  --emoji-color colour \
  --emoji-report \
  --emoji-report-dir build/emoji
```

Pandoc defaults can be overridden via environment variables:

* `ERDA_PANDOC_DEFAULTS_JSON` – inline JSON with keys such as `lua_filters`,
  `metadata`, `variables`, `header_path`, `pdf_engine`, or `extra_args`.
* `ERDA_PANDOC_DEFAULTS_FILE` – path to a JSON file with the same schema.

## Implementation notes

* `publisher.py` combines Markdown sources, applies the optional wide-table
  helpers from `preprocess_md.py`, injects macros from `markdown_combiner.py` and
  uses `table_pdf.py` when a landscape layout is required.  Pandoc executes in
  the surrounding environment (GitHub-hosted runner, the `.github/gitbook_worker/tools` Docker
  image, or a contributor's machine).
* The module honours manifest keys such as `out_dir`, `out_format`,
  `source_type`, `source_format`, `use_summary`, `use_book_json` and
  `keep_combined`.  Relative paths are resolved against the repository root.
* Assets under `fonts/`, `lua/` and `texmf/` ship the LaTeX and emoji resources
  required for headless builds.
* `gitbook_style.py` supports running with or without Git metadata so it can be
  invoked in environments where `.git/` is unavailable.

### Configuring custom fonts

`publisher.py` consumes an optional top-level `fonts` array in `publish.yml` to
make repository or remote typefaces available during the PDF build. Each entry
accepts the following keys:

| Key | Description |
| --- | --- |
| `name` | Optional label that is only used for logging. |
| `path` | Absolute path or manifest-relative directory/file containing `.ttf`/`.otf` fonts. |
| `url` | Download location for archives or single-font files; the filename derived from the URL must end with `.ttf` or `.otf`. |

The publisher copies discovered fonts into `~/.local/share/fonts`, refreshes
`fc-cache`, and tracks the directories for manual discovery when `fontconfig`
is unavailable. Paths take precedence over URLs so repositories can vendor
fonts while providing an external mirror as a fallback.

## Local development checklist

1. Activate the `.github` virtual environment and install dependencies as
   described in the [tool suite README](../README.md).
2. Run `pytest -q` before submitting changes that touch the publishing pipeline.
3. Keep this document updated when new CLI flags or manifest options are added so
   workflow authors understand the impact.
