---
version: 1.0.0
date: 2026-01-10
history:
  - "init: 2026-01-10 add v2.0.6 hotfix release procedure"
---

# Release-Prozedur (ab v2.0.6 Hotfix)

Diese Anleitung beschreibt den Release-Workflow für Hotfixes wie `release-v.2.0.6-hotfix`. Sie folgt den Vorgaben aus `AGENTS.md` und dem bestehenden Release-Prozess.

## Vorbereitungen
- Stelle sicher, dass das Repo sauber ist (außer den geplanten Änderungen). Keine fremden Änderungen zurücksetzen.
- Python-Umgebung aktivieren (`.venv`), Pandoc/TeX/Docker verfügbar machen.
- Fonts müssen über `defaults/fonts.yml` bereitstehen (siehe `AGENTS.md`).

## Schritte
1) **Release Notes anlegen und Release Version anpassen**
   - Neues File in `docs/releases/` mit Frontmatter (`version`, `date`, `status`, `history`) anlegen, Inhalt nach `docs/releases/v2.0.5.md` strukturieren.
   - Release Version `release-v.<Major>.<Minor>.<Patch>[-hotfix|-<NAME>]`
   - Release Short Version `<Major>.<Minor>.<Patch>.[post1]`
   - in setup.cfg die Release Short Version setzen, e.g. version = 2.0.6.post1
   - in gitbook_worker/__init__.py die Release Short Version setzen, e.g. __version__ = "2.0.6.post1"
2) **Lokale Orchestrator-Runs**
   - `python -m gitbook_worker.tools.workflow_orchestrator run --root <repo> --content-config content.yaml --lang customer-de --profile local`
   - TOC mit `python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf customer-de/publish/das-erda-buch.pdf --format text` prüfen.
   - Blocker fixen, einfache Bugs fixen oder Backlog-Eintrag in `gitbook_worker/docs/backlog/` anlegen -> PO involvieren.
3) **Docker-basierte Orchestrator-Runs**
   - `python -m gitbook_worker.tools.workflow_orchestrator run --root <repo> --content-config content.yaml --lang customer-de --profile docker --isolated --logs-dir logs/docker`
   - Blocker fixen, einfache Bugs fixen oder Backlog-Eintrag in `gitbook_worker/docs/backlog/` anlegen -> PO involvieren.
4) **Tests ausführen**
   - `python -m pytest gitbook_worker/tests -m "not slow" -q`
   - Blocker fixen, einfache Bugs fixen oder Backlog-Eintrag in `gitbook_worker/docs/backlog/` anlegen -> PO involvieren.
5) **Wiederholen, bis grün**
   - Schritte 2–4 iterieren, bis alle Runs/Tests fehlerfrei sind.
   - Blocker fixen, einfache Bugs fixen oder Backlog-Eintrag in `gitbook_worker/docs/backlog/` anlegen -> PO involvieren.
6) **Pip-Install-Smoke**
   - `python -m build`
   - In frischem Venv: `python -m venv .venv-smoke && .\.venv-smoke\Scripts\activate && pip install dist/gitbook_worker-<ver>-py3-none-any.whl`
   - `python -m gitbook_worker.tools.workflow_orchestrator --help` (Banner + Exit 0) und optional Dry-Run.
   - Blocker fixen, einfache Bugs fixen oder Backlog-Eintrag in `gitbook_worker/docs/backlog/` anlegen -> PO involvieren.
7) **Wiederholen, bis grün**
   - Bei Problemen zu Schritt 2 zurück und erneut durchlaufen.
8) **Taggen & Push**
   - Tag-Format: `release-v.<Major>.<Minor>.<Patch>[-hotfix|-<NAME>]`, z.B. `release-v.2.0.6-hotfix`.
   - `git tag release-v.2.0.6-hotfix` und `git push origin main --tags` (Branch ggf. anpassen).

## Dokumentation
- Jede Abweichung/Blocker im passenden Backlog-Eintrag festhalten (`gitbook_worker/docs/backlog/`).
- In Release Notes die getesteten Befehle, relevante Fixes und offene Risiken notieren.

## Hinweise
- Keine Fonts außerhalb von `fonts.yml` verwenden; Docker-Setup zieht Fonts aus der Datei (siehe `Dockerfile.dynamic`).
- Bei LaTeX-Problemen `ERDA_KEEP_LATEX_TEMP=1` setzen, Logs unter `logs/` sammeln.
- SemVer beibehalten (`__version__` in `gitbook_worker/__init__.py` und Packaging).