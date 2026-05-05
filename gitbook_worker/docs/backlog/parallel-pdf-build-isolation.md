---
version: 1.0.0
date: 2026-05-05
status: backlog
priority: high
labels: [publisher, pdf, concurrency, multilingual, release-hardening]
history:
  - "1.0.0: 2026-05-05 - Backlog-Eintrag fuer parallele PDF-Build-Isolation mehrerer Sprachbaeume angelegt"
---

# Backlog: Parallele PDF-Builds fuer mehrere Sprachen haerten

## Ausgangslage

GitBook Worker baut aktuell mehrere Sprachbaeume wie `de/` und `en/` sicher
nacheinander. In parallelen Laeufen gab es jedoch zeitweise Blockierungen oder
gegenseitige Beeinflussung. Das Risiko steigt in CI/CD, wenn mehrere Sprachen
gleichzeitig gebaut werden sollen, oder lokal, wenn Anwender mehrere
Orchestrator-Laeufe parallel starten.

## Ziel

PDF-Builds unterschiedlicher Sprachbaeume sollen parallel laufen koennen, ohne
sich gegenseitig zu blockieren oder Artefakte, temporaere Dateien, Logs,
Font-Caches oder Build-Flags zu ueberschreiben.

## Vermutete Konfliktfelder

- Gemeinsame temporaere Arbeitsverzeichnisse fuer Combined Markdown,
  Pandoc-Zwischendateien oder LuaLaTeX-Ausgaben.
- Gemeinsame Log-Dateien oder Debug-Verzeichnisse ohne laufbezogene
  Unterordner.
- Gleichzeitige Aktualisierung von `ATTRIBUTION.md`, `LICENSE-*` oder
  Publish-Artefakten im selben Zielordner.
- LuaTeX- und `luaotfload`-Cache-Locks bei gleichzeitigen Font-Initialisierungen.
- Font-Storage-Bootstrap oder Font-Download ohne Prozess-/Dateilock.
- Orchestrator-Optionen wie `reset_build_flag`, die bei parallelen Laeufen auf
  dieselbe `publish.yml` wirken koennen.
- Globale Umgebungsvariablen oder Logging-Konfiguration in Subprozessen.
- Docker-Container mit identischen Namen, Tags, Workdirs oder gemounteten
  Scratch-Pfaden.

## Anforderungen

- Jeder Build-Lauf bekommt eine eindeutige `run_id`.
- Temp-, Log- und LaTeX-Debug-Verzeichnisse werden pro `run_id`, Sprache und
  Publish-Target isoliert.
- Font-Storage-Sync und LuaTeX-Cache-Aktualisierung verwenden Locks oder eine
  dokumentierte Vorbereitungsphase vor parallelen Builds.
- Publish-Zielartefakte werden atomar geschrieben: erst in einen temporären
  Zielpfad, danach Rename/Move in den finalen Pfad.
- Unterschiedliche Sprachen duerfen parallel bauen, wenn sie nicht denselben
  finalen Output-Pfad verwenden.
- Gleiche Sprache / gleicher Output-Pfad wird entweder sauber serialisiert oder
  mit klarer Fehlermeldung abgewiesen.
- Docker-Laeufe verwenden eindeutige Container-Namen oder erlauben parallele
  Instanzen ueber eine `run_id`.
- Logs muessen die `run_id`, Sprache, Manifest, Profil und Output-Pfade
  enthalten.

## Technischer Ansatz

### Phase 1: Ist-Analyse und Reproduktion

- [ ] Publisher-, Orchestrator-, Font-Storage- und Docker-Pfade auf gemeinsame
      Schreibziele pruefen.
- [ ] Minimalen Parallel-Smoke definieren, z. B. `de` und `en` gleichzeitig.
- [ ] Reproduktionsskript fuer lokale parallele Builds erstellen.
- [ ] Bekannte Lock-/Blockierungsstellen dokumentieren.

### Phase 2: Lauf-Isolation

- [ ] `run_id` im Orchestrator erzeugen und an Publisher/Subprozesse
      weiterreichen.
- [ ] Temp- und Debug-Pfade auf `<logs>/<run_id>/<lang>/<target>/` oder
      vergleichbare Struktur umstellen.
- [ ] Combined-Markdown und LaTeX-Arbeitsdateien pro Build in isolierten
      Arbeitsverzeichnissen erzeugen.
- [ ] Endartefakte atomar aus dem isolierten Arbeitsverzeichnis in `publish/`
      verschieben.

### Phase 3: Locks und Schutzregeln

- [ ] Font-Storage-Sync mit Datei-Lock absichern.
- [ ] LuaTeX-Cache-Update vor parallelen Builds als Preflight empfehlen oder
      mit Lock serialisieren.
- [ ] Konflikte gleicher finaler Output-Pfade erkennen und mit eigener Diagnose
      abbrechen.
- [ ] Docker-Container- und Image-Namen fuer Parallelbetrieb pruefen und, falls
      noetig, um `run_id` erweitern.

### Phase 4: Tests und Dokumentation

- [ ] Unit-Tests fuer Pfadableitung und Output-Konflikterkennung.
- [ ] Integrationstest fuer parallele `de`/`en` PDF-Builds.
- [ ] Docker-Integrationstest fuer parallele Container-Laeufe oder bewusstes
      Serialisierungsverhalten.
- [ ] Anwenderanleitung und Release-Prozedur um Parallel-Build-Hinweise
      ergaenzen.

## Akzeptanzkriterien

- Zwei unterschiedliche Sprachbaeume koennen lokal parallel gebaut werden.
- Beide PDFs bestehen anschliessend das PDF-Font-Gate fuer Emoji und ERDA-CJK.
- Logs und Debug-Dateien sind eindeutig einem Lauf zuordenbar.
- Kein Build ueberschreibt temporaere Dateien eines anderen Builds.
- Konflikte gleicher finaler Zielpfade werden vor dem Schreiben erkannt.
- Docker-Laeufe sind entweder parallel stabil oder geben eine klare
  Serialisierungsdiagnose aus.

## Risiken und offene Fragen

- LuaTeX- und Fontconfig-Caches koennen plattformspezifische Locking-Eigenheiten
  haben.
- Atomare Moves sind auf lokalen Dateisystemen robuster als auf Netzlaufwerken.
- Bestehende CI-Skripte koennten feste Log- oder Container-Namen erwarten.
- `reset_build_flag` ist potentiell nicht parallel-sicher, wenn mehrere Laeufe
  dieselbe `publish.yml` veraendern sollen.

## Manuelle Pruefungsidee

Nach Umsetzung koennte ein lokaler Smoke so aussehen:

```powershell
$de = Start-Process -PassThru -NoNewWindow c:\gitbook-worker\.venv\Scripts\python.exe -ArgumentList "-m gitbook_worker.tools.workflow_orchestrator run --root C:\gitbook-worker --content-config content.yaml --lang de --profile local"
$en = Start-Process -PassThru -NoNewWindow c:\gitbook-worker\.venv\Scripts\python.exe -ArgumentList "-m gitbook_worker.tools.workflow_orchestrator run --root C:\gitbook-worker --content-config content.yaml --lang en --profile local"
$de.WaitForExit(); $en.WaitForExit()
if ($de.ExitCode -ne 0 -or $en.ExitCode -ne 0) { throw "Parallel build failed" }
```

Danach:

```powershell
python -m gitbook_worker.tools.testing.pdf_validator --pdf de\publish\das-sample-buch.pdf
python -m gitbook_worker.tools.testing.pdf_validator --pdf en\publish\the-sample-book.pdf
```