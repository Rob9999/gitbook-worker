---
version: 0.1.0
date: 2025-11-25
history: Erste Ausgabe mit Schritt-für-Schritt-Anleitung zum Hinzufügen neuer Sprachen.
---

# Contributor How-To: Neue Sprache anlegen

Dieses How-To beschreibt den vollständigen Ablauf vom Scaffold einer neuen Sprachversion 
bis zur Validierung in CI. Es ergänzt das `README` und den Multilingual Guide mit 
konkreten Checklisten.

## Voraussetzungen
- funktionierende `pip install -e .`-Umgebung und Zugriff auf die Git-Repo-Root.
- Entscheide vorab, ob die Sprache lokal im Repo lebt oder über ein externes Git-Repo 
  bereitgestellt wird (z. B. mit privaten Deploy-Keys).
- Stelle sicher, dass du Zugriff auf gemeinsame Assets (`gitbook_worker/defaults/*`) 
  hast, da diese zwischen allen Sprachen synchron bleiben müssen.

## Schritt 1 – Struktur duplizieren oder Remote verbinden
1. Lokale Variante: kopiere `de/` nach `<lang-id>/` (Beispiel: `cp -R de en`). Entferne 
   nicht benötigte Kapitel und übersetze Inhalte schrittweise.
2. Remote Variante (`type: git`): stelle sicher, dass das Zielrepo `content/`, `book.json`,
   `publish/` und optionale Assets enthält. Der Git-URI muss ohne Protokoll-Prefix
   funktionieren (z. B. `github.com:owner/repo`).

## Schritt 2 – `content.yaml` erweitern
1. Öffne `content.yaml` und erweitere `contents` um einen Eintrag wie:
   ```yaml
   - id: fr
     type: local
     uri: fr/
     description: French pilot content
   ```
2. Für Remote-Quellen setze `type: git`, `uri` (SSH/HTTPS) und ein `credentialRef`, z. B.:
   ```yaml
   - id: ua
     type: git
     uri: github.com:rob9999@democratic-social-wins
     credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
   ```
3. Passe `default` nur an, wenn eine andere Sprache automatisch gebaut werden soll.

## Schritt 3 – Credentials hinterlegen (optional)
1. Lege ein Secret oder eine lokale Env-Variable mit dem Namen aus `credentialRef` an.
2. Zulässige Werte:
   - absoluter Pfad zu einem privaten SSH-Key (`C:\Keys\gitbook_ua`), oder
   - der Key-Inhalt selbst (inklusive `-----BEGIN OPENSSH PRIVATE KEY-----`).
3. Inline-Werte werden automatisch nach `.gitbook-content/keys/<lang>.key` geschrieben
   und via `GIT_SSH_COMMAND` verwendet. Der Key wird nur mit Lesezugriff für den aktuellen
   Benutzer erstellt.
4. Prüfe mit `gitbook-worker validate --lang <id>`, ob der Clone ohne Passwortabfrage
   funktioniert. Bei Fehlern liefert die CLI eine gezielte Meldung.

## Schritt 4 – Shared Assets synchronisieren
1. Übernehme Änderungen aus `gitbook_worker/defaults/frontmatter.yml`, `fonts.yml` und
   `readme.yml` in deine neue Sprache (z. B. übersetzte Titel, aber gleiche Struktur).
2. Halte `gitbook_worker/defaults/smart.yml` und globale Templates konsistent, damit der
   Publish-Prozess pro Sprache identische Artefakte erzeugt.
3. Gemeinsame Logos, Fonts oder Makros gehören nicht in einzelne Sprachordner. Verweise
   stattdessen auf die bestehenden Dateien oder füge neue Assets zentral hinzu.

## Schritt 5 – Lokale Validierung
1. Führe `gitbook-worker validate --lang <id>` aus, um Manifest, Fonts und Publish-Tarife
   zu prüfen.
2. Optional: `gitbook-worker run --lang <id> --profile default` generiert direkt das
   Publish-Set unter `<lang>/publish/` (oder den geklonten Cache).
3. Passe Tests an, falls du sprachspezifische Fixtures brauchst. Beispiel:
   ```powershell
   pytest gitbook_worker/tests/test_pipeline.py -k <id>
   ```

## Schritt 6 – CI und Dokumentation nachziehen
1. Ergänze neue Sprachen in Workflow-Matrizen (z. B. `matrix.lang` in GitHub Actions) und
   stelle sicher, dass benötigte Secrets hinterlegt sind.
2. Aktualisiere `docs/multilingual-content-guide.md` und dieses How-To, falls sich der
   Prozess ändert oder zusätzliche Assets synchronisiert werden müssen.
3. Notiere Besonderheiten (z. B. externe Tools, Glossare) in `docs/HANDBOOK.md`, damit das
   Onboarding-Team Bescheid weiß.

## Referenzen
- `README.md` – Überblick zur Repo-Struktur und Remote-Source-Regeln.
- `docs/multilingual-content-guide.md` – detaillierte Beschreibung von `content.yaml`,
  Credential-Strategien und dem Gesamtablauf.
- `gitbook_worker/tools/utils/language_context.py` – Quelle der Logik, die `content.yaml`
  lädt und Remote-Repositories cached.
