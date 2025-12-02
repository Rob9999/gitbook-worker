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
6. **Code-Review-Kommentar**: Notiere zu jedem Change eine kurze schriftliche Review-Zusammenfassung mit den wichtigsten Beobachtungen.
7. **Refactoring-Etikette**: Refaktorisiere schrittweise; halte Commits klein, thematisch fokussiert und nachvollziehbar dokumentiert.

## Schreib- und Schnittstellen-Standards
8. **Benennung & Konfiguration**: Bevorzugt klar benannte Methoden/Variablen; vermeide Magic Numbers durch Konstanten oder Konfigurationsobjekte.
9. **CLI-Ergonomie**: Validere Eingaben früh, liefere hilfreiche Fehlermeldungen und halte Interfaces konsistent.
10. **Dokumentationspflicht**: Ergänze neue Funktionen mit kurzen, prägnanten Markdown-Notizen in `docs/` oder passenden Unterordnern; lege bei erkannten Lücken neue Seiten an.
11. **Release- und PR-Hinweise**: Beschreibe im Commit/PR klar, was und warum geändert wurde. Vermeide Sammel-Commits; dokumentiere Tests und bekannte Einschränkungen transparent.

## Font Management & License Compliance
12. **No Hardcoded Fonts**: All fonts MUST be explicitly configured in `gitbook_worker/defaults/fonts.yml`. This is a critical design decision to ensure:
    - **License Compliance**: Every font's license (CC-BY, MIT, OFL, etc.) is tracked and documented
    - **Attribution Requirements**: We can always generate proper attribution for all fonts used
    - **Reproducible Builds**: Identical font configuration across local development, CI/CD, and Docker environments
    - **No System Font Fallbacks**: Publisher will fail rather than use unconfigured system fonts
13. **Font Configuration**: `fonts.yml` is the single source of truth. Each font entry must include:
    - `name`: Official fontconfig family name (e.g., "Twitter Color Emoji")
    - `license`: License identifier (e.g., "CC BY 4.0", "MIT", "OFL 1.1")
    - `license_url`: URL to full license text
    - `download_url` or `paths`: Where to obtain the font
14. **Dynamic Docker Font Setup**: The `Dockerfile.dynamic` reads `fonts.yml` and installs only configured fonts. No fonts are hardcoded in the Dockerfile itself.

## Versionierung
15. Semantic Versioning in allen Dokumenten, JSONs, YAMLs, ...
