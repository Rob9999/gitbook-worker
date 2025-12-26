---
title: Generische Buch-Lizenzierung & Defaults
version: 0.1.0
date: 2025-12-06
history:
  - version: 0.1.0
    date: 2025-12-06
    description: Initial backlog draft for safe defaults and metadata sourcing.
---

# Ziel
Sichere, generische Lizenz-/Attributions-Defaults bereitstellen, wenn ein Buchprojekt das Paket per `pip install gitbook-worker` nutzt – ohne Annahmen zu verletzen oder rechtliche Risiken einzugehen.

# Leitplanken (rechtlich & UX)
- Kein automatisches „Rechtseinräumen“: Platzhalter dürfen keine stillschweigende Lizenzierung suggerieren.
- Sichtbare Warnung, wenn Pflichtfelder fehlen; Build darf wahlweise **failen** oder „warn+placeholder“ schreiben, niemals still schweigen.
- Attribution muss nachvollziehbar bleiben; keine versteckten Autoren-/Projektangaben.

# Metadaten-Quellen (Priorität)
1. `publish.yml` (project/author/license/attribution section) – **Pfad für Nutzer:innen**.
2. `book.json` (falls GitBook-Style vorhanden) – fallback.
3. Repository-Metadaten als letzte Eskalationsstufe: Repo-Name → project name; Repo owner → org/author placeholder; Git remote URL → source link.
4. Keine Daten? → Fail mit klarer Fehlermeldung + Beispielsnippet.

# Empfohlene Felder in `publish.yml`
```yaml
project:
  name: "Mein Buch"
  authors:
    - name: "Vorname Nachname"
      email: "author@example.com"
      org: "Organisation"
  license: "CC BY 4.0"   # oder CC BY-SA 4.0, CC0, etc.
  attribution_policy: "fail"  # fail | warn
```

# Default-Verhalten (wenn Felder fehlen)
- `project.name`: Repo-Name als Placeholder, **markiert** (z.B. "<MISSING project.name | using repo 'erda-book'>").
- `authors`: Repo-Owner als Placeholder-Author mit Warnung.
- `license`: keine Vermutung; Build **failt**, wenn nicht gesetzt.
- `attribution_policy`: default `fail` (kein stilles Durchwinken).
- Platzhalter-Text landet in `publish/ATTRIBUTION.md` und PDF-Frontmatter, mit Hinweis „PLEASE SET project.* IN publish.yml“.

# Umsetzungsskizze
- Parser-Erweiterung in `workflow_orchestrator`/`publisher`:
  - Lese `publish.yml` → optional `book.json` → Repo-Metadaten.
  - Sammle Missing-List; wenn critical (license/author), gemäß Policy fail oder warn.
- Neue Validatoren/Tests:
  - Unit: fehlendes `project.license` → Fehler.
  - Repo-derived Defaults: prüfen, dass Warnhinweis in Attribution erscheint.
- Templates/Docs:
  - README-Snippet für `project`-Block.
  - Hinweis im `pip-install` Quickstart.

# UX-Notizen
- CLI-Hinweis beim Run: „project.license missing → set in publish.yml (example shown)“.
- Keine automatische Lizenz-Wahl; Anwender müssen aktiv wählen.

# Offene Punkte
- Welche Lizenzen erlauben? (Whitelist analog fonts/license-policy?)
- Ob book.json-Felder (title/author) immer überschrieben oder gemerged werden.
- Mehrsprachige Attribution? (lokalisierte Hinweise).
