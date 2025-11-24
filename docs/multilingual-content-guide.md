---
version: 0.1.0
date: 2025-11-24
history: Initial multilingual content guide created.
---

# Multilingual Content Guide

Diese Anleitung beschreibt, wie wir mehrere Sprachvarianten des Buchs parallel pflegen, konfigurieren und bauen.

## Überblick
- Jede Sprache besitzt einen eigenen Ordner (`<lang-id>/`) im Repo-Root mit demselben Aufbau wie das bisherige Single-Language-Projekt.
- Eine zentrale `content.yaml` im Root listet alle Sprachvarianten, damit Skripte wie `gitbook_worker` automatisch wissen, welche Inhalte existieren und wo sie liegen.
- Credentials für externe Quellen (z. B. Git-Repos) werden **nicht** in der YAML-Datei abgelegt, sondern über Environment-Variablen oder Secret Stores referenziert.

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
  |   |- citation.cff
  |   |- license/
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
1. Hinterlege Secrets pro Sprache in `.env.local` (entwicklerseitig) bzw. in CI (z. B. GitHub Secrets, Azure Key Vault).
2. Benenne die Variable identisch mit `credentialRef` aus `content.yaml` (z. B. `GITBOOK_CONTENT_UA_DEPLOY_KEY`).
3. Der CLI-Layer liest `content.yaml`, erkennt den `credentialRef` und lädt das Secret bei Bedarf. Fehlt es, wird der Build mit einer klaren Fehlermeldung abgebrochen.

## Typischer Workflow
1. **Neue Sprache hinzufügen**
   - Ordnerstruktur aus `de/` kopieren (`en/`, `ua/`, …) und Inhalte anpassen.
   - Eintrag in `content.yaml` ergänzen; falls externe Quelle, `credentialRef` notieren.
2. **Lokales Bauen/Testen**
   - `gitbook-worker build --lang de` oder `--lang en` ruft den entsprechenden Ordner auf und schreibt in `<lang>/publish/`.
   - `pytest -k "lang"` für neue Tests, die Spracherkennung und Credential-Fehler abdecken.
3. **CI-Integration**
   - Matrix-Build über `content.yaml`-Einträge, um pro Sprache PDF/HTML zu erzeugen.
   - Validierung: `gitbook-worker validate --lang <id>` prüft Manifest, Fonts und Publish-Ziel.
4. **Deployment/Veröffentlichung**
   - Artefakte aus `<lang>/publish/` bündeln (PDF, Sammel-Markdown, Lizenz, Attribution, `citation.cff`).
   - Upload/Release pro Sprache, optional automatisiert via CLI.

## Offene Punkte / Nächste Schritte
- Loader in `gitbook_worker` implementieren, der `content.yaml` parst und die obige Logik verwendet.
- Bestehenden Content nach `de/` migrieren und den neuen Workflow einmal komplett durchspielen.
- Tests ergänzen (z. B. `tests/test_content_discovery.py`), damit Schema-Änderungen frühzeitig auffallen.
