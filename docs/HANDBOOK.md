---
version: 1.4.1
date: 2026-05-12
history:
  - "1.4.1: 2026-05-12 - v2.9.2 Layoutpakete und Quellenlisten-Kontext fuer Landscape-Tabellen dokumentiert"
  - "1.4.0: 2026-05-11 - v2.9.1 Abnahmefix, URL-Breaking und fokussierte Editorial-Signale dokumentiert"
  - "1.3.9: 2026-05-10 - Text-Checkbox-Symbole fuer PDF-Fallback ueber DejaVu Sans dokumentiert"
  - "1.3.8: 2026-05-09 - Tabellenprofi-Strategie fuer v2.8.0 dokumentiert"
  - "1.3.7: 2026-05-08 - Wide-Table-Paper-Selection fuer v2.7.0 dokumentiert"
  - "1.3.6: 2026-05-08 - URL-Code-Fence-Hotfix fuer v2.6.1 dokumentiert"
  - "1.3.5: 2026-05-07 - PDF-Code-Fence-Wrapping fuer v2.6.0 dokumentiert"
  - "1.3.4: 2026-05-07 - Windows-Font-Stub-Haertung und H4/H5-Blockheadings fuer v2.4.3 dokumentiert"
  - "1.3.3: 2026-05-06 - CJK-Linebreak und ERDA-Script-Font-Routing fuer v2.4.2 dokumentiert"
  - "1.3.2: 2026-05-05 - Dockerfile.dynamic als Release-Pfad und legacy Dockerfile als deprecated dokumentiert"
  - "1.3.1: 2026-05-04 - RUN-Sicherungspunkt vor potenziell destruktiven Laeufen dokumentiert"
  - "1.3.0: 2026-02-08 — pdf_options passthrough, Aliases, publish.yml Konfigurationsanleitung"
  - "1.2.0: 2025-12-07 — Added font fallback reporting and abort semantics for PDF builds."
---

# GitBook Worker Handbook

This handbook replaces the sprawling legacy tree (now archived under
`gitbook_worker/docs/archive/legacy-package/`) with a concise,
maintained reference. The legacy archive remains read-only for deep dives.

## Package layout at a glance
- `content.yaml` lists all languages (currently `de/` live, `en/` staging, `ua/` remote) and feeds the CLI via `--lang`.
- Per-language content lives under `<lang>/` (`de/` already contains `content/`, `book.json`, `publish/`, etc.).
- Python package lives at repository root under `gitbook_worker/` and exposes the `gitbook-worker` console script.
- Tests reside in `gitbook_worker/tests/` and cover publishing, orchestrator flows, and emoji/font QA.
- CI workflows under `.github/workflows/` mirror local usage by building the Docker image and invoking the same CLI entrypoints.
- User-facing docs belong in `docs/`, engineering/sprint notes in `gitbook_worker/docs/` (per `AGENTS.md`).

## Local development essentials
- Install dependencies with `pip install -r requirements.txt` and run quick checks via `pytest -q` from the repository root.
- Before potentially destructive RUN/build/smoke/validation steps, create a small Git commit as a recovery point for the intended current changes. If committing is not possible, record the reason and create an equivalent backup branch or patch before running the command.
- When editing YAML planning docs, keep the front matter (`version`, `date`, `history`) in sync with the change.
- The deprecated `tools/` shim exists only for legacy imports—prefer `gitbook_worker.*` everywhere else.
- Remote Sprachbäume mit `type: git` werden automatisch nach `.gitbook-content/<id>` geklont; setze die in `credentialRef` genannte Env-Variable auf einen SSH-Key (Pfad oder Inhalt), sonst schlägt der Build fehl.

## Contributor quickstart
- Install in editable mode: `pip install -e .` from the repository root.
- Validate manifests quickly: `gitbook-worker validate --lang de` (does not run the pipeline).
- Run a local build: `./gitbook_worker/scripts/build-pdf.sh --profile local --manifest de/publish.yml` or `gitbook-worker run --lang de --profile default`.
- Execute targeted tests during iterations: `pytest gitbook_worker/tests/test_publisher.py gitbook_worker/tests/test_orchestrator_validate.py` (fixtures now resolve the default language via `content.yaml`).

### Adding or updating language trees
- Copy the structure from `de/` (or an existing language) and adjust `content/`, `book.json`, `publish/`, and attribution/licensing files for the new locale.
- Append the new entry to `content.yaml` with a unique `id`, `type`, and `uri`; remote repos require a `credentialRef` so secrets remain outside git.
- Keep shared defaults in sync: `gitbook_worker/defaults/frontmatter.yml`, `fonts.yml`, and `readme.yml` should match across languages to avoid divergent PDFs/HTML.
- Reference assets that all languages consume (fonts, templates, logos) from shared folders instead of duplicating them per language; update the contributor how-to (`docs/contributor-new-language.md`) whenever the process changes.
- Verify the addition with `gitbook-worker validate --lang <id>` followed by a targeted `pytest -k <id>` run if you introduced locale-specific tests.

## Troubleshooting
- If PDF output misses images, ensure the source directory is covered by Pandoc `--resource-path` (handled automatically by the publisher helper) and that assets live under `assets/` or `.gitbook/assets/`.
- For font issues, confirm Twemoji/ERDA fonts are installed in the Docker image; the dynamic Dockerfile bundles them by default.
- Enable verbose orchestrator analytics by reviewing log entries containing `Orchestrator analytics` after failures.

## CI guardrails
- Unit tests enforce coverage via `pytest ... --cov=gitbook_worker --cov-fail-under=45` and publish `coverage.xml` as an artifact.
- A dedicated `type-check` job runs `mypy` against the package on Python 3.12 with project dependencies installed.
- Integration tests validate PDF rendering inside the Docker image and confirm Twemoji + ERDA CJK fonts are present before running slow suites.

## Publishing and fonts (field notes)
- The dynamic Docker build installs TeX Live and Pandoc, then applies font setup driven by repository configuration rather than hardcoded fonts.
- If integration tests report missing emoji or CJK fonts, ensure Twemoji and ERDA CC-BY CJK are available in the runner or rebuild the Docker image so the font check passes.
- Repository builds now keep vendor fonts out of git: `fonts-storage/` (ignored) is populated automatically by `gitbook_worker.tools.publishing.font_storage.FontStorageBootstrapper` during `fonts sync` and orchestrator runs. Delete the folder to force a refresh or set `GITBOOK_WORKER_DISABLE_FONT_STORAGE_BOOTSTRAP=1` when developing offline.
- v2.4.3 keeps the global fallback stack CJK-first for stability. Long Devanagari and Ethiopic samples are routed through explicit ERDA script helpers instead of moving Indic/Ethiopic ahead of CJK globally. Script helpers now load validated managed font files by path and avoid optional `\IfFontExistsTF` family probes so stale Windows user-font stubs cannot abort the PDF header.
- Pandoc H4/H5 headings (`\paragraph`/`\subparagraph`) are redefined with package-free LaTeX `\@startsection` rules so they render as block headings without requiring `titlesec.sty`.
- v2.6.1 extends PDF code-fence wrapping for Pandoc token macros such as `\NormalTok{...}`. When `fvextra` is available, token arguments are routed through `\FV@InsertBreaks`; this keeps long URLs inside code fences within the page bounds while preserving a clean PDF text layer.
- v2.7.0 improves wide Markdown table handling. Pipe tables are estimated by per-column text width and compared against usable text width after margins; the old column-count heuristic remains a lower bound, and oversized tables emit a warning instead of pretending that a standard paper size solved them.
- v2.8.0 moves table paper choice into `table_strategy.py` and adds editorial scoring. The strategy compares candidate papers by expected wrapping, row height, header wraps, narrow columns, and unbreakable overflow; `pdf_options.table_paper_strategy` can tune thresholds, write JSONL layout reports, and accept per-table `gbw-table` paper overrides.
- v2.9.2 keeps compact editorial context with wrapped landscape tables: short lead text, legends, sibling micro-tables, cross-references, and source/reference lists can travel with the table when bounded by the height check.
- Checklist symbols such as `☐`, `☑`, `☒`, `✓`, and `✔` are text symbols, not colour emoji. The publisher routes them through `text-symbols.lua` and the configured sans font so Pandoc task-list markers do not fall back to math square placeholders or missing-glyph boxes.
- v2.9.1 routes visible HTTP/HTTPS URLs through `url-breaks.lua` as breakable `\url{...}` LaTeX, avoids nested `\href{...}{\url{...}}`, and keeps access-date markers such as `(Zugriff: ...)` outside the URL macro.
- Editorial quality signals are intentionally scoped for review usefulness: long-token warnings skip frontmatter and URL-bearing Markdown tokens, duplicate-heading warnings are near-document signals, and plain prose such as "peer review" is not treated as an open review marker.

### PDF font fallback behavior

1. Missing glyph detection and reporting
The PDF build shall detect whenever a glyph required by the document cannot be rendered by the configured primary fonts. For all such cases, the build shall produce a clear, detailed report listing:
- the affected code points (and, if possible, their Unicode names),
- the fonts that were attempted,
- and the fact that they could not provide a valid glyph (i.e. the result would be a .notdef / empty box).
This report shall be written to the build log for troubleshooting.

2. Use of the mainfontfallback stack
The `mainfontfallback` stack exists to prevent missing-glyph boxes, not just to check font availability. For every glyph that the primary fonts cannot render, the PDF build shall try each font in the `mainfontfallback` stack in order and use the first fallback font that can provide a proper glyph (e.g. a regular text glyph, emoji glyph, etc.). As long as every required glyph can be rendered either by a primary font or by at least one font in the `mainfontfallback` stack, the PDF build shall succeed and no .notdef / empty box glyphs shall appear in the output.

For CJK-heavy PDFs, `cjk-linebreak.lua` adds safe breakpoints after CJK characters so long Traditional Chinese, Japanese, and Korean passages can wrap before the page margin.

Text-style checklist symbols are routed through the configured sans font (`DejaVu Sans` in the shipped profiles). Keep that font available and include it in custom fallback stacks when a project overrides `mainfont_fallback`, especially for customer books that use Pandoc task lists or literal `☐`/`☑` markers.

3. Abort condition
The PDF build shall abort only if, after trying all configured primary fonts and all fonts in the `mainfontfallback` stack, there remains at least one required glyph that would still be rendered as a missing-glyph box (.notdef). In that case, the pipeline shall fail and emit the detailed missing-glyph report described in (1), instead of silently producing a PDF with empty boxes.

Control: In `publish.yml` you can disable aborting while still logging the report via `pdf_options.abort_if_missing_glyph: false` (default: true).

4. Central font configuration
a) All fonts, including the primary ones and the `mainfontfallback` ones, shall be configured exclusively in `gitbook_worker/defaults/fonts.yml`. 
b) In the unique book project `publish.yml` then is defined which fonts finally shall be used for the book project; e.g. as main font, as, sans font, as ... font, as mainfont fallback. 
c) The publishing header shall apply the configured fallback stack automatically; individual documents shall not configure their own font fallback behavior.


## Configuring `publish.yml` — pdf_options & aliases

Since v2.2.0 the publisher transparently forwards standard Pandoc / LaTeX
variables from `publish.yml ➜ pdf_options` to the Pandoc command line.
You no longer need to use custom `header-includes` hacks for common knobs.

### Minimal example

```yaml
project:
  name: "My Book"
  author: "Jane Doe"           # singular alias for authors:[]
  version: "1.0.0"
  license: "CC-BY-SA-4.0"

publish:
  - out_format: pdf             # aliases: format, target_format
    source_dir: content/
    pdf_options:
      documentclass: book
      fontsize: 12pt
      geometry: "margin=2.5cm"
      toc: true
      toc-depth: 2
      numbersections: true
      colorlinks: true
      linkcolor: blue
      urlcolor: blue
      lang: de-DE
      mainfont: "DejaVu Serif"
      sansfont: "DejaVu Sans"
      monofont: "DejaVu Sans Mono"
```

### Supported pdf_options keys

| Key | Type | Effect |
|-----|------|--------|
| `documentclass` | string | LaTeX document class (`article`, `report`, `book`, …) |
| `fontsize` | string | Font size (`10pt`, `11pt`, `12pt`) |
| `geometry` | string | Page geometry (`margin=1in`, `a4paper,margin=2.5cm`, …) |
| `toc` | bool | Generate table of contents (overrides default: folder→true, file→false) |
| `toc-depth` | int | Depth of the TOC (1–6) |
| `numbersections` | bool | Number headings |
| `colorlinks` | bool | Coloured hyperlinks |
| `linkcolor` | string | Internal link colour |
| `urlcolor` | string | External URL colour |
| `citecolor` | string | Citation link colour |
| `toccolor` | string | TOC link colour |
| `lang` | string | Pandoc/Babel language tag (e.g. `de-DE`, `en-US`) |
| `header-includes` | string/list | Raw LaTeX injected into the preamble |
| `classoption` | string | Additional LaTeX class options |
| `papersize` | string | Paper size (`a4`, `letter`, …) |
| `linestretch` | string | Line spacing factor |
| `mainfont` | string | Main font (Pandoc-native, preferred over `main_font`) |
| `sansfont` | string | Sans font (Pandoc-native, preferred over `sans_font`) |
| `monofont` | string | Mono font (Pandoc-native, preferred over `mono_font`) |
| `main_font` | string | Legacy key for main font (backwards-compatible) |
| `sans_font` | string | Legacy key for sans font (backwards-compatible) |
| `mono_font` | string | Legacy key for mono font (backwards-compatible) |
| `mainfont_fallback` | string | LuaTeX fallback chain (`;`-separated) |
| `abort_if_missing_glyph` | bool | Abort on missing glyphs (default: `true`) |
| `code_block_wrap` | bool | Wrap long PDF code-fence lines via `fvextra` when available (default: `true`) |

All keys not explicitly handled (fonts, toc, lang, header-includes) are passed
through as Pandoc `-V key=value` arguments, so any valid Pandoc/LaTeX variable
works.

### Aliases recognised in `publish.yml`

| What | Aliases accepted | Canonical key |
|------|-----------------|---------------|
| Output format | `format`, `target_format` | `out_format` |
| Author(s) | `author` (string) | `authors` (list) |

Full reference: see [`docs/configuration-reference.md`](configuration-reference.md).

## Docker usage paths
- Use the dynamic image (`gitbook_worker/tools/docker/Dockerfile.dynamic`) for CI, release validation, and local customer-like runs. It keeps font and LaTeX packages aligned with the publishing defaults and resolves TeX Live through `/usr/local/texlive/current`.
- Treat the static image (`gitbook_worker/tools/docker/Dockerfile`) as deprecated legacy material. Do not use it for new release validation or customer onboarding.
- Use `Dockerfile.python` only for lightweight Python test containers; it intentionally does not install Pandoc or TeX Live.

### Running builds in Docker
**Local execution (NO Docker)**:
```bash
# Runs on your local machine (uses local TeX Live, Python, fonts)
python -m gitbook_worker.tools.workflow_orchestrator run --lang de --profile local
```

**Docker execution (isolated container)**:
```bash
# Builds Docker image and runs orchestrator INSIDE container
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile default --use-dynamic --rebuild

# Or with convenience script
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

**Key difference**: The `run_docker.py` module builds the Docker image, starts a container, mounts your workspace to `/workspace`, and executes `workflow_orchestrator` inside the container. The `workflow_orchestrator` has a `--profile docker` option but this is just a profile name—it does NOT trigger Docker execution.

## Migration pointers
- Treat `gitbook_worker/docs/archive/legacy-package/` as historical background; copy only distilled details back into this handbook.
- Prefer small, reviewable commits with a short rationale alongside notable behavior changes.
