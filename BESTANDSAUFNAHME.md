---
version: 1.0.0
date: 2026-05-04
status: inventory
history:
  - "1.0.0: 2026-05-04 - Erste komplette Bestandsaufnahme des Repository-Standes v2.3.0"
---

# GitBook Worker - Bestandsaufnahme und Ausblick

## Kurzfazit

GitBook Worker ist aktuell ein Python-basiertes CLI-Toolkit fuer reproduzierbare
Markdown-zu-PDF-Publikationen. Der Schwerpunkt liegt auf GitBook-kompatiblen
Buchprojekten mit mehrsprachigen Inhaltsbaeumen, klar versionierten
Konfigurationen, automatischer PDF-Erzeugung via Pandoc und LuaLaTeX,
Font-Lizenz-Compliance, Emoji-/Fallback-Font-Unterstuetzung, Docker-faehigen
Builds und CI-gestuetzter Qualitaetssicherung.

Der Stand des Repos ist v2.3.0 "Pfadtreu". Die Release-Linie adressiert vor
allem stabile Pfadauflosung bei Einzeldatei-Publishing, explizite Steuerung des
GitBook-Rename-Schritts und robustere Font-Fallbacks. Die Codebasis wirkt
funktional breit, dokumentiert und testnah, hat aber einige sichtbar offene
Kanten bei CI-Pfaden, Packaging-Metadaten und der weiteren Konsolidierung der
historisch gewachsenen Dokumentation.

## Datenbasis dieser Aufnahme

Geprueft wurden insbesondere:

- [README.md](README.md)
- [setup.cfg](setup.cfg)
- [pyproject.toml](pyproject.toml)
- [content.yaml](content.yaml)
- [de/publish.yml](de/publish.yml)
- [en/publish.yml](en/publish.yml)
- [docs/HANDBOOK.md](docs/HANDBOOK.md)
- [docs/configuration-reference.md](docs/configuration-reference.md)
- [docs/releases/v2.3.0.md](docs/releases/v2.3.0.md)
- [gitbook_worker/__init__.py](gitbook_worker/__init__.py)
- [gitbook_worker/defaults/fonts.yml](gitbook_worker/defaults/fonts.yml)
- [gitbook_worker/defaults/smart.yml](gitbook_worker/defaults/smart.yml)
- [gitbook_worker/defaults/docker_config.yml](gitbook_worker/defaults/docker_config.yml)
- [gitbook_worker/tools/workflow_orchestrator/orchestrator.py](gitbook_worker/tools/workflow_orchestrator/orchestrator.py)
- [gitbook_worker/tools/publishing/fonts_cli.py](gitbook_worker/tools/publishing/fonts_cli.py)
- [.github/workflows/orchestrator.yml](.github/workflows/orchestrator.yml)
- [.github/workflows/test.yml](.github/workflows/test.yml)

Zusaetzlich wurde die sichtbare Datei- und Teststruktur ueber die VS-Code-Suche
inventarisiert. Zum Zeitpunkt dieser Aufnahme waren keine uncommitted Changes im
Git-Worktree vorhanden.

## Was GitBook Worker aktuell leistet

### 1. Markdown- und GitBook-Projekte zu PDF publizieren

Der Kernnutzen ist die Umwandlung von Markdown-Buchprojekten in druckfertige
PDFs. Die Pipeline kombiniert GitBook-Strukturen wie `content/`, `SUMMARY.md`
und `book.json` mit `publish.yml`-gesteuerten PDF-Optionen. Der Publisher baut
ueber Pandoc und LuaLaTeX, setzt Fonts, Metadaten, Inhaltsverzeichnis,
Kapitelreihenfolge, Assets und optionale kombinierte Markdown-Artefakte um.

Aktuell sichtbar implementierte Zielausgabe: PDF. Andere Formate sind in der
Konfigurationsreferenz nicht als produktive Ausgabe ausgewiesen.

### 2. Orchestrator als zentrale CLI-Schicht

Das Hauptkommando ist ueber `setup.cfg` als Console Script registriert:

```bash
gitbook-worker = gitbook_worker.tools.workflow_orchestrator.orchestrator:main
```

Der Orchestrator unterstuetzt die Subcommands `run` und `validate`. Ohne
explizites Subcommand faellt er auf `run` zurueck. Wichtige Optionen sind:

- `--root` fuer den Repository-Root
- `--content-config` fuer `content.yaml`
- `--lang` beziehungsweise `--language` fuer die Sprach-ID
- `--manifest` fuer ein explizites `publish.yml`
- `--profile` fuer Profilnamen aus dem Manifest
- `--step` fuer gezielte Einzelschritte
- `--dry-run` fuer Simulation
- `--isolated` fuer kontrollierte Python-Subprozesse
- `--no-gitbook-rename` fuer pfadtreue Einzeldatei- und Sonderfaelle
- `--help exit-codes` ueber die Exit-Code-Hilfe

Die aktuell verdrahteten Orchestrator-Schritte sind:

- `check_if_to_publish`: Git-Diff-basierte Build-Flag-Logik
- `ensure_readme`: README-Generierung in Inhaltsbaeumen
- `update_citation`: Aktualisierung von `CITATION.cff` im Publish-Ordner
- `ai-reference-check`: KI-/Bibliographie-Referenzpruefung
- `converter`: Manifest-Dump und Asset-Konvertierung
- `engineering-document-formatter`: Frontmatter-Injection fuer Markdown-Dateien
- `generate_attribution`: Font-Attribution in Publish-Ziele schreiben
- `publisher`: PDF-Pipeline ausfuehren

### 3. Profilbasierte Build-Pipeline

Die Sprachmanifeste [de/publish.yml](de/publish.yml) und
[en/publish.yml](en/publish.yml) definieren drei zentrale Profile:

- `default`: komplette Orchestrator-Pipeline fuer CI-nahe Nutzung
- `local`: lokaler Lauf ohne Registry-Zugriff, mit Converter, Attribution und Publisher
- `publisher`: nur Attribution und Publisher, geeignet fuer reduzierte Publish-Laeufe

Das Standardprofil umfasst die volle Kette aus Publish-Flag-Pruefung,
README-Sicherung, Citation-Update, Konvertierung, Engineering-Formatierung,
Attribution und PDF-Erzeugung. Das lokale Profil laesst die Git-/CI-nahen
Vorschritte aus.

### 4. Mehrsprachige Inhalte und Remote-Content

[content.yaml](content.yaml) ist die zentrale Sprach- und Quellenkonfiguration.
Der aktuelle Root-Stand kennt:

- `de`: lokaler deutscher Basisinhalt
- `en`: lokaler englischer Inhalt
- `de-edge-cases`: lokale deutsche Edge-Case-Samples, standardmaessig `build: false`
- `en-edge-cases`: lokale englische Edge-Case-Samples, standardmaessig `build: false`
- `ua`: Remote-Content via Git, abgesichert ueber `GITBOOK_CONTENT_UA_DEPLOY_KEY`

Damit kann der Worker lokale und remote gepflegte Sprachbaeume in ein
gemeinsames Build-Modell einordnen. Remote-Inhalte werden ueber die
Content-Discovery- und Language-Context-Utilities aufgeloest.

### 5. Font-Management und Lizenz-Compliance

[gitbook_worker/defaults/fonts.yml](gitbook_worker/defaults/fonts.yml) ist als
Single Source of Truth fuer alle Fonts angelegt. Jeder Font-Eintrag traegt Name,
Lizenz, Lizenz-URL, Quelle beziehungsweise Download-URL, Version und Pfade.
Konfigurierte Fonts umfassen aktuell unter anderem:

- ERDA CC-BY CJK
- ERDA CC-BY Indic
- ERDA CC-BY Ethiopic
- Twemoji Mozilla
- DejaVu Serif
- DejaVu Sans
- DejaVu Sans Mono

Die Font-Schicht leistet mehr als Pfadauflosung: Sie stuetzt reproduzierbare
Builds, klaert Attribution, verhindert stille System-Font-Fallbacks und bereitet
Fonts fuer lokale, CI- und Docker-Laeufe vor.

Zweites Console Script:

```bash
gitbook-worker-fonts = gitbook_worker.tools.publishing.fonts_cli:main
```

Dieses Font-CLI bietet aktuell:

- `sync`: Fonts aus `fonts.yml` und optionalen Manifest-Overrides aufloesen,
  herunterladen und cachen
- `generate-attribution`: `ATTRIBUTION.md` und Lizenzdateien aus Font-Metadaten erzeugen

### 6. Emoji-, Glyphen- und Fallback-Verhalten

Die Codebasis enthaelt eine eigene Emoji-Toolgruppe fuer Scans, Reports,
Inline-Emoji-Behandlung und Font-Inventur. PDF-Builds koennen Farb-Emoji ueber
Twemoji Mozilla nutzen. Die PDF-Optionen in den Sprachmanifesten aktivieren
`emoji_color: true` und definieren eine Fallback-Kette mit Twemoji, ERDA CJK,
ERDA Indic und ERDA Ethiopic.

Die Dokumentation beschreibt das Zielverhalten klar: fehlende Glyphen sollen
erkannt, protokolliert und je nach `abort_if_missing_glyph` entweder als Fehler
behandelt oder als Warnung dokumentiert werden. v2.3.0 enthaelt zudem einen
Fix, damit RawFeature-Fallbacks nicht gesetzt werden, wenn Lua-Fallbacks
deaktiviert sind.

### 7. GitBook-Struktur, Dokumenttypen und SUMMARY-Erzeugung

Die Publishing-Konfiguration unterstuetzt GitBook-typische Felder wie
`use_summary`, `use_book_json`, `summary_mode` und
`summary_appendices_last`. Zusaetzlich ist ein Dokumenttypen-System sichtbar,
das Abschnitte wie Widmung, Vorwort, Kapitel, Anhaenge, Glossar,
Bibliographie, Index, Attribution, Errata, Release Notes und Kolophon ordnen
kann.

Die deutschen und englischen Manifeste nutzen `use_document_types: true` und
lokalisierte Abschnittstitel. Automatische Nummerierung von Kapiteln,
Anhaengen und Teilen ist konfiguriert.

### 8. Konverter, Assets und Hilfswerkzeuge

Der Converter-Bereich umfasst unter anderem:

- CSV-zu-Markdown- und Chart-Konvertierung
- Asset-Konvertierung und Asset-Kopie
- Manifest-Dump fuer nachgelagerte Tools

Die Publish-Eintraege koennen Assets definieren, etwa
`content/.gitbook/assets`, und diese in die Ausgabe uebernehmen. Die Pipeline
bezieht Ressourcenpfade fuer Pandoc ein, damit Bilder und Begleitdateien im PDF
verfuegbar bleiben.

### 9. Qualitaetssicherung und Diagnose

Die Tool-Schicht enthaelt mehrere QA- und Diagnosemodule:

- Link-Audit fuer Links, Bilder, Heading-Kollisionen und TODO-Hinweise
- Quellen-/Bibliographie-Export
- AI-Reference-Pruefungen
- Frontmatter-Checker
- PDF-TOC-Extraktor
- Appendix Layout Inspector
- Image-Info- und Asset-Copy-Utilities
- Exit-Code-Tabelle und Exit-Code-Hilfe

Fuer PDF-Inhaltsverzeichnisse existieren VS-Code-Tasks fuer deutsche und
englische Artefakte. Die Taskliste enthaelt ausserdem lokale PDF-Builds fuer
`de` und `en`.

### 10. Docker- und CI-Faehigkeit

Der Docker-Bereich bietet statische und dynamische Dockerfiles. Das dynamische
Dockerfile ist die zentrale CI-Variante und richtet TeX/Pandoc sowie Fonts aus
der Konfiguration ein. [gitbook_worker/defaults/docker_config.yml](gitbook_worker/defaults/docker_config.yml)
enthaelt Template-Namen fuer Images und Container.

Die GitHub Actions umfassen:

- [.github/workflows/orchestrator.yml](.github/workflows/orchestrator.yml):
  baut ein GHCR-Publisher-Image oder lokal ein Fallback-Image, startet den
  Orchestrator im Container und committet Publish-Artefakte bei Aenderungen.
- [.github/workflows/test.yml](.github/workflows/test.yml):
  definiert Unit-/Integrationstests, Language-Smoke-Validierung, Emoji-Harness,
  QA-Checks und mypy-Type-Check.

### 11. Testabdeckung

Die sichtbare Teststruktur liegt ueberwiegend unter
[gitbook_worker/tests](gitbook_worker/tests). Die Suche zeigt 59 Python-Testdateien
und deckt unter anderem ab:

- Orchestrator und Manifest-Validierung
- Pipeline, Publisher und PDF-Integration
- Font-Konfiguration, Font-Fallbacks und Attribution
- Emoji-Rendering, Emoji-Reports und visuelle Regressionen
- Smart-Utilities fuer Git, Manifest, Content, Book und Publisher
- Markdown-Kombination, LaTeX-Escaping und PDF-Option-Passthrough
- Docker-Container-Verhalten
- Exit-Codes und Konfigurationsvollstaendigkeit
- Core-Ports fuer SVG-zu-PDF, Repo-Root und PDF-TOC

Die Release Notes fuer v2.3.0 nennen als damaligen Teststand 463 bestandene,
11 uebersprungene und 0 fehlgeschlagene Tests. Diese Aufnahme hat keinen neuen
Testlauf ausgefuehrt, weil nur Dokumentation ergaenzt wurde.

## Repository-Bestand nach Bereichen

### Root und Paketierung

- [README.md](README.md): zweisprachige Projektuebersicht, Schnellstart,
  Zielgruppen, Installation und Release-Verweise
- [setup.cfg](setup.cfg): Paketmetadaten, Dependencies, Console Scripts
- [pyproject.toml](pyproject.toml): setuptools Build-System
- [pytest.ini](pytest.ini): Testmarker fuer `slow`, `unit`, `integration`, `manual`
- [content.yaml](content.yaml): zentrale Sprach- und Quellenliste
- [build-pdf.ps1](build-pdf.ps1) und [build-pdf.sh](build-pdf.sh): Wrapper fuer PDF-Builds

### Sprach- und Kundenbaeume

- [de](de): deutscher Sprachbaum mit `book.json`, `publish.yml`, Content,
  Font-Storage und Publish-Artefakten
- [en](en): englischer Sprachbaum mit analoger Struktur
- [de-edge-cases](de-edge-cases) und [en-edge-cases](en-edge-cases): isolierte
  Edge-Case-Samples, standardmaessig nicht gebaut
- [customer-de](customer-de) und [customer-flat](customer-flat): Kunden- und
  Beispielstrukturen fuer reale oder flachere Projektlayouts
- [qa-customer-feedback](qa-customer-feedback): dokumentierte Kundenfeedback-/QA-Faelle

### Python-Paket

- [gitbook_worker/core](gitbook_worker/core): application/ports-Schicht fuer
  fachliche Kernoperationen wie PDF-TOC, Repo-Root und SVG-zu-PDF
- [gitbook_worker/adapters](gitbook_worker/adapters): konkrete Adapter fuer PDF,
  SVG und Dateisystem
- [gitbook_worker/tools/workflow_orchestrator](gitbook_worker/tools/workflow_orchestrator):
  Haupt-CLI und Ablaufsteuerung
- [gitbook_worker/tools/publishing](gitbook_worker/tools/publishing): Publisher,
  Pipeline, Markdown-Kombination, GitBook-Style, Fonts, Attribution,
  Dokumenttypen und PDF-Vorverarbeitung
- [gitbook_worker/tools/converter](gitbook_worker/tools/converter): Konverter fuer
  Assets und CSV/Charts
- [gitbook_worker/tools/quality](gitbook_worker/tools/quality): Link-, Quellen-
  und Referenzpruefungen
- [gitbook_worker/tools/emoji](gitbook_worker/tools/emoji): Emoji-Scans,
  Reports und Inline-Behandlung
- [gitbook_worker/tools/docker](gitbook_worker/tools/docker): Dockerfiles,
  Docker-CLI, Setup und Diagnostik
- [gitbook_worker/tools/utils](gitbook_worker/tools/utils): Smart-Utilities,
  Runner, Git, SemVer, Language Context, Asset Copy, PDF-TOC
- [gitbook_worker/tools/validators](gitbook_worker/tools/validators):
  Frontmatter-Validierung
- [gitbook_worker/tests](gitbook_worker/tests): Unit-, Integration- und
  Regressionstests

### Dokumentation

- [docs](docs): nutzer- und kundenseitige Dokumentation, Konfigurationsreferenz,
  Handbuch, FAQs, Releases und Features
- [docs/configs](docs/configs): per-Datei-Konfigurationsdokumentation
- [docs/releases](docs/releases): Release Notes von v2.0.0 bis v2.3.0
- [gitbook_worker/docs](gitbook_worker/docs): Engineering-Dokumente, Architektur,
  Sprintplaene, Backlog, Release-Prozedur und historische Archive
- [gitbook_worker/docs/attentions](gitbook_worker/docs/attentions): Diagnose- und
  Attention-Dokumente wie Exit-Codes und Lua-Font-Cache

### Fonts und Assets

- [fonts-storage](fonts-storage): lokaler Font-Storage fuer DejaVu, Twemoji und
  Fontconfig-Dateien
- [.github/fonts](.github/fonts): ERDA-Fontquellen, Generator- und Dokuanteile
- [build/emoji-assets](build/emoji-assets): generierte oder vorbereitete
  Emoji-/Build-Assets

## Aktuelle Staerken

- Klare CLI-Zentrierung: `gitbook-worker` ist der produktive Einstiegspunkt,
  waehrend Modulaufrufe fuer Spezialfaelle erhalten bleiben.
- Konfigurationsvollstaendigkeit ist systematisch dokumentiert, inklusive Status
  pro Schluessel und Versionshistorie.
- Font-Compliance ist ein ernsthaft behandeltes Kernthema statt ein spaeter
  Build-Nebeneffekt.
- Die Pipeline ist mehrsprachig und fuer lokale, Docker- und CI-Laeufe gedacht.
- Edge-Case-Sprachbaeume und viele Regressionstests zeigen, dass PDF-, Font-,
  Emoji- und Pfadfaelle aktiv abgesichert werden.
- Der Orchestrator trennt Profile, Schritte und Manifestvalidierung sauber genug,
  um laengere Workflows schrittweise laufen zu lassen.
- Die Dokumentation ist fuer Kundenbetrieb, Konfiguration, Releases und
  Engineering-Hintergruende bereits breit vorhanden.

## Sichtbare Risiken und offene Punkte

### 1. CI-Testpfad pruefen

In [.github/workflows/test.yml](.github/workflows/test.yml) ruft der Unit-Test-Job
`pytest tests -q ...` auf. Die sichtbaren Tests liegen jedoch unter
[gitbook_worker/tests](gitbook_worker/tests). Das sollte geprueft werden, weil
ein falscher Pfad im CI entweder Tests ueberspringen oder den Job unerwartet
scheitern lassen kann.

### 2. Dokumentation enthaelt teils historische Pfadangaben

[docs/HANDBOOK.md](docs/HANDBOOK.md) spricht im Schnellueberblick ebenfalls von
Tests unter `tests/`, waehrend die aktuelle Struktur [gitbook_worker/tests](gitbook_worker/tests)
zeigt. Das ist kein Laufzeitfehler, aber ein Onboarding-Risiko.

### 3. Packaging-Lizenzmetadaten harmonisieren

[setup.cfg](setup.cfg) nennt `license = CC-BY-SA-4.0`, waehrend [LICENSE](LICENSE)
und [LICENSE-CODE](LICENSE-CODE) MIT ausweisen. Inhalt, Code und Fonts haben
bewusst getrennte Lizenzdateien; die Paketmetadaten sollten diesen Stand aber
eindeutig abbilden, damit Distribution und README keine widerspruechlichen
Signale senden.

### 4. Docker-Profilfelder sind teilweise deklarativ

Die Konfigurationsreferenz weist `profiles.<name>.docker.*` als deklarativ fuer
CI aus. Das ist in Ordnung, sollte aber bei Ausbau von `run_docker.py` bewusst
entschieden werden: entweder konsequent Python-seitig nutzen oder dauerhaft als
CI-Metadaten kennzeichnen.

### 5. Historischer Dokumentationsbestand bleibt umfangreich

Das Archiv unter [gitbook_worker/docs/archive](gitbook_worker/docs/archive) ist
wertvoll, kann aber Suchergebnisse und Orientierung verwischen. Fuer neue
Beitragende sollte klar bleiben: aktuelle Nutzer-Doku liegt unter [docs](docs),
aktuelle Engineering-Doku unter [gitbook_worker/docs](gitbook_worker/docs),
Archive sind nur Hintergrund.

### 6. PyPI-/Wheel-Pfad weiter schaerfen

Die Release-Prozedur beschreibt Build, Wheel-Smoke-Test und Versionierung. Der
Smart-Font-Stack und die Kundeninstallation deuten bereits Richtung besserer
Installierbarkeit. Fuer externe Nutzung waere eine nochmals geglaettete
Distribution mit eindeutigen Extras, Font-Sync-Hinweisen und Smoke-Kommandos
der naechste logische Schritt.

## Ausblick

### Kurzfristig

- CI-Testpfad und Handbuchpfade auf [gitbook_worker/tests](gitbook_worker/tests)
  harmonisieren.
- Lizenzmetadaten in [setup.cfg](setup.cfg), [README.md](README.md) und den
  Lizenzdateien eindeutig ausrichten.
- Einen schnellen Smoke-Abschnitt fuer `gitbook-worker validate --lang de`,
  `gitbook-worker validate --lang en` und `gitbook-worker-fonts sync` in der
  Hauptdokumentation staerken.
- Die vorhandenen VS-Code-Tasks fuer lokale PDF-Builds und TOC-Pruefung in der
  Dokumentation sichtbarer machen.

### Mittelfristig

- Docker-Konfiguration entscheiden: CI-only deklarativ halten oder in
  `run_docker.py` als echte Profilsteuerung nutzbar machen.
- Font-Supply-Chain haerten, insbesondere durch konsequente `sha256`-Felder fuer
  herunterladbare Fonts.
- Remote-Content-Flows fuer `type: git` weiter dokumentieren, inklusive
  Credential-Fehlerbildern und Cache-Verhalten.
- QA-Reports fuer Links, Quellen, AI-Referenzen und PDF-TOC in einem einheitlichen
  Report-Format buendeln.

### Laengerfristig

- GitBook Worker als installierbares Publishing-Produkt weiter schaerfen:
  reproduzierbarer Wheel-Flow, klarer Font-Sync nach Installation, kleine
  Beispielprojekte und robuste Smoke-Tests.
- Die hexagonale Architektur weiter ausbauen: fachliche Ports und Adapter sind
  sichtbar begonnen, koennten aber noch mehr der Tool-Schicht entkoppeln.
- Mehr Ausgabeziele nur dann ergaenzen, wenn sie dieselbe Qualitaet wie PDF
  erreichen koennen. Aktuell ist PDF die klare Staerke und sollte nicht durch
  halb implementierte Formate verwaessert werden.
- Konfigurationsvollstaendigkeit als dauerhaftes Gate pflegen: jeder neue Key
  braucht Status, Dokumentation, Tests und Beispielcontent.

## Praktische Kommandos fuer den aktuellen Stand

```bash
gitbook-worker validate --lang de
gitbook-worker validate --lang en
gitbook-worker run --lang de --profile local
gitbook-worker run --lang en --profile local
gitbook-worker-fonts sync --manifest de/publish.yml --search-path .github/fonts
python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf de/publish/das-sample-buch.pdf --format text
```

Unter Windows im aktuellen Workspace existieren passende VS-Code-Tasks fuer
lokale PDF-Builds und PDF-TOC-Pruefungen.

## Gesamtbewertung

GitBook Worker ist im aktuellen Stand ein ernstzunehmendes internes Publishing-
Werkzeug mit produktivem Schwerpunkt auf PDF-Buechern. Die Staerke liegt in der
Kombination aus GitBook-kompatibler Inhaltsstruktur, profilgesteuertem Orchestrator,
strenger Font- und Lizenzkontrolle, mehrsprachigem Content-Modell, Docker-/CI-
Faehigkeit und einer fuer PDF-Fragilitaet ungewoehnlich breiten Testlandschaft.

Der naechste Reifegrad entsteht weniger durch neue Features als durch
Konsolidierung: CI-Pfade pruefen, Lizenzsignale klaeren, historische Doku noch
sauberer von aktueller Doku trennen und den Installations-/Font-Sync-Pfad fuer
externe Nutzer weiter glaetten. Danach waere das Projekt gut positioniert, um
als wiederverwendbarer Publishing-Baustein ueber einzelne Buchrepos hinaus zu
funktionieren.
