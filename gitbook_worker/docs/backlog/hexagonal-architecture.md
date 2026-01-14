---
version: 0.6.0
date: 2026-01-14
history:
   - version: 0.6.0
      date: 2026-01-14
      description: Detailed the next 2 slices (Root resolution + Artifact layout) with concrete file targets, acceptance criteria, and test strategy
   - version: 0.5.0
      date: 2026-01-13
      description: Tightened architecture guardrails (dependency direction, packaging-first imports) and added a repeatable “next slice” template with testing guidance
   - version: 0.4.0
      date: 2026-01-13
      description: Implemented the next hexagonal slice (PDF TOC extraction) with Port + Use-Case + Adapter; migrated the CLI and added tests
   - version: 0.3.0
      date: 2026-01-13
      description: Added explicit next-step and next-10-steps incremental plan to keep the hexagonal migration track actionable
   - version: 0.2.0
      date: 2026-01-12
      description: Implemented first Ports & Adapters slice (SVG→PDF conversion) and documented incremental migration strategy
   - version: 0.1.0
      date: 2025-12-01
      description: Initial notes on Hexagonal/Clean architecture for the project
---

Für ein mittelgroßes bis großes **CLI-Tools-Paket (100k–500k LoC)** mit klar getrennten Fachdomänen (Fonts, Lizenzen, Projekt-/Dokument-Konfigurationen, Konvertierung nach PDF/HTML usw., `CITATION.cff` pro Projekt) ist in der Praxis am robustesten:

## Empfehlung: **Modularer Monolith + Hexagonal/Clean Architecture + Plugin/Microkernel für Converter**

Das ist kein “ein Pattern”, sondern eine sehr bewährte **Kombination**, die bei CLI-Toolchains besonders gut skaliert:

* **Hexagonal (Ports & Adapters) / Clean Architecture**: hält dein „Kernwissen“ stabil und testbar.
* **Modularer Monolith**: ein Repo/Artefakt, aber klar abgegrenzte Module (ohne Microservices-Overhead).
* **Microkernel/Plugin-Architektur** *für die Konvertierer*: weil Formate/Engines typischerweise wachsen und wechseln.

Damit kannst du neue Output-Formate, Render-Engines oder License-Backends hinzufügen, ohne den Kern umzubauen.

---

## Status im Repository (inkrementelle Migration)

Diese Architektur wird in diesem Repo **inkrementell** eingeführt (kein Big-Bang-Refactor).

### Implementiert (erster Slice): SVG → PDF als Port & Adapter

Ziel: doppelte/abweichende SVG→PDF-Logik in Tools konsolidieren, so dass der “Kern” eine stabile, testbare API hat und die konkreten Libraries (CairoSVG, svglib/reportlab) nur noch Adapter sind.

- **Port (Interface):** `gitbook_worker/core/ports/svg_to_pdf.py`
- **Use-Case (Application):** `gitbook_worker/core/application/svg_to_pdf.py` (`ensure_svg_pdf`)
- **Adapter:**
   - `gitbook_worker/adapters/svg/cairosvg_svg_to_pdf.py`
   - `gitbook_worker/adapters/svg/svglib_svg_to_pdf.py`
- **Eingebunden in bestehende Tools (Adapter-Caller):**
   - `gitbook_worker/tools/utils/asset_copy.py`
   - `gitbook_worker/tools/publishing/publisher.py`

Diese Änderung ist bewusst klein gehalten, aber sie zeigt die Abhängigkeitsrichtung: Tools/Infra hängen nun von einem Core-Use-Case ab (nicht umgekehrt).

### Nächster inkrementeller Schritt (konkret geplant): PDF-TOC Extraktion als Port & Adapter

Warum als nächstes?

- Es ist ein **klar abgegrenzter IO-Use-Case** (PDF rein → strukturierte TOC raus).
- Es gibt bereits **eine dedizierte CLI/Tooling-Nutzung** (TOC-Checks) und es ist damit gut testbar.
- Optional/wechselnde Abhängigkeiten (z.B. PDF-Libraries) bleiben **in Adaptern**.

Status: ✅ umgesetzt (Port + Use-Case + Adapter + CLI-Migration + Tests)

Zielzustand (minimaler Slice, ohne Nebenkriegsschauplätze):

- **Port:** `gitbook_worker/core/ports/pdf_toc.py` (`PdfTocExtractorPort`)
- **Use-Case:** `gitbook_worker/core/application/pdf_toc.py` (`extract_pdf_toc(...)`)
- **Adapter:** `gitbook_worker/adapters/pdf/pypdf_toc_extractor.py`
- **Einbindung:** `gitbook_worker/tools/utils/pdf_toc_extractor.py` ruft nur noch den Use-Case.
- **Tests:** `gitbook_worker/tests/core/test_pdf_toc.py` (Fake-Port Unit-Tests + pypdf Smoke-Test)

Akzeptanzkriterien:

- TOC-Tool läuft unverändert weiter (gleiche CLI-Args, gleiche Ausgabeformate).
- Core/Application kann ohne PDF-Library getestet werden.
- Import von optionalen PDF-Dependencies passiert nur im Adapter (keine Import-Time Side-Effects im Package-Init).

### Offener Plan: nächste 10 inkrementelle Schritte (ohne Big-Bang)

Die Reihenfolge ist absichtlich so gewählt, dass jeder Schritt **klein** ist, **schnell testbar**, und jeweils nur 1–2 Call-Sites migriert.

1) ✅ **PDF-TOC Extraktion hexagonal schneiden** (Port + Use-Case + Adapter; Tool ruft Use-Case)
2) **Pfad-/Root-Resolution als Port** (z.B. Repo-Root/Project-Root Discovery; entkoppelt von `os.getcwd()`/git)
3) **Content/Publish-Konfig-Parsing als Use-Case** (Validierung + Merge-Policy zentral, keine Duplikate in CLI/Tools)
4) **Artifact-Layout/Publish-Paths als Domain-Service** (ein Ort für “wo liegen Outputs”, statt verteilte Pfad-Logik)
5) **License-Attribution Generation als Use-Case** (Inputs: verwendete Assets/Fonts; Output: Attribution-Model; Writer als Port)
6) **Font-Inventory als Port** (Discovery/Install als Adapter; Policies/Filtering im Core, inkl. `fonts.yml` als SoT)
7) **External-Command Runner Port** (Pandoc/LaTeX als Adapter; im Core nur “run tool X with args”, inkl. strukturierter Fehler)
8) **Renderer/Converter Registry minimal einführen** (einfaches Registry-Interface, ohne Plugin-Overengineering)
9) **Workflow-Orchestrator: Plan vs Execute trennen** (Domain/Application erzeugt “Plan”; Adapter führt aus)
10) **CLI Commands verschlanken** (CLI wird dünner Adapter; Use-Cases werden erste Anlaufstelle; Exit-Codes aus Core-Modell)

---

## a) Konkretisierte nächste 2 Slices (sofort umsetzbar)

Diese beiden Schritte sind bewusst so geschnitten, dass sie **Duplikate entfernen** und **die restliche Toolchain stabiler** machen, ohne einen großen Umbau.

### Slice 2: Pfad-/Root-Resolution als Port

**Problem heute**

- Root-Erkennung existiert mehrfach (Docker-Tools, Publisher, Orchestrator, Tests) und nutzt unterschiedliche Heuristiken.
- Das führt zu “läuft lokal, bricht in CI/Container” oder “cwd vs repo root” Inkonsistenzen.

**Ist-Zustand (konkrete Stellen)**

- Root-Argumente/Defaults in mehreren CLIs:
   - `gitbook_worker/tools/workflow_orchestrator/orchestrator.py` (`--root`)
   - `gitbook_worker/tools/publishing/pipeline.py` (`--root`)
   - `gitbook_worker/tools/publishing/dump_publish.py` (`--root`)
   - `gitbook_worker/tools/converter/convert_assets.py` (`--root`)
- Root-Discovery Logik an mehreren Orten:
   - `gitbook_worker/tools/utils/smart_manifest.py` (Repo-Root detection)
   - `gitbook_worker/tools/docker/cli.py` (find repo root by `.git`)
   - `gitbook_worker/tools/docker/run_docker.py` (best-effort root detection)
   - `gitbook_worker/tools/utils/smart_git.py` (`git rev-parse --show-toplevel`)
- Tests nutzen eigene Root-Helpers:
   - `gitbook_worker/tests/conftest.py` (repo_root fixtures)

**Zielzustand (minimaler Slice)**

- **Port:** `gitbook_worker/core/ports/repo_root.py`
   - `RepoRootResolverPort.resolve(start: Path) -> Path`
   - klare Errors (z.B. `RepoRootNotFoundError`) statt `None`-Propagation
- **Use-Case:** `gitbook_worker/core/application/repo_root.py`
   - `resolve_repo_root(start: Path, resolver: RepoRootResolverPort) -> Path`
   - optional: `resolve_repo_root_or_cwd(...)` falls Tools bewusst tolerant bleiben sollen
- **Adapter:** `gitbook_worker/adapters/fs/repo_root_resolver.py`
   - Heuristik-Order (explizit dokumentiert):
      1) `GITBOOK_REPO_ROOT` (wenn gesetzt)
      2) `git rev-parse --show-toplevel` (wenn git verfügbar)
      3) Upwards scan: Marker-Dateien (`pyproject.toml`, `content.yaml`, `publish.yml`, `.git`)

**Migratierte Call-Sites (max 2 im Slice)**

- `gitbook_worker/tools/docker/run_docker.py`: ersetzt lokale Root-Detection durch Use-Case
- `gitbook_worker/tools/docker/cli.py`: nutzt ebenfalls Use-Case (damit Docker-Tools konsistent sind)

**Akzeptanzkriterien**

- Docker-Tools finden in allen drei Modi konsistent den Root: `cwd` im Repo, Subfolder, und außerhalb (liefert klaren Fehler).
- Core/Application importiert keine Git/OS-spezifischen Dependencies.
- Mindestens 1 Unit-Test: Use-Case + Fake-Port.
- Mindestens 1 Integration/Smoke-Test: Adapter findet Root in Test-Repo-Struktur.

### Slice 4: Artifact-Layout/Publish-Paths als Domain-Service

**Problem heute**

- “Wo liegen Outputs?” ist verteilt (Publisher, Orchestrator, Smart-Publisher), mit Sonderfällen (`publish/`, `publish/temp/`, lang-spezifische publish dirs).

**Ist-Zustand (konkrete Stellen)**

- `gitbook_worker/tools/publishing/publisher.py`:
   - `_resolve_publish_directory(...)`
   - `publish_dir`/`tempfile.tempdir = <publish>/temp`
   - schreibt/liest diverse Artefakte relativ zum publish dir
- `gitbook_worker/tools/workflow_orchestrator/orchestrator.py`:
   - schreibt `CITATION.cff` in das Publish-Verzeichnis
- `gitbook_worker/tools/utils/smart_publisher.py`:
   - arbeitet mit `target.out_dir`/`publish_dir`

**Zielzustand (minimaler Slice)**

- **Domain-Service/DTO:** `gitbook_worker/core/domain/artifacts.py`
   - `ArtifactLayout(repo_root: Path, publish_dir: Path, temp_dir: Path, citation_path: Path, logs_dir: Path, ...)`
   - keine IO: nur Pfade berechnen + invariants
- **Use-Case:** `gitbook_worker/core/application/artifacts.py`
   - `build_artifact_layout(repo_root: Path, publish_dir: Path | None, ...) -> ArtifactLayout`
   - Policy: default publish dir vs overrides (z.B. manifest-dir vs repo-root)
- **Adapter-Integration:** zunächst nur 1–2 Call-Sites umbauen

**Migratierte Call-Sites (max 2 im Slice)**

- `gitbook_worker/tools/workflow_orchestrator/orchestrator.py`: nutzt `ArtifactLayout.citation_path` statt harte `publish/`-Annahmen
- `gitbook_worker/tools/publishing/publisher.py`: nutzt `ArtifactLayout.publish_dir/temp_dir` statt eigener temp-dir Setups

**Akzeptanzkriterien**

- Für gleiche Inputs werden in Orchestrator und Publisher identische Publish/Temp-Pfade berechnet.
- Alle erzeugten Artefakte (inkl. `CITATION.cff`) landen ausschließlich im `<publish_dir>` (kein Copy ins Repo-Root).
- `publish/temp` wird weiterhin genutzt, aber die Definition liegt an einem Ort.
- Unit-Tests: Layout-Berechnung (pure), plus 1 Smoke-Test in einem temp workspace.

---

## Wie das auf dein Problem “passt”

### 1) Stabiler Kern (Domain)

Hier lebt das, was dein Tool *ist*, unabhängig davon *wie* es CLI-Args parst oder PDFs rendert:

* **Domain-Modelle**: `Project`, `DocumentConfig`, `FontAsset`, `License`, `ConversionTarget`, `CitationMetadata`, `ConversionPlan`
* **Regeln/Validierung**: Lizenz-Kompatibilität, Font-Auswahlregeln, Projektauflösung, Prioritäten von Konfigs (global → project → doc)
* **Policies**: “Welche Lizenz gilt für welches Asset?”, “Wie wird citation.cff generiert?”

→ Vorteil: fast alles davon ist **pure logic** und extrem gut unit-testbar.

### 2) Application Layer (Use-Cases)

Orchestriert Abläufe, aber enthält möglichst wenig Fachlogik:

* `InitProject`
* `ValidateProject`
* `ConvertDocument`
* `ExportCitationCFF`
* `ListFonts`, `InstallFonts`, `AuditLicenses`

Use-Cases sprechen nur über **Ports (Interfaces)**, nicht über konkrete Implementierungen.

### 3) Adapters/Infrastructure

Alles, was “dreckig” ist: IO, Dateisystem, Git, Netz, externe Tools, PDF-Renderer, Font-Discovery usw.

* Filesystem-Adapter (lesen/schreiben)
* Git-Adapter (Version-Info, Repo-Root, Tags)
* Renderer-Adapter (z.B. Pandoc/LaTeX/Prince/wkhtmltopdf/…)
* Font-Adapter (OS-Font-Dirs, Bundles, Caches)
* License-Scanner (SPDX, Lizenztexte, Header-Scanner)

---

## Plugin/Microkernel für Konverter (der Schlüssel bei PDF/HTML etc.)

Konverter/Renderer sind die Komponente, die typischerweise am häufigsten wächst.

**Core definiert nur ein Port**, z.B. `Converter`:

* `canHandle(inputType, outputType, features)`
* `plan()` (optional)
* `convert(plan, context)`

**Plugins liefern Implementierungen**:

* `Markdown → HTML`
* `Markdown → PDF`
* `Docx → PDF`
* `HTML → PDF`
* `…`

Core hat nur eine **Registry**, die Plugins registriert (compile-time oder runtime).
CLI sagt nur: “convert this project/doc to PDF”, Application Layer wählt passend den Converter.

---

## Praktische Modul-Schnitte (für dein Thema sinnvoll)

Ich würde *mindestens* diese Module trennen:

1. **project-config**
   Parsing/Merging/Schema-Versionierung, inkl. Multi-Config-Handling
2. **fonts**
   Discovery, Bundling, Subsetting, Embedding-Policies
3. **licenses**
   Lizenzinventar, Kompatibilitätsregeln, Audits, Ausgabe von Lizenzreports
4. **citation**
   Generierung/Validierung von `CITATION.cff` (plus optional BibTeX/CSL export)
5. **conversion**
   Pipeline-Planung, Target-Resolver, Converter-Ports, Artifact-Layout

Wichtig: **conversion** darf nicht “heimlich” Font/Lizenz-Regeln duplizieren, sondern nutzt deren Use-Cases/Services.

---

## Ordner-/Paketstruktur (sprachagnostisch)

Eine bewährte Struktur (sinngemäß):

* `core/domain/...`
* `core/application/...`
* `core/ports/...`
* `adapters/cli/...`
* `adapters/fs/...`
* `adapters/renderers/...`
* `plugins/converters/...` (oder `adapters/converters/...`)

Entscheidend sind nicht die Ordnernamen, sondern die Regel:
**Abhängigkeiten zeigen nach innen.**
Domain kennt nichts von CLI, Filesystem oder PDF-Tools.

---

## Guardrails (damit es nicht „Clean Architecture in Theorie“ bleibt)

Diese Regeln sind absichtlich “hart”, weil sie den Core testbar und stabil halten.

### 1) Abhängigkeitsrichtung (praktisch)

- `gitbook_worker/core/domain/**` darf nur von der Standardbibliothek abhängen.
- `gitbook_worker/core/application/**` darf Domain importieren und Ports nutzen, aber keine Adapter.
- `gitbook_worker/core/ports/**` definiert Interfaces/DTOs/Exceptions, aber enthält keine IO.
- `gitbook_worker/adapters/**` implementiert Ports und darf schwere/optionale Libraries importieren.
- `gitbook_worker/tools/**` ist ein CLI/Script-Adapter: ruft Use-Cases, macht Argument-Parsing, Exit-Codes, Logging.

Wenn irgendwo ein Adapter in den Core importiert wird, ist die Schichtung faktisch gebrochen.

### 2) Package-first Layout (Repo-spezifisch)

Im Repo gilt: **Python-Code lives in `gitbook_worker/`**.

- Neue Imports immer über `gitbook_worker.*`.
- Der Fallback unter `tools/` ist nur Abwärtskompatibilität; neue Ports/Use-Cases/Adapter gehören nicht dorthin.

### 3) Optional Dependencies nur im Adapter

Regel: Wenn eine Dependency optional ist oder IO macht (pypdf, reportlab, LaTeX-Tools, …), dann:

- Import erst im Adapter-Modul.
- Core/Application bleibt import-time clean.
- Tests können den Use-Case gegen Fake-Port laufen lassen (keine Third-Party nötig).

### 4) Exit-Codes sind Teil des Contracts

CLI-Tools sollen eindeutige Exit-Codes nutzen und diese dokumentieren.

- Canonical Doc: `gitbook_worker/docs/attentions/exit-codes.md`
- UX: CLI zeigt die Tabelle über `--help exit-codes` (oder äquivalent).

---

## “Next Slice” Template (wiederholbarer Bauplan)

Wenn wir etwas als nächsten Hex-Slice ziehen, dann immer in dieser Reihenfolge.

### Schritt A: Port definieren

- Datei: `gitbook_worker/core/ports/<topic>.py`
- Inhalt: Protocol/ABC, Requests/Responses (Dataclasses), domain-nahe Exceptions

### Schritt B: Use-Case bauen

- Datei: `gitbook_worker/core/application/<topic>.py`
- Signatur: nimmt Port als Dependency entgegen (Constructor-Injection oder Parameter)
- Logik: pure orchestration + policies, keine IO

### Schritt C: Adapter implementieren

- Datei: `gitbook_worker/adapters/<area>/<impl>.py`
- Hält Third-Party Imports, IO, “dirty details”

### Schritt D: Tool/CLI migrieren

- Datei: `gitbook_worker/tools/**` bleibt dünn
- Tut nur: args parsen, Use-Case aufrufen, exit-codes/logging, output-formatting

### Schritt E: Tests (Definition of Done)

- Unit-Test: Use-Case + Fake-Port (schnell, deterministisch)
- Smoke-Test: Adapter gegen echte Lib (wenn verfügbar; minimal)
- Optional: Golden output (Text/JSON) für CLI, falls Ausgabe contract-stabil ist

---

## Mapping: Wo liegt was im aktuellen Repo?

Kurzform, damit neue Beiträge nicht “irgendwo” landen:

- **Ports:** `gitbook_worker/core/ports/`
- **Use-Cases:** `gitbook_worker/core/application/`
- **Adapter:** `gitbook_worker/adapters/`
- **CLI/Tools (Adapter-Caller):** `gitbook_worker/tools/`
- **Engineering Docs:** `gitbook_worker/docs/` (diese Datei ist korrekt platziert)

---

## Warum ich das gegenüber Alternativen vorziehe

* **Reines “Command Pattern”** ist zu flach: wird bei 300k LoC schnell spaghetti, wenn Domain-Regeln wachsen.
* **DDD-only** ohne Ports/Adapters führt oft zu „Infra sickert rein“ (Renderer-Details landen im Kern).
* **Microservices** sind für CLI-Tooling fast immer unnötig schwer.
* **Nur Plugin-Architektur** ohne Clean/Hex endet oft in einem untestbaren Core, der doch alles weiß.

Die Kombination macht’s: **Clean/Hex für Stabilität + Plugins für Wachstum.**

---

## Mini-Checkliste, ob du “richtig” liegst

Du bist auf dem richtigen Weg, wenn:

* Domain-Tests laufen ohne Dateisystem, ohne externe Tools, ohne CLI.
* Ein neuer Converter braucht **keine** Änderungen im Domain-Kern (nur Registrierung).
* Konfig-Merging ist zentral gelöst und nicht in jedem Command neu.
* Lizenz-/Font-Policies sind **einmal** definiert und überall gleich.

