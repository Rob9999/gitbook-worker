# Agent Directives for GitBook Worker (v1.1.0)

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
5. **Logging**: Behalte aussagekräftige `info`/`warn`/`error`-Logs in neuer Automatisierung bei, damit Abläufe nachvollziehbar bleiben.
6. **GitHub Actions & Hilfsskripte**: Falls im Ordner `.github/` wieder Python-Helfer auftauchen, richte dort eine eigene `pyproject.toml` samt lokalem `.venv/` ein und verweise VS Code explizit auf dieses Environment. Actions-Schritte sollen entweder das veröffentlichte Paket oder diese lokale Toolchain nutzen – niemals globale Systeminstallationen.
7. **Format & Lint**: Formatiere Code mit `black`, sortiere Importe via `isort`, lint mit `flake8`. Neue Funktionen bekommen Typannotationen; nutze `pathlib.Path` statt nackter Strings für Dateipfade.
8. **Code-Review-Kommentar**: Notiere zu jedem Change eine kurze schriftliche Review-Zusammenfassung mit den wichtigsten Beobachtungen.
9. **Refactoring-Etikette**: Refaktorisiere schrittweise; halte Commits klein, thematisch fokussiert und nachvollziehbar dokumentiert.

## Schreib- und Schnittstellen-Standards
10. **Benennung & Konfiguration**: Bevorzugt klar benannte Methoden/Variablen; vermeide Magic Numbers durch Konstanten oder Konfigurationsobjekte.
11. **CLI-Ergonomie**: Validere Eingaben früh, liefere hilfreiche Fehlermeldungen und halte Interfaces konsistent.
12. **Dokumentationspflicht**: Ergänze neue Funktionen mit kurzen, prägnanten Markdown-Notizen in `docs/` oder passenden Unterordnern; lege bei erkannten Lücken neue Seiten an.
13. **Release- und PR-Hinweise**: Beschreibe im Commit/PR klar, was und warum geändert wurde. Vermeide Sammel-Commits; dokumentiere Tests und bekannte Einschränkungen transparent.

## Font Management & License Compliance
14. **No Hardcoded Fonts**: All fonts MUST be explicitly configured in `gitbook_worker/defaults/fonts.yml`. This is a critical design decision to ensure:
    - **License Compliance**: Every font's license (CC-BY, MIT, OFL, etc.) is tracked and documented
    - **Attribution Requirements**: We can always generate proper attribution for all fonts used
    - **Reproducible Builds**: Identical font configuration across local development, CI/CD, and Docker environments
    - **No System Font Fallbacks**: Publisher will fail rather than use unconfigured system fonts
15. **Font Configuration**: `fonts.yml` is the single source of truth. Each font entry must include:
    - `name`: Official fontconfig family name (e.g., "Twemoji Mozilla")
    - `license`: License identifier (e.g., "CC BY 4.0", "MIT", "OFL 1.1")
    - `license_url`: URL to full license text
    - `download_url` or `paths`: Where to obtain the font
16. **Dynamic Docker Font Setup**: The `Dockerfile.dynamic` reads `fonts.yml` and installs only configured fonts. No fonts are hardcoded in the Dockerfile itself.
17. **LuaTeX Cache Guard**: If fallback fonts are configured but not in the LuaTeX cache, publishing will now abort early. See [gitbook_worker/docs/attentions/lua-font-cache.md](gitbook_worker/docs/attentions/lua-font-cache.md) for recovery steps (install fonts, then run `luaotfload-tool --update --force`).

## Versionierung
18. Semantic Versioning in allen Dokumenten, JSONs, YAMLs, ...


## Exit Codes & Diagnose
19. Führe eine dokumentierte Exit-Code-Tabelle mit Klartext-Fehlermeldung und Healing-Steps in [gitbook_worker/docs/attentions/exit-codes.md](gitbook_worker/docs/attentions/exit-codes.md); halte sie bei jedem neuen Exit-Grund aktuell.
20. CLI-Tools müssen die Exit-Code-Tabelle über `--help exit-codes` (oder gleichwertig) ausgeben, damit Nutzer sie ohne Doku-Aufruf sehen.
21. Jeder eindeutige Exit-Grund erhält einen eigenen Exit-Code und eine menschenlesbare Fehlermeldung; Codes bleiben stabil, Deprecations müssen kenntlich gemacht werden.
22. Für Fehler, die in Entwicklung/Test auftreten und nicht dauerhaft behebbar sind, definiere trotzdem einen Exit-Code plus dokumentierte Workarounds/Healing.

## Problemlösungsphilosophie
23. **Schritt-für-Schritt-Ansatz**: Der wichtigste Ansatz um ein Ziel zu erreichen ist, Schritt für Schritt, Schicht um Schicht, nie aufgeben, dennoch prüfen ob die Umgebung - zwar nicht den Kern des Hauptauftrages (das Hauptziel) dennoch einige Randparameter - Anpassung am Vorgehen erfordert. Und klar: das Hauptziel soll und muss Pro Leben sein.

## Fixe
24. Keine Dirty Fixe!!!