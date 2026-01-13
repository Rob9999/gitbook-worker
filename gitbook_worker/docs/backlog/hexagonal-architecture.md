---
version: 0.4.0
date: 2026-01-13
history:
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

1) **PDF-TOC Extraktion hexagonal schneiden** (Port + Use-Case + Adapter; Tool ruft Use-Case)
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

