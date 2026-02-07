---
version: 0.1.0
date: 2026-01-17
history:
  - version: 0.1.0
    date: 2026-01-17
    description: Initial fachliches Konzept für ArtifactLayout (Publish-Dir als Single Source of Truth) als Grundlage für den nächsten Hex-Slice
---

# Fachliches Konzept: ArtifactLayout / Publish-Layout

## Ziel

Ein zentrales, fachlich definiertes **ArtifactLayout** beschreibt *ausschließlich per Pfadberechnung* (keine IO), wo Build-/Publish-Artefakte liegen sollen. Dadurch:

- berechnen Orchestrator, Publisher und Hilfstools identische Pfade,
- es gibt eine einzige Stelle für Layout-Policies,
- Tests können Pfadlogik ohne Dateisystem/Tools validieren.

## Kernaussage (Policy)

**Alle erzeugten Artefakte müssen im `<publish_dir>` liegen.**

- Keine Kopien in den Repository-Root.
- Insbesondere gilt: `CITATION.cff` wird *nur* im Publish-Verzeichnis gepflegt.

Damit bleibt der Output vollständig “container-/CI-freundlich” und ist pro Lauf/Language-Root sauber isoliert.

## Begriffsklärung

- **`repo_root`**: Wurzel des Repos/Workspaces (Checkout), z.B. `C:\gitbook-worker`.
- **`language_root`**: Root der Sprache bzw. Content-Entry (kann = `repo_root` sein oder z.B. `de/`).
- **`publish_dir`**: Zielverzeichnis für Artefakte (absoluter Pfad), konfigurierbar/ableitbar.

## Was ist ein Artefakt?

Artefakte sind *Outputs oder Nebenoutputs* einer Pipeline, z.B.:

- PDFs, HTML, EPUB (je nach Pipeline)
- `CITATION.cff`
- Reports (z.B. AI-reference report, Emoji-Report)
- temporäre Build-Dateien, soweit sie für Debugging/Weiterverarbeitung relevant sind

Nicht gemeint sind Quell-Dateien oder Konfiguration in der Repo-Struktur.

## ArtifactLayout (Domain-DTO)

ArtifactLayout ist ein reines Datenobjekt (DTO) mit folgenden Mindestfeldern:

- `repo_root: Path`
- `language_root: Path`
- `publish_dir: Path`  *(absolute Path)*
- `temp_dir: Path`  *(typisch: `<publish_dir>/temp`)*
- `citation_path: Path` *(typisch: `<publish_dir>/CITATION.cff`)*

Optional (später, wenn tatsächlich gebraucht):

- `logs_dir: Path` *(falls Logs ebenfalls ins publish dir wandern sollen)*
- `reports_dir: Path` *(z.B. `<publish_dir>/reports`)*

## Ableitungsregeln (Business Rules)

### 1) Publish Dir bestimmen

Die Layout-Berechnung muss deterministisch sein. Priorität der Inputs:

1. **Explizites Publish-Dir** (CLI-Argument / Konfig) → wird absolut gemacht.
2. **Manifest-basierte Out-Dir** (z.B. `publish.yml` entry `out_dir`) → relativ zum Manifest-Parent.
3. **Default** → `language_root / "publish"`.

Wichtig: Es gibt keinen Sonderfall “repo root publish” oder Copy-Back in die Root.

### 2) Temp Dir

- `temp_dir = publish_dir / "temp"`

### 3) Citation

- `citation_path = publish_dir / "CITATION.cff"`
- Wenn eine Sprache (`language_root`) ein eigenes publish dir hat, bleibt citation dort.

## Verantwortlichkeiten (Hexagonal)

- **Domain (`core/domain`)**: `ArtifactLayout` + Invariants (z.B. alle Paths müssen absolut sein; `temp_dir` muss unter `publish_dir` liegen).
- **Application (`core/application`)**: Use-Case `build_artifact_layout(...)` implementiert die Policy (Prioritäten, Normalisierung).
- **Adapter (`adapters/fs` / `tools/**`)**:
  - IO: Directory-Erstellung, Writes, Logging
  - Mapping von CLI-Args/Manifest-Strukturen auf die Use-Case Inputs

## Nicht-Ziele (bewusst)

- Keine Umstellung aller Artefakte in einem Schritt.
- Kein großer Umbau der bestehenden Pipeline.
- Kein Plugin-System.

Der Slice ist bewusst so klein, dass er in 1–2 Call-Sites Nutzen bringt.

## Akzeptanzkriterien für den Slice

- Orchestrator und Publisher berechnen bei gleichen Inputs identische `publish_dir`/`temp_dir`.
- `CITATION.cff` wird nicht mehr ins Repo-Root kopiert.
- Unit-Tests prüfen die Pfadberechnung (ohne IO).
- Ein Smoke-Test bestätigt: `temp_dir` liegt unter `publish_dir` und wird genutzt.
