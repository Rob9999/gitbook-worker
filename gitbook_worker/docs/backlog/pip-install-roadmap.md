---
version: 0.1.0
date: 2025-12-06
history:
  - version: 0.1.0
    date: 2025-12-06
    description: Initial plan to make gitbook_worker installable via pip/PyPI.
---

# Roadmap: pip-installierbares gitbook_worker-Paket (PyPI-ready)

## Zielbild
- `pip install gitbook-worker` liefert lauffähige CLI/Module ohne Repo-Checkout.
- Fonts und Assets laufen lizenzkonform (keine System-Fallbacks, nur `fonts.yml`-Konfiguration).
- CI/CD baut sdist+wheel, führt Tests/Smoke-Läufe aus und kann signierte Uploads zu PyPI erledigen.
- Konsumenten können optional Fonts synchronisieren (`[fonts]` extra) und automatisiert PDFs erzeugen (GitHub Actions Beispiel).

## Scope
- Build-/Release-Pipeline für sdist & wheel.
- Paketinhalt: CLI (`gitbook-worker`), Orchestrator, Publisher, Smart-Font-Stack, Defaults (`fonts.yml`, `frontmatter.yml`, `readme.yml`, `smart.yml`, `docker_config.yml`).
- Optionale Extras: `[fonts]` zieht nur benötigte Runtime-Abhängigkeiten (kein systemweiter Font-Fallback).
- Docs: Nutzer:innen-Guide für pip-Install + CI-Example-Workflow.

## Out-of-Scope (jetzt)
- Veröffentlichung sensibler Assets, die nicht lizenz-cleared sind.
- Vollautomatischer Font-Download in Post-Install (nur opt-in via CLI/extra).
- Registry-Mirroring (nur PyPI, kein GitHub Packages in diesem Schritt).

## Ist-Stand
- PoC `poc-standalone-package` existiert (minimal, Version 0.1.0, nur hello/CLI-Dummy).
- Smart Font Stack Architektur entworfen (`docs/architecture/smart-font-stack.md`), Font-Backlogs vorhanden (dynamic generation, attribution).
- CI-Workflows existieren für Orchestrator/Tests (Docker-basiert), aber keine PyPI-Pipeline.

## Lücken
- Kein produktives `pyproject.toml`/`setup.cfg` fürs echte Paket (Name, Versioning, deps, entry-points).
- Paket-Inhalte/Package-Data (defaults, Lua-Skripte, templates) nicht verdrahtet.
- Fonts/License-Handling im Wheel ungeklärt (Attribution, LICENSE-FONTS, optionaler Download-Flow).
- Smoke-Tests für Wheel/Editable-Install fehlen; kein matrix-test `pip install gitbook-worker` ohne Repo.
- Kein Release-Process (tagging, changelog, signing, PyPI token handling, dry-run).
- Docs fehlen: Install/Usage, CI-Workflow-Beispiel.

## Plan (Phasen & Tasks)
1) **Paket-Skelett anheben**
   - [ ] `pyproject.toml` finalisieren (name `gitbook-worker`, version aus `gitbook_worker/__init__.py`, classifiers, deps, optional extras `[fonts]`).
   - [ ] Entry Points: `gitbook-worker = gitbook_worker.tools.workflow_orchestrator:main` (oder Wrapper), plus evtl. `gitbook-worker-fonts` für sync.
   - [ ] Package-Data definieren: defaults/*.yml, Lua-Filter, templates, Docker configs falls nötig.
   - [ ] Lizenzbeilagen: LICENSE, LICENSE-FONTS, ATTRIBUTION.md in sdist/wheel aufnehmen.

2) **Font-/Asset-Compliance für Paket**
   - [ ] Klarstellen: keine System-Fallbacks; Fail-fast wenn Font fehlt.
   - [ ] Extras `[fonts]`: zieht nur Python-Abhängigkeiten; Font-Bits via `fonts_cli sync`/`smart_font_stack` (kein Bundling proprietärer Dateien).
   - [ ] Attribution-Generator integrieren (mindestens Hook/CLI), referenzierbar im Paket.
   - [ ] Prüfen, ob Twemoji/ERDA-Fonts als Download-Quelle (nicht eingebettet) ausreichend dokumentiert sind.

3) **Tests & Smokes für pip-Install**
   - [ ] Wheel-/sdist-Build-Test: `python -m build` in CI.
   - [ ] Install-Smoke: `pip install dist/*.whl` → `gitbook-worker --help`; `python -c "import gitbook_worker"`.
   - [ ] Minimal PDF-Smoke ohne Repo: kleiner Markdown-Stub + `publish.yml` from package defaults.
   - [ ] Mypy/pytest weiter nutzen; marker für fontabhängige Tests skippen, wenn Fonts nicht installiert.

4) **CI/CD für Release**
   - [ ] Neuer GH Actions Workflow `pypi-publish.yml`: build sdist/wheel, run smokes, publish on tag; use PyPI API token secret.
   - [ ] Dry-run-Job (test.pypi.org) für PRs.
   - [ ] Signierte Artefakte optional (GHA provenance/sigstore, wenn gewünscht).

5) **Docs & DX**
   - [ ] Neues Doc: Install & Quickstart (pip, optional fonts sync, minimal publish.yml Beispiel, GitHub Action Snippet).
   - [ ] README-Update mit PyPI-Badge, Supported Python Versions, Known Limitations (TeX/Pandoc required).
   - [ ] CHANGELOG/Release Notes Format festlegen (semver, v2.0.0+ baseline).

6) **Versionierung & Governance**
   - [ ] Quelle der Version: `gitbook_worker/__init__.py` + `pyproject.toml` harmonisieren.
   - [ ] Tagging-Konvention (`v2.0.1` etc.), Release-Branch-Policy.
   - [ ] Entscheiden, ob Fonts-Changes minor/patch heben.

## Akzeptanzkriterien MVP
- `pip install gitbook-worker` auf clean VM (ohne Repo) → CLI `gitbook-worker --help` funktioniert.
- `python -m build` erzeugt gültige sdist+wheel; Wheel enthält Defaults/Lua-Files.
- Testmatrix (Linux, optional Windows) grün für Install-Smoke + zentrale Pytest-Suite (font-sensitive Tests dürfen skippen, aber dokumentiert).
- Dokumentation: Schritt-für-Schritt für Nutzer:innen + CI-Workflow-Beispiel.

## Sofort nächste Schritte
1. Packaging-Skelett aufsetzen (pyproject + entry points + package_data) im Hauptrepo.
2. Smoke-Test für Wheel-Install schreiben und in CI einhängen.
3. Draft für PyPI-Workflow (`.github/workflows/pypi-publish.yml`) erstellen (build + test + optional TestPyPI).