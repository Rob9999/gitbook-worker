# Agent Directives for GitBook Worker (v1.1.0)

## Scope & How to Use This File
- Diese Anweisungen gelten für das gesamte Repository; es gibt aktuell keine verschachtelten Abweichungen.
- Neue Regeln sollten hier ergänzt werden, damit Beitragende eine einzige, verlässliche Quelle haben.

## Projekt- und Layout-Hinweise
1. **Package-first Layout**: Der Python-Code lebt im Wurzelverzeichnis unter `gitbook_worker/`. Nutze Importe über `gitbook_worker.*`; der Fallback unter `tools/` dient nur der Abwärtskompatibilität.
2. **Dokumentationsort**: Neue Entwicklungsdokumente gehören an die Repo-Wurzel (z. B. `README.md`, `SPRINT_PLAN.md`). Der Archivbereich unter `.github/gitbook_worker/docs/` bleibt unverändert für historische Referenzen.
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
