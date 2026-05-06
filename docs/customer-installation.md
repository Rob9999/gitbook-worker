---
version: 2.0.1
date: 2026-05-05
status: stable
history:
  - "2.0.1: 2026-05-05 - Anwenderanleitung fuer v2.4.0 zur Kundenauslieferung auf stable gesetzt"
  - "2.0.0: 2026-05-05 - Zur zentralen Anwenderanleitung fuer GitBook Worker v2.4.0 ausgebaut"
  - "1.2.0: 2026-05-05 - Dockerfile.dynamic als Kundenpfad, AI-Reference-Schutz und v2.4.0-Verifikation ergaenzt"
  - "1.1.0: 2026-02-08 - publish.yml-Konfiguration und pdf_options-Anleitung ergaenzt"
  - "1.0.0: 2025-12-31 - init"
---

# GitBook Worker Anwenderanleitung v2.4.0

Diese Anleitung ist der zentrale Einstieg fuer Anwenderinnen und Anwender von
GitBook Worker v2.4.0. Sie beschreibt Installation, Projektstruktur,
Konfiguration, lokale PDF-Builds, Docker-Builds, Font-Pruefungen,
AI-Reference-QA und typische Fehlerbilder.

Der Dokumentstatus `stable` bedeutet: Die Anleitung ist als User-Manual-Fassung
fuer v2.4.0 freigegeben. Die Checkliste am Ende bleibt als Liefer- und
Support-Smoke fuer konkrete Kundenuebergaben erhalten.

## 1. Was GitBook Worker leistet

GitBook Worker ist ein Python-basiertes CLI-Werkzeug fuer reproduzierbare
PDF-Buchproduktion aus GitBook-kompatiblen Markdown-Projekten. Der typische
Einsatz ist ein Repository mit einem oder mehreren Sprachbaeumen wie `de/`,
`en/` oder extern eingebundenen Git-Quellen.

Die wichtigsten Funktionen:

- Markdown- und GitBook-Strukturen zu druckfertigen PDFs verarbeiten.
- Sprachbaeume ueber `content.yaml` auswaehlen.
- `publish.yml`-Profile fuer lokale, CI- oder Release-Laeufe verwenden.
- PDF-Ausgabe mit Pandoc und LuaLaTeX erzeugen.
- Emoji- und CJK-Fonts kontrolliert ueber `fonts.yml` einbetten.
- Font-Attribution und Lizenzhinweise generieren.
- AI-Reference-Pruefungen report-first ausfuehren.
- Builds lokal, in Docker oder in CI/CD vergleichbar betreiben.

Nicht im Fokus sind HTML-Hosting, interaktive Web-Publishing-Workflows oder
juristische Compliance-Audits. GitBook Worker liefert technische Pruefungen und
reproduzierbare Artefakte; fachliche, redaktionelle und rechtliche Freigaben
bleiben beim jeweiligen Projektteam.

## 2. Begriffe

| Begriff | Bedeutung |
|---|---|
| Repository Root | Wurzelverzeichnis des Buchprojekts, z. B. `C:\gitbook-worker` |
| Sprachbaum | Ordner eines Inhaltsstands, z. B. `de/` oder `en/` |
| `content.yaml` | Zentrale Liste der verfuegbaren Sprachbaeume |
| `book.json` | GitBook-kompatible Buchmetadaten pro Sprachbaum |
| `publish.yml` | Build-Profile, Projektmetadaten und PDF-Optionen pro Sprachbaum |
| Profil | Benannte Schrittfolge aus `publish.yml`, z. B. `local` oder `default` |
| Orchestrator | CLI-Einstieg fuer Validierung und Pipeline-Laeufe |
| Publisher | Pipeline-Schritt, der das PDF via Pandoc/LuaLaTeX erzeugt |
| Font Gate | PDF-Pruefung, ob konfigurierte Emoji- und CJK-Fonts eingebettet sind |

## 3. Voraussetzungen

### Lokal

- Windows, Linux oder macOS.
- Python 3.10 oder neuer; fuer v2.4.0 ist Python 3.11/3.12 empfohlen.
- Pandoc.
- TeX Live mit LuaLaTeX.
- Zugriff auf die konfigurierten Fonts oder einen erlaubten Downloadpfad.

### Optional fuer Docker

- Docker Desktop oder kompatibler Docker-Daemon.
- Genuegend Speicherplatz fuer ein TeX-Live/Pandoc-Image.
- Zugriff auf das Repository als gemountetes Arbeitsverzeichnis.

### Optional fuer AI-Reference-QA

- API-Key fuer den gewaehlten Provider.
- Erlaubnis, Referenztexte an den Provider zu senden.
- Projektentscheidung, ob nur Reports erzeugt oder Markdown-Dateien mit
  `--apply` geaendert werden duerfen.

## 4. Installation in einer sauberen Python-Umgebung

Fuehre die Installation pro Projekt in einer eigenen virtuellen Umgebung aus.
Das verhindert, dass alte lokale `tools`-Pakete oder globale Python-Pakete die
gelieferte Version ueberlagern.

### Windows PowerShell

```powershell
cd C:\Path\To\Project
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip uninstall -y gitbook-worker tools
```

Installation aus einem gelieferten Wheel:

```powershell
python -m pip install --force-reinstall dist\gitbook_worker-2.4.0-py3-none-any.whl
```

Installation direkt aus dem Repository:

```powershell
python -m pip install --force-reinstall .
```

### Bash

```bash
cd /path/to/project
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip uninstall -y gitbook-worker tools
python -m pip install --force-reinstall dist/gitbook_worker-2.4.0-py3-none-any.whl
```

## 5. Installation pruefen

Pruefe nach der Installation, welche Version und welche Module Python wirklich
laedt:

```powershell
python -c "import gitbook_worker, tools; print('version:', gitbook_worker.__version__); print('gitbook_worker:', gitbook_worker.__file__); print('tools shim:', tools.__file__)"
```

Erwartung:

- `version:` zeigt `2.4.0`.
- `gitbook_worker:` zeigt in die aktive `.venv` oder in das bewusst installierte
  Repository.
- `tools shim:` zeigt auf den Kompatibilitaets-Shim aus `gitbook_worker`, nicht
  auf ein fremdes globales Paket.

Zusaetzlich kann die CLI-Hilfe geprueft werden:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator --help
python -m gitbook_worker.tools.workflow_orchestrator --help-exit-codes
```

## 6. Empfohlene Projektstruktur

Ein robuster Buchstand folgt dieser Struktur:

```text
mein-buch/
  content.yaml
  de/
    book.json
    publish.yml
    CITATION.cff
    LICENSE
    LICENSE-CODE
    LICENSE-FONTS
    content/
      README.md
      SUMMARY.md
      kapitel-1/
        README.md
    publish/
  en/
    book.json
    publish.yml
    content/
      README.md
      SUMMARY.md
    publish/
  fonts-storage/
  logs/
```

Die Anwenderdokumentation gehoert in `docs/`. Engineering- und
Release-Vorbereitungsdokumente gehoeren unter `gitbook_worker/docs/`.

## 7. `content.yaml`

`content.yaml` liegt im Repository Root und legt fest, welche Sprachbaeume
bekannt sind und welcher Sprachbaum der Default ist.

```yaml
version: 1.1.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: German baseline content
  - id: en
    type: local
    uri: en/
    description: English content
  - id: ua
    type: git
    uri: github.com:owner/repository.git
    description: Remote content
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

Wichtige Regeln:

- `id` ist der Wert fuer `--lang`.
- `type: local` verweist auf einen Ordner im Repository.
- `type: git` wird nach `.gitbook-content/<id>` geklont.
- `credentialRef` benennt die Umgebungsvariable mit SSH-Key-Pfad oder Key-Inhalt.
- Sprachbaeume mit `build: false` sind Samples oder Edge-Cases und werden nicht
  als Standard-Publish-Ziel behandelt.

## 8. `book.json`

`book.json` liegt pro Sprachbaum und liefert GitBook-kompatible Metadaten. Viele
Werte koennen in `publish.yml` ueberschrieben werden, bleiben aber als Fallback
nuetzlich.

```json
{
  "schema_version": "1.0.0",
  "title": "Mein Buch",
  "author": "Autorenname",
  "language": "de-DE",
  "description": "Kurze Beschreibung des Buchs.",
  "root": "content/",
  "structure": {
    "readme": "README.md",
    "summary": "SUMMARY.md"
  }
}
```

## 9. `publish.yml`

`publish.yml` ist die zentrale Steuerdatei fuer einen Sprachbaum. Sie enthaelt
Profile, Projektmetadaten und Publish-Eintraege.

```yaml
version: 0.1.1

profiles:
  local:
    description: Lokaler Build ohne externe CI-Schritte.
    steps:
      - converter
      - generate_attribution
      - publisher
  default:
    description: Voller Standardlauf.
    steps:
      - check_if_to_publish
      - ensure_readme
      - update_citation
      - converter
      - engineering-document-formatter
      - generate_attribution
      - publisher

project:
  name: "Mein Buch"
  author: "Jane Doe"
  version: "1.0.0"
  license: "CC BY-SA 4.0"
  date: "2026-05-05"

publish:
  - build: true
    out_format: pdf
    path: content/
    out_dir: publish/
    out: mein-buch.pdf
    source_type: folder
    source_format: markdown
    use_summary: true
    generate_attribution: true
    pdf_options:
      documentclass: book
      fontsize: 12pt
      geometry: "a4paper, margin=2.5cm"
      papersize: a4
      toc: true
      toc-depth: 3
      numbersections: true
      colorlinks: true
      linkcolor: blue
      urlcolor: blue
      lang: de-DE
      mainfont: "DejaVu Serif"
      sansfont: "DejaVu Sans"
      monofont: "DejaVu Sans Mono"
      mainfont_fallback: "Twemoji Mozilla;ERDA CC-BY CJK"
      abort_if_missing_glyph: true
```

Die vollstaendige Schluesselreferenz steht in der
[Configuration Reference](configuration-reference.md). Fuer einzelne
Konfigurationsdateien siehe [docs/configs/](configs/README.md).

## 10. Manifest validieren

Vor einem Build sollte das Manifest validiert werden:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator validate --root C:\Path\To\Project --content-config content.yaml --lang de --profile local
```

Alle Profile eines Manifests pruefen:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator validate --root C:\Path\To\Project --content-config content.yaml --lang de --all-profiles
```

Wenn `--lang` fehlt, verwendet der Orchestrator `content.yaml:default`.

## 11. Lokaler PDF-Build

Der normale lokale Lauf startet den Orchestrator aus dem Repository Root:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run --root C:\Path\To\Project --content-config content.yaml --lang de --profile local
```

Nur einen einzelnen Schritt ausfuehren:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run --root C:\Path\To\Project --content-config content.yaml --lang de --profile local --step publisher
```

Dry-Run ohne Artefakte:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run --root C:\Path\To\Project --content-config content.yaml --lang de --profile local --dry-run
```

Wichtig: `--profile docker` ist nur ein Profilname. Es startet keinen Container.
Fuer echte Docker-Laeufe wird das Docker-CLI-Modul aus Abschnitt 12 verwendet.

## 12. Docker-Builds

Docker ist optional, aber fuer Release- und kundennahe Reproduzierbarkeit der
empfohlene isolierte Pfad.

Image bauen und Orchestrator im Container starten:

```powershell
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile local --lang de --content-config content.yaml --use-dynamic --rebuild
```

Nur das Docker-Image bauen:

```powershell
python -m gitbook_worker.tools.docker.run_docker build --use-dynamic --rebuild
```

Interaktive Shell im Container:

```powershell
python -m gitbook_worker.tools.docker.run_docker shell --use-dynamic
```

Hinweise:

- Fuer pip-/sdist-basierte Docker-CI bitte mindestens `2.4.1` verwenden. `2.4.1`
  stellt sicher, dass die Dockerfiles und `gitbook_worker/tools/requirements.txt`
  im Lieferpaket enthalten sind.
- `--use-dynamic` ist der v2.4.x-Release-Pfad.
- `Dockerfile.dynamic` verwendet `/usr/local/texlive/current` und keinen
  hartcodierten TeX-Live-Jahrgang.
- Das legacy `Dockerfile` ist deprecated und nicht fuer neue Anwenderlaeufe
  gedacht.
- `Dockerfile.python` ist nur fuer leichte Python-Testcontainer gedacht und
  enthaelt bewusst kein Pandoc/TeX Live.
- Docker-Befehle werden aus dem Repository Root ausgefuehrt; das Arbeitsverzeichnis
  wird in den Container gemountet.

## 13. Fonts synchronisieren und Attribution erzeugen

Alle Fonts muessen in `gitbook_worker/defaults/fonts.yml` konfiguriert sein. Das
ist die Single Source of Truth fuer Font-Namen, Pfade, Lizenzen und Download-URLs.
Harte System-Fallbacks sind fuer reproduzierbare Builds nicht vorgesehen.

Fonts synchronisieren:

```powershell
gitbook-worker-fonts sync --manifest de\publish.yml --repo-root C:\Path\To\Project --search-path .github\fonts
```

Attribution-Dateien manuell erzeugen:

```powershell
gitbook-worker-fonts generate-attribution --out-dir de\publish
```

Wenn LuaLaTeX eine Font nicht findet, hilft nach Installation oder Sync oft:

```powershell
luaotfload-tool --update --force
```

Die technischen Hintergruende stehen in
[lua-font-cache.md](../gitbook_worker/docs/attentions/lua-font-cache.md).

## 14. PDF-Font-Gate nach einem Build

Nach einem PDF-Build sollte die Font- und Textsignal-Pruefung laufen. Fuer den
deutschen Beispielbuild:

```powershell
python -m gitbook_worker.tools.testing.pdf_validator --pdf de\publish\das-sample-buch.pdf
```

Mit Log-Scan:

```powershell
python -m gitbook_worker.tools.testing.pdf_validator --pdf de\publish\das-sample-buch.pdf --log de\publish\_latex-debug
```

Als JSON fuer CI oder Support:

```powershell
python -m gitbook_worker.tools.testing.pdf_validator --pdf de\publish\das-sample-buch.pdf --json
```

Erwartete Signale fuer v2.4.0:

- Der konfigurierte Emoji-Font `Twemoji Mozilla` ist eingebettet.
- Der konfigurierte CJK-Font `ERDA CC-BY CJK` ist eingebettet.
- Der PDF-Textscan findet ein positives CJK-Signal.
- Neue Missing-Glyph- oder `.notdef`-Signale werden als Warnung oder, mit
  `--fail-on-log-pattern`, als Fehler sichtbar.

## 15. AI-Reference-QA

Der AI-Reference-Checker ist in v2.4.0 report-first. Ohne `--apply` werden keine
Markdown-Dateien geaendert; Vorschlaege landen im JSON-Report.

No-network Precheck:

```powershell
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files de\content\README.md --precheck-only --json-report logs\ai-reference-precheck.json
```

Inline-Referenzen, Markdown-Links und Frontmatter-DOIs einbeziehen:

```powershell
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files de\content\README.md --include-inline-references --include-markdown-links --include-frontmatter-dois --precheck-only --json-report logs\ai-reference-inline.json
```

Provider-Beispiele:

```powershell
$env:AI_REFERENCE_API_KEY = "<secret>"
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files de\content\README.md --ai-provider openai --model gpt-4o-mini --json-report logs\ai-reference-openai.json
```

```powershell
$env:GEMINI_API_KEY = "<secret>"
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files de\content\README.md --ai-provider genai --model gemini-2.5-flash --json-report logs\ai-reference-genai.json
```

```powershell
$env:MISTRAL_API_KEY = "<secret>"
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files de\content\README.md --ai-provider mistral --model mistral-small-latest --json-report logs\ai-reference-mistral.json
```

Batch- und Resume-Lauf:

```powershell
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files-list logs\reference-files.txt --max-tasks 100 --resume-from-report logs\ai-reference-report.json --as-of-date 2026-05-05 --json-report logs\ai-reference-report-next.json
```

Rate-Limit-Haertung:

```powershell
python -m gitbook_worker.tools.quality.ai_references --root C:\Path\To\Project --files-list logs\reference-files.txt --requests-per-minute 20 --max-consecutive-429 3 --cooldown-on-429-seconds 60 --json-report logs\ai-reference-report.json
```

Sicherheits- und Datenschutzhinweise:

- API-Keys und tokenartige Felder werden in JSON-Reports redigiert.
- Provider-Fehlertexte redigieren rohe API-Keys und `?key=` / `api_key=` Werte.
- `AI_API_KEY`, `AI_URL` und `AI_PROVIDER` werden als Kompatibilitaets-Aliase
  akzeptiert.
- Die Pruefung ist ein technischer Schutz gegen Secret-Leaks und ein
  Referenz-QA-Werkzeug. Sie ist kein juristisches EU-/DSGVO-Audit.
- Markdown-Dateien werden nur mit `--apply` veraendert.

## 16. Logs, Exit-Codes und Diagnose

Orchestrator-Laeufe schreiben Logs in das konfigurierte oder automatische
Logverzeichnis. Bei Supportfaellen sind diese Punkte besonders wichtig:

- Startup-Banner mit GitBook-Worker-Version.
- Aufgeloestes `root`, `content_config`, `manifest`, `profile` und `language`.
- Ausgefuehrte Profile und Schritte.
- Pandoc-/LuaLaTeX-Fehlerausgaben.
- PDF-Font-Gate-Ausgabe.
- AI-Reference-JSON-Report, falls Referenz-QA betroffen ist.

Exit-Codes anzeigen:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator --help-exit-codes
python -m gitbook_worker.tools.quality.ai_references --help-exit-codes
```

Die zentrale Tabelle fuer Diagnose und Healing-Steps liegt in
[exit-codes.md](../gitbook_worker/docs/attentions/exit-codes.md).

## 17. Typische Fehler und schnelle Abhilfe

| Symptom | Wahrscheinliche Ursache | Abhilfe |
|---|---|---|
| Falsches `tools`-Modul wird importiert | Globale Altinstallation oder Paketname `tools` | `.venv` aktivieren, `python -m pip uninstall -y tools`, Importpfad pruefen |
| `project.license fehlt` | Pflichtfeld fehlt in `publish.yml` | `project.license` setzen |
| Manifest wird nicht gefunden | Falscher Root oder falsches `--lang` | `--root`, `--content-config` und `content.yaml` pruefen |
| Profil faellt auf `default` zurueck | Gewuenschtes Profil fehlt in `publish.yml` | Profil anlegen oder korrekt benennen |
| PDF zeigt fehlende Glyphen | Font fehlt oder LuaTeX-Cache veraltet | Fonts syncen und `luaotfload-tool --update --force` ausfuehren |
| Docker findet Fonts nicht | Font-Cache/Font-Ordner fehlen im Workspace | `gitbook-worker-fonts sync` ausfuehren und Docker mit `--use-dynamic --rebuild` starten |
| AI-Reference bricht wegen 429 ab | Provider-Rate-Limit | `--requests-per-minute`, `--max-consecutive-429` und Backoff-Optionen setzen |
| Markdown wurde nicht geaendert | Report-first Default | Nur mit `--apply` werden Vorschlaege geschrieben |

Mehr konkrete Fehlerbilder stehen in den [FAQs](FAQs.md).

## 18. Update von einer aelteren Version

Empfohlene Reihenfolge:

1. Release Notes lesen: [v2.4.0 Release Notes](releases/v2.4.0.md).
2. Recovery-Punkt im Projekt setzen, bevor Build- oder Migrationslaeufe starten.
3. Neue Version in einer sauberen `.venv` installieren.
4. Importpfade und Version pruefen.
5. `validate` fuer die betroffenen Sprachbaeume ausfuehren.
6. Fonts synchronisieren.
7. Lokalen PDF-Build starten.
8. PDF-Font-Gate ausfuehren.
9. Optional Docker-Build mit `Dockerfile.dynamic` ausfuehren.
10. AI-Reference-QA zuerst report-only testen.

## 19. Release-Verifikation v2.4.0

Der v2.4.0-Releasekandidat wurde lokal mit diesen Signalen geprueft:

- Non-slow Test-Suite: `515 passed, 11 skipped, 10 deselected, 4 warnings`.
- Docker-Tests inklusive echtem `Dockerfile.dynamic` Build/Run: `4 passed`.
- Sauberer Wheel- und sdist-Build.
- Wheel-Smoke in frischer virtueller Umgebung.
- Deutscher und englischer PDF-Build.
- PDF-Font-Gates fuer Twemoji und ERDA CC-BY CJK.
- Positives CJK-Textsignal in beiden Sample-PDFs.
- AI-Reference-Secret-Redaction und Provider-Fehler-Redaction.

## 20. Review- und Smoke-Checkliste fuer diese Anleitung

Vor dem Statuswechsel von `review-ready` auf `stable` sollten diese Punkte fuer
eine konkrete Lieferung oder ein Kundenprojekt geprueft werden:

- [ ] Wheel-Dateiname und Versionsnummer stimmen mit der ausgelieferten Version
      ueberein.
- [ ] Installationsbefehle wurden in einer frischen `.venv` getestet.
- [ ] Importpruefung zeigt keine fremden `tools`-Module.
- [ ] `workflow_orchestrator --help` und `--help-exit-codes` funktionieren.
- [ ] `validate` funktioniert fuer mindestens einen lokalen Sprachbaum.
- [ ] Lokaler PDF-Build erzeugt das erwartete PDF.
- [ ] PDF-Font-Gate bestaetigt Emoji- und CJK-Font-Einbettung.
- [ ] Docker-Lauf mit `--use-dynamic` funktioniert, falls Docker Teil der
      Lieferung ist.
- [ ] AI-Reference-Precheck schreibt einen JSON-Report ohne Markdown-Aenderung.
- [ ] Keine API-Keys oder Tokens erscheinen in Reports oder Logs.
- [ ] Supportteam kann die Quick-Diagnosepunkte aus Abschnitt 16 nachvollziehen.

## 21. Quick-Support-Fragen

Wenn ein Lauf fehlschlaegt, klaere zuerst:

- Welche GitBook-Worker-Version wird geladen?
- Welche Python-Umgebung ist aktiv?
- Welcher Root, welche Sprache und welches Profil wurden verwendet?
- Welche `publish.yml` wurde aufgeloest?
- Ist `project.license` gesetzt?
- Existieren Pandoc, LuaLaTeX und die konfigurierten Fonts?
- Wurde der LuaTeX-Fontcache aktualisiert?
- Sind Docker und lokaler Build beide betroffen oder nur einer davon?
- Gibt es einen AI-Reference-Report, und ist der Lauf report-only oder mit
  `--apply` erfolgt?
