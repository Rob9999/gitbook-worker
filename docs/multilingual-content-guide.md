---
version: 0.4.0
date: 2025-11-25
history: Contributor-Workflow ergänzt, Shared-Asset-Sync dokumentiert, Frontmatter korrigiert.
---

# Multilingual Content Guide

Diese Anleitung beschreibt, wie wir mehrere Sprachvarianten des Buchs parallel pflegen, konfigurieren und bauen.

## Überblick
- Jede Sprache besitzt einen eigenen Ordner (`<lang-id>/`) im Repo-Root. `de/` enthält bereits den produktiven Buchinhalt (inkl. `content/`, `book.json`, `publish/`).
- Eine zentrale `content.yaml` im Root listet alle Sprachvarianten, damit Skripte wie `gitbook_worker` automatisch wissen, welche Inhalte existieren und wo sie liegen.
- Credentials für externe Quellen (z. B. Git-Repos) werden **nicht** in der YAML-Datei abgelegt, sondern über Environment-Variablen oder Secret Stores referenziert (`credentialRef`).

## content.yaml
```yaml
version: 1.0.0
default: de
contents:
  - id: de
    uri: de/
    type: local
    description: German baseline content
  - id: en
    uri: en/
    type: local
    description: English content (WIP)
  - id: ua
    uri: github.com:rob9999@democratic-social-wins
    type: git
    description: Book about democratic society of Ukraine
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```
**Felder**
- `version`: Schema-Version, damit spätere Erweiterungen migrationsfähig bleiben.
- `default`: Sprache, die ohne weitere Parameter gebaut wird.
- `contents[]`: Liste der Sprachdefinitionen.
  - `id`: Kurzname, wird für CLI-Flags (`--lang de`) und Credential-Lookups verwendet.
  - `uri`: Wurzelpfad (lokal) oder Remote-Quelle (Git/HTTP).
  - `type`: `local`, `git`, `archive` usw., damit der Loader weiß, wie `uri` zu behandeln ist.
  - `description`: Kurzbeschreibung für CLI-Ausgaben/Docs.
  - `credentialRef`: Optionaler Name einer Env-Variable oder eines Secret-Handles für geschützte Quellen.

## Sprachordner-Aufbau
```
repo/
  |- de/
  |   |- book.json
  |   |- content/
  |   |- CITATION.cff
  |   |- LICENSE
  |   |- publish/
  |   \- assets/ (optional)
  |- en/
  |- ua/
  |- gitbook_worker/
  |- tests/
  \- content.yaml
```
- `content/`: Markdown-Einträge des Buchs (Kapitel, Appendices, Templates).
- `book.json`: Build-Einstellungen für GitBook/CLI.
- `citation.cff`, `license/`, `publish/`: Artefakte, die pro Sprache ausgeliefert werden.
- Gemeinsame Skripte/Packages bleiben im Root (`gitbook_worker/`, `tests/`).

## Credential-Strategie
1. Hinterlege Secrets pro Sprache in `.env.local` (entwicklerseitig) oder direkt im CI (z. B. GitHub Secrets, Azure Key Vault).
2. Benenne die Variable identisch mit `credentialRef` aus `content.yaml` (z. B. `GITBOOK_CONTENT_UA_DEPLOY_KEY`).
3. Der CLI-Layer liest `content.yaml`, erkennt den `credentialRef` und lädt das Secret bei Bedarf. Der Wert kann entweder **den Pfad** zu einem privaten SSH-Key oder den **Key-Inhalt** selbst enthalten. Inline-Keys werden nach `.gitbook-content/keys/<lang>.key` geschrieben und mit restriktiven Berechtigungen versehen. Fehlt das Secret, bricht der Build mit einer klaren Fehlermeldung ab.

## Remote-Inhalte & Cache
- `type: git`-Einträge werden automatisch nach `.gitbook-content/<lang-id>` geklont. Wiederholte Läufe aktualisieren diese Checkouts statt sie neu zu clonen.
- Das Secret aus `credentialRef` wird als `GIT_SSH_COMMAND` eingebunden, damit Deploy-Keys ohne zusätzliche Wrapper funktionieren.
- Falls bereits ein externer Checkout existiert (z. B. CI-Cache), setze `GITBOOK_CONTENT_ROOT` auf diesen Pfad und die CLI überspringt den Clone-Schritt.
 
## Contributor-Workflow (Kurzfassung)
1. **Struktur kopieren oder Remote verbinden** – dupliziere `de/` als Vorlage oder verbinde eine bestehende Git-Quelle via `type: git`.
2. **`content.yaml` erweitern** – neuer `id`, `uri`, `type`, optional `credentialRef`; `default` nur ändern, wenn eine andere Sprache der Standard werden soll.
3. **Shared Assets synchronisieren** – gleiche Änderungen an Frontmatter/Fonts/README-Snippets zwischen allen Sprachen ab (`gitbook_worker/defaults/*`).
4. **Validieren & testen** – `gitbook-worker validate --lang <id>` plus fokussierte Pytests (`pytest -k <id>`), anschließend CI-Matrix erweitern.
5. **Dokumentation aktualisieren** – Ergänzungen in `docs/contributor-new-language.md` festhalten, damit der Ablauf nachvollziehbar bleibt.

Die ausführliche Schritt-für-Schritt-Anleitung steht in `docs/contributor-new-language.md`.

## Shared Assets & Templates
- `gitbook_worker/defaults/frontmatter.yml` – Basis-Metadaten für PDF/Markdown; halte Übersetzungen synchron, damit Release-Banner und Attribution übereinstimmen.
- `gitbook_worker/defaults/fonts.yml` – Schriftkonfiguration, die alle Sprach-Pipelines verwenden; teste neue Fonts zunächst in einer Sprache, bevor du sie global aktualisierst.
- `gitbook_worker/defaults/readme.yml` und `smart.yml` – definieren, welche Dateien beim Publish kombiniert werden; füge neue Kapitel/Anhänge an allen Sprachen gleichzeitig hinzu.
- Gemeinsame Assets (Logos, Fonts, Templates) sollten nicht in einzelnen Sprachordnern dupliziert werden. Leite sie stattdessen aus `gitbook_worker/defaults/` oder `gitbook_worker/tools/assets/` ab und dokumentiere Ausnahmen.

## Offene Punkte / Nächste Schritte
- CI-Matrix über alle Sprachen (inkl. Smoke-PDF pro Sprache) sowie erweiterte Tests für Credential-Fehlerfälle.
