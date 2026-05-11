# Agent Directives for GitBook Worker (v1.3.3)

## Scope & How to Use This File
- Diese Anweisungen gelten für das gesamte Repository; es gibt aktuell keine verschachtelten Abweichungen.
- Neue Regeln sollten hier ergänzt werden, damit Beitragende eine einzige, verlässliche Quelle haben.

## Projekt- und Layout-Hinweise
1. **Package-first Layout**: Der Python-Code lebt im Wurzelverzeichnis unter `gitbook_worker/`. Nutze Importe über `gitbook_worker.*`; der Fallback unter `tools/` dient nur der Abwärtskompatibilität.
2. **Dokumentationsort**: 
 * Alle Anwendungsdokumente inkluding deren Examples (docs/examples) in den docs/ Ordner; mit Hinweis oder Link im repo README.md 
 * Alle Entwicklungsdokumente gehören in den gitbook_worker/docs Ordner; dort in selbsbeschreibende Ordner: e.g. sprints, migrations, architectures, ...
3. **Front matter & Versionierung**: Planungs- oder Engineering-Dokumente benötigen YAML-Frontmatter mit mindestens `version`, `date` und einem kurzen `history`-Eintrag.

## Arbeitsweise & Qualitätssicherung
4. **Testing**: Führe `pytest` aus dem Repo-Root für neue Features oder Fixes aus. Falls Tests nicht laufen, begründe es in Commit- oder PR-Texten.
5. **RUN-Sicherungspunkt**: Vor potenziell destruktiven Run-, Build-, Smoke- oder Validierungsläufen zuerst einen kleinen Git-Commit als Wiederherstellungspunkt erstellen. Wenn ein Commit nicht möglich oder fachlich falsch ist, Grund dokumentieren und vor dem Lauf einen gleichwertigen Sicherungspunkt per Backup-Branch oder Patch herstellen.
6. **Logging**: Behalte aussagekräftige `info`/`warn`/`error`-Logs in neuer Automatisierung bei, damit Abläufe nachvollziehbar bleiben.
7. **GitHub Actions & Hilfsskripte**: Falls im Ordner `.github/` wieder Python-Helfer auftauchen, richte dort eine eigene `pyproject.toml` samt lokalem `.venv/` ein und verweise VS Code explizit auf dieses Environment. Actions-Schritte sollen entweder das veröffentlichte Paket oder diese lokale Toolchain nutzen – niemals globale Systeminstallationen.
8. **Format & Lint**: Formatiere Code mit `black`, sortiere Importe via `isort`, lint mit `flake8`. Neue Funktionen bekommen Typannotationen; nutze `pathlib.Path` statt nackter Strings für Dateipfade.
9. **Code-Review-Kommentar**: Notiere zu jedem Change eine kurze schriftliche Review-Zusammenfassung mit den wichtigsten Beobachtungen.
10. **Refactoring-Etikette**: Refaktorisiere schrittweise; halte Commits klein, thematisch fokussiert und nachvollziehbar dokumentiert.

## Schreib- und Schnittstellen-Standards
11. **Benennung & Konfiguration**: Bevorzugt klar benannte Methoden/Variablen; vermeide Magic Numbers durch Konstanten oder Konfigurationsobjekte.
12. **CLI-Ergonomie**: Validere Eingaben früh, liefere hilfreiche Fehlermeldungen und halte Interfaces konsistent.
13. **Dokumentationspflicht**: Ergänze neue Funktionen mit kurzen, prägnanten Markdown-Notizen in `docs/` oder passenden Unterordnern; lege bei erkannten Lücken neue Seiten an.
14. **Release- und PR-Hinweise**: Beschreibe im Commit/PR klar, was und warum geändert wurde. Vermeide Sammel-Commits; dokumentiere Tests und bekannte Einschränkungen transparent.
- **Kundenproblem-Repros**: Kundendaten und Kunden-PDFs dienen nur der Diagnose. Fuer jedes kundenbezogene Problem muss vor einer Lieferung ein eigenes anonymisiertes Sample oder Fixture im Repo entstehen; Kundenrohdaten, extrahierte Kundentexte und Diagnoseartefakte duerfen nicht als Testfixture, Repo-Inhalt oder Release-Anhang verwendet werden.

## Font Management & License Compliance
15. **No Hardcoded Fonts**: All fonts MUST be explicitly configured in `gitbook_worker/defaults/fonts.yml`. This is a critical design decision to ensure:
    - **License Compliance**: Every font's license (CC-BY, MIT, OFL, etc.) is tracked and documented
    - **Attribution Requirements**: We can always generate proper attribution for all fonts used
    - **Reproducible Builds**: Identical font configuration across local development, CI/CD, and Docker environments
    - **No System Font Fallbacks**: Publisher will fail rather than use unconfigured system fonts
16. **Font Configuration**: `fonts.yml` is the single source of truth. Each font entry must include:
    - `name`: Official fontconfig family name (e.g., "Twemoji Mozilla")
    - `license`: License identifier (e.g., "CC BY 4.0", "MIT", "OFL 1.1")
    - `license_url`: URL to full license text
    - `download_url` or `paths`: Where to obtain the font
17. **Dynamic Docker Font Setup**: The `Dockerfile.dynamic` reads `fonts.yml` and installs only configured fonts. No fonts are hardcoded in the Dockerfile itself.
18. **LuaTeX Cache Guard**: If fallback fonts are configured but not in the LuaTeX cache, publishing will now abort early. See [gitbook_worker/docs/attentions/lua-font-cache.md](gitbook_worker/docs/attentions/lua-font-cache.md) for recovery steps (install fonts, then run `luaotfload-tool --update --force`).

Additional font policy decisions as of 2026-05-10:
- Apart from the already configured DejaVu family, all project fonts and emoji fonts must be CC BY 4.0 licensed ERDA/Twemoji-family assets.
- Noto fonts are explicitly forbidden for this repository, including as temporary fallback, test fixture, Docker dependency, or documentation recommendation.
- When Twemoji Mozilla does not cover required customer emojis, build and configure an ERDA Emoji font under CC BY 4.0 instead of adding another external fallback family.
- The historical `.github/fonts/erda-ccby-cjk/` name is deprecated conceptually; new planning should use the broader `erda-ccby-fonts` family name while preserving compatibility until the rename is performed deliberately.

## Versionierung
19. Semantic Versioning in allen Dokumenten, JSONs, YAMLs, ...


## Exit Codes & Diagnose
20. Führe eine dokumentierte Exit-Code-Tabelle mit Klartext-Fehlermeldung und Healing-Steps in [gitbook_worker/docs/attentions/exit-codes.md](gitbook_worker/docs/attentions/exit-codes.md); halte sie bei jedem neuen Exit-Grund aktuell.
21. CLI-Tools müssen die Exit-Code-Tabelle über `--help exit-codes` (oder gleichwertig) ausgeben, damit Nutzer sie ohne Doku-Aufruf sehen.
22. Jeder eindeutige Exit-Grund erhält einen eigenen Exit-Code und eine menschenlesbare Fehlermeldung; Codes bleiben stabil, Deprecations müssen kenntlich gemacht werden.
23. Für Fehler, die in Entwicklung/Test auftreten und nicht dauerhaft behebbar sind, definiere trotzdem einen Exit-Code plus dokumentierte Workarounds/Healing.

## Problemlösungsphilosophie
24. **Schritt-für-Schritt-Ansatz**: Der wichtigste Ansatz um ein Ziel zu erreichen ist, Schritt für Schritt, Schicht um Schicht, nie aufgeben, dennoch prüfen ob die Umgebung - zwar nicht den Kern des Hauptauftrages (das Hauptziel) dennoch einige Randparameter - Anpassung am Vorgehen erfordert. Und klar: das Hauptziel soll und muss Pro Leben sein.

## Fixe
25. Keine Dirty Fixe!!!

## Konfigurationsvollständigkeit (Config-Completeness-Policy)
26. **Jeder Konfigurationsschlüssel braucht einen Status**: Alle Einträge in `publish.yml`, `book.json`, `fonts.yml`, `content.yaml` und den Dateien unter `gitbook_worker/defaults/` müssen einem dieser Zustände zugeordnet sein: ✅ Implementiert, 🔨 Teilweise implementiert, 📝 Deklarativ (extern/CI), 🚧 WIP, ❌ Unused.
27. **Neue Schalter nur mit Dokumentation**: Wer einen neuen Konfigurationsschlüssel einführt, muss gleichzeitig die Konfigurationsreferenz (`docs/configuration-reference.md`) und den Backlog-Eintrag (`gitbook_worker/docs/backlog/config-completeness-and-documentation.md`) aktualisieren.
28. **WIP klar kennzeichnen**: Noch nicht fertig implementierte Schalter erhalten den Status 🚧 WIP in der Referenzdokumentation. Sie dürfen keine stillschweigende Fehl- oder Nicht-Funktion haben; stattdessen Warnung oder Early-Exit mit Hinweis.
29. **Testpflicht für ✅-Schalter**: Jeder als „implementiert" markierte Schlüssel muss mindestens einen zugehörigen Unit- oder Integrationstest haben.
30. **Konfigurationsdatei-Versionierung**: Jede YAML/JSON-Konfigurationsdatei muss ein `version`-Feld (SemVer) tragen. Schema-Änderungen bumpen dieses Feld und werden im zugehörigen Dokument unter `docs/configs/` mit Versionshistorie dokumentiert.
31. **Sample-Content-Abdeckung**: Die Sprachbäume `de/` und `en/` müssen für jeden ✅-Schalter mindestens ein Sample-Dokument enthalten. Feature-spezifische Sprachbäume (z. B. `de-edge-cases/`) dienen dem isolierten Testen von Sonderfällen und werden in `content.yaml` mit `build: false` als Default eingetragen.

## How to release
- Bump version consistently (setup.cfg, gitbook_worker/__init__.py, any manifest/release notes), following semver; remove stray duplicate packaging files.
- Run tests from repo root (`python -m pytest gitbook_worker/tests -m "not slow"`) and note failures with rationale if any remain.
- Build installable artifacts: `python -m build`; ensure dist filenames carry the target version.
- Smoke the wheel in a fresh venv: `pip install dist/gitbook_worker-<ver>-py3-none-any.whl`; run `python -m gitbook_worker.tools.workflow_orchestrator --help` and check the banner shows the new version; optional dry-run `workflow_orchestrator run --dry-run --root <repo>`.
- Update user-facing docs: README.md (version refs, examples, release history DE+EN), docs/HANDBOOK.md, docs/customer-installation.md, docs/configuration-reference.md, docs/releases/v<ver>.md. Commit docs separately.
- Tag and push: use **annotated tags** (`git tag -a v<ver> -m "message"`); feature releases use `v<Major>.<Minor>.<Patch>`, hotfixes use `release-v.<ver>-hotfix`. Push with `git push origin main --tags`.
- Publish GitHub release with the tag and changelog; attach sdist/wheel from `dist/` if distributing; keep release notes in docs/releases in sync.
- Full step-by-step procedure: `gitbook_worker/docs/how-to-release/release-procedure.md`.