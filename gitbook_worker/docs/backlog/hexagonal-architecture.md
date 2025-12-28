Für ein mittelgroßes bis großes **CLI-Tools-Paket (100k–500k LoC)** mit klar getrennten Fachdomänen (Fonts, Lizenzen, Projekt-/Dokument-Konfigurationen, Konvertierung nach PDF/HTML usw., `CITATION.cff` pro Projekt) ist in der Praxis am robustesten:

## Empfehlung: **Modularer Monolith + Hexagonal/Clean Architecture + Plugin/Microkernel für Converter**

Das ist kein “ein Pattern”, sondern eine sehr bewährte **Kombination**, die bei CLI-Toolchains besonders gut skaliert:

* **Hexagonal (Ports & Adapters) / Clean Architecture**: hält dein „Kernwissen“ stabil und testbar.
* **Modularer Monolith**: ein Repo/Artefakt, aber klar abgegrenzte Module (ohne Microservices-Overhead).
* **Microkernel/Plugin-Architektur** *für die Konvertierer*: weil Formate/Engines typischerweise wachsen und wechseln.

Damit kannst du neue Output-Formate, Render-Engines oder License-Backends hinzufügen, ohne den Kern umzubauen.

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

---

Wenn du mir sagst, in welcher Sprache/Toolchain du das baust (Go/Rust/Python/Node/Java) und ob Converter eher “externe Tools” (Pandoc etc.) oder “Libraries” sind, kann ich dir die **konkrete Paketstruktur + Interface-Sets** sehr passend vorschlagen (inkl. Fehler-/Exitcode-Strategie für CLIs).
