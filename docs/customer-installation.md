---
version: 1.1.0
date: 2026-02-08
status: draft
history:
  - "1.1.0: 2026-02-08 — publish.yml-Konfiguration und pdf_options-Anleitung ergänzt"
  - "1.0.0: 2025-12-31 — init"
---

# Customer Guide: Installation & Getting Started with the GitBook Worker

**Purpose:**  
Ensure that the provided version of the `gitbook_worker` is always used – even if older projects with their own local `tools/` modules exist on the same machine.  

## 1) Clean Python environment (per project)

1. Change into the project directory (for example: `C:\Path\To\Project`).
2. Create and activate a virtual environment (Windows PowerShell):
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Remove legacy packages if present:

   ```powershell
   pip uninstall -y gitbook-worker tools
   ```
4. Install the provided version:

   * Using a wheel file (recommended):

     ```powershell
     pip install --no-deps --force-reinstall dist/gitbook_worker-<version>-py3-none-any.whl
     ```
   * Or directly from the delivered repository:

     ```powershell
     pip install --no-deps --force-reinstall .
     ```

## 2) Verify what is actually imported

After installation, verify that no foreign `tools` modules are being imported:

```powershell
python - <<'PY'
import gitbook_worker, tools
print("gitbook_worker:", gitbook_worker.__file__)
print("tools shim     :", tools.__file__)
PY
```

All reported paths must point into the active `.venv` (for example:
`...\ .venv\Lib\site-packages\gitbook_worker\...`).

## 3) Start the orchestrator

Example for a language-specific run using a local profile (the corresponding `publish.yml` is resolved automatically from `content.yaml`):

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run --root <PROJECT_ROOT> --profile local --lang <lang>
```

Common variants:

* Run only converter / PDF pipeline: `--step converter` or `--step publisher`
* Dry run (no external steps executed): `--dry-run`
* Explicitly specify a manifest: `--manifest <lang>/publish.yml` (overrides automatic resolution from `content.yaml`)

## 4) Docker run (optional, if Docker Desktop is available)

```powershell
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile local --use-dynamic --lang <lang> --root <PROJECT_ROOT>
```

Notes:

* Fonts are injected at runtime via volume mounts; `fonts-storage/` and `.github/fonts/` must exist.
* On Windows, path translation is handled automatically by Docker Desktop.

## 5) Configuring `publish.yml` for your book

The `publish.yml` in each language directory controls PDF generation.
Here is a complete annotated example:

```yaml
project:
  name: "Mein Buch"
  author: "Jane Doe"             # or: authors: ["Jane", "Bob"]
  version: "1.0.0"
  license: "CC-BY-SA-4.0"
  date: "2026-01-01"

publish:
  - out_format: pdf              # also accepted: format, target_format
    source_dir: content/
    summary_file: content/SUMMARY.md
    pdf_options:
      # --- Layout ---
      documentclass: book        # article | report | book
      fontsize: 12pt
      geometry: "a4paper, margin=2.5cm"
      papersize: a4
      numbersections: true

      # --- TOC ---
      toc: true                  # folder builds default true, file builds false
      toc-depth: 3               # 1–6

      # --- Fonts (Pandoc-native keys preferred) ---
      mainfont: "DejaVu Serif"
      sansfont: "DejaVu Sans"
      monofont: "DejaVu Sans Mono"

      # --- Hyperlinks ---
      colorlinks: true
      linkcolor: blue
      urlcolor: blue
      citecolor: green

      # --- Language / Babel ---
      lang: de-DE

      # --- Advanced: raw LaTeX preamble ---
      header-includes: |
        \usepackage{booktabs}
```

> **Tip:** All standard Pandoc/LaTeX variables are forwarded transparently.
> The full key reference is in [`docs/configuration-reference.md`](configuration-reference.md).

## 6) Common pitfalls

* **Wrong `tools` module:** Always activate the `.venv` and, if necessary, run `pip uninstall tools`.
* **Manifest not found:** Provide `--manifest` relative to the repository root (e.g. `<lang>/publish.yml`), or omit the flag to fall back to `content.yaml`.
* **Missing LuaTeX / fonts:** Ensure `luaotfload-tool --update --force` has been run at least once (handled in test fixtures, but may be required locally).
* **`project.license` missing in the manifest:** Set a license under `project.license` in `<lang>/publish.yml` (e.g., `CC-BY-SA-4.0`), otherwise the publisher fails with `project.license fehlt`.

## 7) Quick support checklist

* `.venv` active? (`where python` points to the project `.venv`)
* `gitbook_worker.__version__` matches the delivered release?
* `tools.__file__` points to
  `.venv\Lib\site-packages\gitbook_worker\tools\__init__.py`?
* Orchestrator log shows
  `manifest=...\<lang>\publish.yml` and
  `tools_dir=...site-packages\gitbook_worker\tools`?
