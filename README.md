# GitBook Worker

**v2.1.0** · [Release Notes](docs/releases/v2.1.0.md) · [Kundenguide / Customer Guide](docs/customer-installation.md) · [Lizenz / License](LICENSE)

🇩🇪 [Deutsch](#-deutsch) · 🇬🇧 [English](#-english)

---

## 🇩🇪 Deutsch

### Was ist GitBook Worker?

GitBook Worker ist ein Python-basiertes CLI-Toolkit, das **Markdown-Inhalte in
druckfertige PDF-Bücher** umwandelt. Es übernimmt den gesamten Weg von der
GitBook-kompatiblen Ordnerstruktur bis zum fertigen PDF – inklusive
Inhaltsverzeichnis, Titelseite, Emoji-Rendering, Font-Management und
Lizenz-Attribution.

Die Pipeline besteht aus aufeinander abgestimmten Schritten:

| Schritt | Aufgabe |
|---|---|
| **Converter** | Konvertiert und normalisiert Markdown-Quellen |
| **Engineering Formatter** | Formatiert technische Dokumente einheitlich |
| **Attribution Generator** | Erzeugt `ATTRIBUTION.md` und `LICENSE-*` aus der Font-Konfiguration |
| **Publisher** | Baut das PDF via Pandoc + LuaLaTeX mit konfigurierten Fonts und Fallbacks |

Ein einziger CLI-Befehl orchestriert alle Schritte – lokal, in Docker oder in
GitHub Actions.

### Warum und wann GitBook Worker einsetzen?

GitBook Worker ist das richtige Werkzeug, wenn du:

- **Markdown-Bücher als PDF publizieren** willst, ohne manuell LaTeX schreiben
  zu müssen.
- **Mehrsprachige Buchprojekte** aus einer einzigen Repository-Struktur
  verwalten und bauen möchtest (z. B. `de/`, `en/`, `ua/`).
- **Reproduzierbare Builds** brauchst – ob lokal, in CI/CD oder im
  Docker-Container, das Ergebnis ist identisch.
- **Farb-Emojis im PDF** benötigst (Twemoji Mozilla COLR/CPAL).
- **Lückenlose Font-Lizenz-Compliance** sicherstellen musst: Jede Schriftart
  wird in `fonts.yml` deklariert, Attribution wird automatisch generiert.
- **Bestehende GitBook-Projekte** (mit `SUMMARY.md` und `book.json`) offline
  in hochwertige PDFs überführen willst.

> **Nicht geeignet für**: reine HTML/Web-Ausgabe (dafür GitBook selbst nutzen),
> Projekte ohne Markdown-Quellen oder Einzeldatei-Konvertierungen (einzelne Markdown ginge, wenn der Aufwand das rechtfertigt, ansonsten dafür
> Pandoc direkt nutzen).

### Wie GitBook Worker einsetzen?

#### Voraussetzungen

- Python ≥ 3.10
- Pandoc und TeX Live (LuaLaTeX) – für PDF-Erzeugung
- Optional: Docker Desktop – für isolierte Builds

#### Installation

```bash
python -m pip install --upgrade pip
pip install -e .          # Entwicklermodus (empfohlen)
# oder
pip install dist/gitbook_worker-2.1.0-py3-none-any.whl   # fertige Distribution
```

#### Schnellstart

```bash
# Gesamte Pipeline für das deutsche Buch ausführen
gitbook-worker run --lang de --profile local

# Nur den Publisher-Schritt ausführen
gitbook-worker run --lang de --step publisher

# Manifest validieren, ohne die Pipeline zu starten
gitbook-worker validate --lang de
```

#### Wichtige CLI-Optionen

| Option | Beschreibung |
|---|---|
| `--lang <id>` | Sprache wählen (muss in `content.yaml` definiert sein) |
| `--profile <name>` | Profilname aus `publish.yml` (`default`, `local`, `publisher`) |
| `--step <name>` | Einzelnen Schritt ausführen statt der ganzen Pipeline |
| `--root <path>` | Projekt-Wurzelverzeichnis (Standard: aktuelles Verzeichnis) |
| `--dry-run` | Pipeline simulieren, ohne Artefakte zu erzeugen |
| `--isolated` | Isolierten Lauf ohne Seiteneffekte erzwingen |

#### Docker-Builds

Für reproduzierbare Builds in einem isolierten Container:

```bash
# Docker-Image bauen und Orchestrator im Container ausführen
python -m gitbook_worker.tools.docker.run_docker orchestrator \
  --profile default --use-dynamic --rebuild

# Oder das Convenience-Skript verwenden
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

> **Hinweis**: `--profile docker` im Orchestrator ist lediglich ein Profilname und
> löst *keine* Docker-Ausführung aus. Für echte Container-Läufe immer
> `run_docker.py` verwenden.

#### Remote-Inhaltsquellen

Einträge mit `type: git` in `content.yaml` werden automatisch nach
`.gitbook-content/<lang-id>` geklont. Zugangsdaten konfigurierst du über die in
`credentialRef` benannte Umgebungsvariable (SSH-Key-Pfad oder -Inhalt). Fehlt
der Zugang, bricht das CLI mit einer klaren Fehlermeldung ab. Für CI-Caches
setze `GITBOOK_CONTENT_ROOT` auf den vorbereiteten Sprachbaum.

### Wie das eigene Projekt für optimale Ergebnisse strukturieren?

GitBook Worker erwartet eine klar definierte Verzeichnisstruktur. Je genauer du
dieser Konvention folgst, desto reibungsloser läuft die Pipeline.

#### Empfohlene Projektstruktur

```
mein-buch/
├── content.yaml              # Zentrale Sprachkonfiguration
├── de/                       # Sprachbaum (beliebig viele)
│   ├── book.json             # Buch-Metadaten (Titel, Autor, Sprache)
│   ├── publish.yml           # Build-Profile, Fonts, PDF-Optionen
│   ├── CITATION.cff          # Zitationsmetadaten (optional)
│   ├── LICENSE               # Lizenz des Buchinhalts
│   ├── content/              # Markdown-Inhalte
│   │   ├── README.md         # Bucheinleitung (Cover/Intro)
│   │   ├── SUMMARY.md        # Inhaltsverzeichnis / Kapitelreihenfolge
│   │   ├── kapitel-1/
│   │   │   └── README.md
│   │   ├── kapitel-2/
│   │   │   └── README.md
│   │   └── anhang-a.md
│   └── publish/              # Ausgabeverzeichnis (PDFs landen hier)
├── en/                       # Weiterer Sprachbaum
│   └── ...
├── fonts-storage/            # Lokaler Font-Cache (wird automatisch befüllt)
└── gitbook_worker/           # Das Toolkit (als Paket oder Submodul)
```

#### Die drei Schlüsseldateien

**1. `content.yaml`** – listet alle Sprachen und ihre Quellen:

```yaml
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: Deutscher Basisinhalt
  - id: en
    type: local
    uri: en/
    description: Englischer Inhalt
  - id: ua
    type: git
    uri: github.com:rob9999@democratic-social-wins
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

**2. `book.json`** – Buch-Metadaten im GitBook-Format:

```json
{
  "title": "Mein Buch",
  "author": "Autorenname",
  "language": "de",
  "description": "Kurze Beschreibung des Buchs.",
  "root": "content/",
  "structure": {
    "readme": "README.md",
    "summary": "SUMMARY.md"
  }
}
```

**3. `publish.yml`** – steuert Profile, Fonts und PDF-Optionen:

```yaml
version: 0.1.0
profiles:
  local:
    steps: [converter, generate_attribution, publisher]
    registry: null
  default:
    steps: [check_if_to_publish, ensure_readme, update_citation,
            converter, engineering-document-formatter,
            generate_attribution, publisher]

project:
  name: "Mein Buch"
  version: "1.0.0"
  license: "CC BY-SA 4.0"

publish:
  - build: true
    format: pdf
    source_type: folder
    source_format: markdown
    target_style: gitbook
    pdf_options:
      mainfont: "DejaVu Serif"
      sansfont: "DejaVu Sans"
      monofont: "DejaVu Sans Mono"
      mainfontfallback:
        - "Twemoji Mozilla"
        - "ERDA CC-BY CJK"
```

#### Tipps für optimale Ergebnisse

- **`SUMMARY.md` pflegen**: Diese Datei definiert die Kapitelreihenfolge und
  Hierarchie im PDF. Jeder Eintrag verweist auf eine Markdown-Datei.
- **Bilder unter `content/assets/`** oder `.gitbook/assets/` ablegen – der
  Publisher löst diese Pfade automatisch auf.
- **Ein Kapitel pro Ordner**: Lege für jedes Kapitel einen Unterordner mit
  `README.md` an. Das hält die Struktur übersichtlich und erlaubt
  kapitelspezifische Assets.
- **Frontmatter nutzen**: Setze `doc_type` in YAML-Frontmatter, um die
  Dokumentklassifikation zu steuern (z. B. `chapter`, `appendix`, `cover`).
  Ohne Frontmatter greift eine Pfad-Heuristik.
- **Fonts nur über `fonts.yml` konfigurieren**: Nie Systemfonts direkt
  referenzieren. Alle Schriftarten müssen in
  `gitbook_worker/defaults/fonts.yml` registriert sein.
- **Emojis verwenden**: Farb-Emojis (🎨 🌈 ✨) werden nativ in PDF gerendert.
  Der Publisher erkennt und konvertiert sie automatisch.

#### Weitere Sprache hinzufügen

1. Struktur von `de/` duplizieren (`content/`, `book.json`, `publish.yml`,
   `publish/`).
2. Eintrag in `content.yaml` ergänzen.
3. Gemeinsame Defaults aus `gitbook_worker/defaults/` synchronisieren.
4. `gitbook-worker validate --lang <id>` ausführen.
5. Besonderheiten in `docs/contributor-new-language.md` dokumentieren.

Ausführliche Anleitung: [docs/contributor-new-language.md](docs/contributor-new-language.md).

### Repository-Aufbau

| Pfad | Inhalt |
|---|---|
| `content.yaml` | Zentrale Sprach- und Quellenkonfiguration |
| `<lang>/` (`de/`, `en/`) | Eigenständige GitBook-Bäume mit Inhalt, Konfiguration und Ausgabe |
| `gitbook_worker/` | Python-Paket: Publishing, Konvertierung, QA, Docker-Helfer |
| `gitbook_worker/defaults/` | Gemeinsame Defaults: `fonts.yml`, `frontmatter.yml`, `readme.yml` |
| `docs/` | Nutzer-Dokumentation, Release Notes, Anleitungen |
| `gitbook_worker/docs/` | Engineering-Dokumente (Sprints, Architektur, Migrationen) |
| `tests/` | pytest-Suiten für Publishing, Orchestrierung und Emoji-QA |
| `.github/workflows/` | CI/CD-Pipelines mit dem paketierten CLI |
| `fonts-storage/` | Lokaler Font-Cache (nicht in Git, wird automatisch befüllt) |

### Font-Verwaltung & Lizenz-Compliance

Alle vom Publisher genutzten Fonts müssen explizit in
`gitbook_worker/defaults/fonts.yml` konfiguriert sein – keine hardcodierten
Fallbacks, keine automatische Systemfont-Erkennung. Dies gewährleistet:

- **Lizenz-Compliance**: Jede Font-Lizenz wird nachverfolgt und dokumentiert.
- **Automatische Attribution**: `ATTRIBUTION.md` und `LICENSE-*` werden aus der
  Konfiguration generiert.
- **Reproduzierbare Builds**: Identische Fonts in lokaler, CI- und Docker-Umgebung.
- **Fehlschlag statt Überraschung**: Der Publisher bricht ab, wenn Fonts fehlen,
  statt leere Kästchen zu erzeugen.

Details: [gitbook_worker/docs/architecture/smart-font-stack.md](gitbook_worker/docs/architecture/smart-font-stack.md).

### Entwicklung

- Abhängigkeiten in `setup.cfg`, Version in `gitbook_worker/__init__.py`
  synchron halten (aktuell 2.1.0).
- Tests: `pytest -q` aus dem Repository-Root.
- Konventionen: siehe `AGENTS.md` (Formatting, Logging, Commit-Etikette).
- Docs-Ablage: Nutzer-Docs → `docs/`, Engineering-Docs → `gitbook_worker/docs/`.

### Weiterführende Dokumentation

| Thema | Dokument |
|---|---|
| Installation & Kundenstart | [docs/customer-installation.md](docs/customer-installation.md) |
| Mehrsprachiger Inhalt | [docs/multilingual-content-guide.md](docs/multilingual-content-guide.md) |
| Neue Sprache beitragen | [docs/contributor-new-language.md](docs/contributor-new-language.md) |
| Dokumenttypen konfigurieren | [docs/Configure-Doc-Types.md](docs/Configure-Doc-Types.md) |
| Handbuch (Referenz) | [docs/HANDBOOK.md](docs/HANDBOOK.md) |
| Font-Architektur | [gitbook_worker/docs/architecture/smart-font-stack.md](gitbook_worker/docs/architecture/smart-font-stack.md) |
| Konfigurationsreferenz | [docs/configuration-reference.md](docs/configuration-reference.md) |

<details>
<summary>📋 Release-Verlauf</summary>

#### 🎉 v2.1.0 (7. Februar 2026)

- **Font-Attribution-Generator**: Neuer Workflow-Schritt erzeugt automatisch `ATTRIBUTION.md` und `LICENSE-*` aus `fonts.yml`.
- **Projektversion auf Titelseite**: `project.version` in `publish.yml` wird auf der PDF-Titelseite gerendert.
- **50+ Beispieldateien** für `de` und `en` (Zitate, Sprachproben, Emoji-Kategorien, Bildtests).

→ [docs/releases/v2.1.0.md](docs/releases/v2.1.0.md)

#### 🔧 v2.0.6 (10. Januar 2026, Hotfix)

- Heading-Normalizer folgt `SUMMARY.md`-Tiefe, behebt PDF-ToC-Versatz.
- `pypdf` als Laufzeitabhängigkeit hinzugefügt.
- Release-Prozedur dokumentiert.

→ [docs/releases/v2.0.6.md](docs/releases/v2.0.6.md)

#### v2.0.5 (8. Januar 2026, Hotfix)

- TeX-Log-Auszug bei Pandoc/LuaLaTeX-Fehlern.
- `--isolated` und `--logs-dir` für den Orchestrator.
- Emoji-Überschriften in LaTeX gehärtet.

→ [docs/releases/v2.0.5.md](docs/releases/v2.0.5.md)

#### v2.0.4 (31. Dezember 2025, Hotfix)

- Converter nutzt vollqualifizierten Modulpfad, vermeidet Kollisionen mit lokalen `tools`-Paketen.
- Kundeninstallationsanleitung hinzugefügt.

→ [docs/releases/v2.0.4.md](docs/releases/v2.0.4.md)

#### v2.0.3 (31. Dezember 2025, Hotfix)

- Emoji-Testartefakte ins pytest-Temp-Verzeichnis verschoben.
- PEP-440-konforme Versionierung (2.0.3.post1).

→ [docs/releases/v2.0.3.post1.md](docs/releases/v2.0.3.post1.md)

#### v2.0.2 (31. Dezember 2025, Hotfix)

- Doc-Type-Summary-Ausrichtung, Template-Einträge sichtbar.
- Übersetzerhinweise mit expliziten H1-Überschriften.

→ [docs/releases/v2.0.2.md](docs/releases/v2.0.2.md)

#### v2.0.1 (29. Dezember 2025, Hotfix)

- Manifest-Preflight: `project.license` wird erzwungen.
- Root-Handling und Tool-Fallback für pip-Installationen repariert.
- Dry-Run-Sicherheit verbessert.

→ [docs/releases/v2.0.1.md](docs/releases/v2.0.1.md)

#### v2.0.0 (5. Dezember 2025)

- **Mehrsprachige Architektur**: Inhalte über `content.yaml`, lokale und remote Sprachbäume.
- **Farb-Emoji-Rendering** mit Twemoji Mozilla (COLR/CPAL).
- **Smart Font Stack**: Deterministische Font-Verwaltung mit Lizenz-Compliance.
- **Docker-Volume-Mount-Architektur** für Fonts.
- **ERDA CC-BY CJK Font**: Eigene mehrsprachige Schriftart.

→ [docs/releases/v2.0.0.md](docs/releases/v2.0.0.md)

</details>

---

## 🇬🇧 English

### What Is GitBook Worker?

GitBook Worker is a Python-based CLI toolkit that turns **Markdown content into
print-ready PDF books**. It handles the entire journey from a
GitBook-compatible folder structure to a finished PDF – including table of
contents, title page, emoji rendering, font management, and license
attribution.

The pipeline consists of coordinated steps:

| Step | Purpose |
|---|---|
| **Converter** | Converts and normalises Markdown sources |
| **Engineering Formatter** | Applies uniform formatting to technical documents |
| **Attribution Generator** | Creates `ATTRIBUTION.md` and `LICENSE-*` files from the font configuration |
| **Publisher** | Builds the PDF via Pandoc + LuaLaTeX with configured fonts and fallbacks |

A single CLI command orchestrates all steps – locally, in Docker, or in
GitHub Actions.

### Why and When to Use GitBook Worker?

GitBook Worker is the right tool when you need to:

- **Publish Markdown books as PDF** without writing LaTeX by hand.
- **Manage multilingual book projects** from a single repository structure
  (e.g. `de/`, `en/`, `ua/`).
- **Ensure reproducible builds** – whether locally, in CI/CD, or inside a
  Docker container, the output is identical.
- **Render colour emojis in PDF** (Twemoji Mozilla COLR/CPAL).
- **Guarantee font license compliance**: every font is declared in `fonts.yml`,
  attribution is generated automatically.
- **Convert existing GitBook projects** (with `SUMMARY.md` and `book.json`)
  into high-quality PDFs offline.

> **Not suited for**: pure HTML/web output (use GitBook itself), projects
> without Markdown sources, or single-file conversions (a single Markdown file
> would work if the overhead is justified, otherwise use Pandoc directly).

### How to Use GitBook Worker?

#### Prerequisites

- Python ≥ 3.10
- Pandoc and TeX Live (LuaLaTeX) – for PDF generation
- Optional: Docker Desktop – for isolated builds

#### Installation

```bash
python -m pip install --upgrade pip
pip install -e .          # editable / dev mode (recommended)
# or
pip install dist/gitbook_worker-2.1.0-py3-none-any.whl   # pre-built distribution
```

#### Quick Start

```bash
# Run the full pipeline for the German book
gitbook-worker run --lang de --profile local

# Run only the publisher step
gitbook-worker run --lang de --step publisher

# Validate the manifest without running the pipeline
gitbook-worker validate --lang de
```

#### Key CLI Options

| Option | Description |
|---|---|
| `--lang <id>` | Select language (must be defined in `content.yaml`) |
| `--profile <name>` | Profile name from `publish.yml` (`default`, `local`, `publisher`) |
| `--step <name>` | Run a single step instead of the full pipeline |
| `--root <path>` | Project root directory (default: current directory) |
| `--dry-run` | Simulate the pipeline without producing artefacts |
| `--isolated` | Force an isolated run without side effects |

#### Docker Builds

For reproducible builds in an isolated container:

```bash
# Build Docker image and run orchestrator inside the container
python -m gitbook_worker.tools.docker.run_docker orchestrator \
  --profile default --use-dynamic --rebuild

# Or use the convenience script
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

> **Note**: `--profile docker` in the orchestrator is merely a profile name and
> does *not* trigger Docker execution. For actual container runs, always use
> `run_docker.py`.

#### Remote Content Sources

Entries with `type: git` in `content.yaml` are automatically cloned into
`.gitbook-content/<lang-id>`. Credentials are configured via the environment
variable named in `credentialRef` (SSH key path or contents). If the credential
is missing, the CLI aborts with a clear error. For CI caches, set
`GITBOOK_CONTENT_ROOT` to the prepared language tree.

### How to Structure Your Project for Optimal Results?

GitBook Worker expects a well-defined directory layout. The closer you follow
this convention, the smoother the pipeline runs.

#### Recommended Project Structure

```
my-book/
├── content.yaml              # Central language configuration
├── de/                       # Language tree (as many as you need)
│   ├── book.json             # Book metadata (title, author, language)
│   ├── publish.yml           # Build profiles, fonts, PDF options
│   ├── CITATION.cff          # Citation metadata (optional)
│   ├── LICENSE               # Content license
│   ├── content/              # Markdown content
│   │   ├── README.md         # Book introduction (cover/intro)
│   │   ├── SUMMARY.md        # Table of contents / chapter order
│   │   ├── chapter-1/
│   │   │   └── README.md
│   │   ├── chapter-2/
│   │   │   └── README.md
│   │   └── appendix-a.md
│   └── publish/              # Output directory (PDFs go here)
├── en/                       # Another language tree
│   └── ...
├── fonts-storage/            # Local font cache (auto-populated)
└── gitbook_worker/           # The toolkit (as package or submodule)
```

#### The Three Key Files

**1. `content.yaml`** – lists all languages and their sources:

```yaml
version: 1.0.0
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
    uri: github.com:rob9999@democratic-social-wins
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

**2. `book.json`** – book metadata in GitBook format:

```json
{
  "title": "My Book",
  "author": "Author Name",
  "language": "en",
  "description": "A short description of the book.",
  "root": "content/",
  "structure": {
    "readme": "README.md",
    "summary": "SUMMARY.md"
  }
}
```

**3. `publish.yml`** – controls profiles, fonts, and PDF options:

```yaml
version: 0.1.0
profiles:
  local:
    steps: [converter, generate_attribution, publisher]
    registry: null
  default:
    steps: [check_if_to_publish, ensure_readme, update_citation,
            converter, engineering-document-formatter,
            generate_attribution, publisher]

project:
  name: "My Book"
  version: "1.0.0"
  license: "CC BY-SA 4.0"

publish:
  - build: true
    format: pdf
    source_type: folder
    source_format: markdown
    target_style: gitbook
    pdf_options:
      mainfont: "DejaVu Serif"
      sansfont: "DejaVu Sans"
      monofont: "DejaVu Sans Mono"
      mainfontfallback:
        - "Twemoji Mozilla"
        - "ERDA CC-BY CJK"
```

#### Tips for Optimal Results

- **Maintain `SUMMARY.md`**: this file defines chapter order and hierarchy in
  the PDF. Every entry points to a Markdown file.
- **Place images in `content/assets/`** or `.gitbook/assets/` – the publisher
  resolves these paths automatically.
- **One chapter per folder**: create a subfolder with `README.md` for each
  chapter. This keeps the structure tidy and allows chapter-specific assets.
- **Use front matter**: set `doc_type` in YAML front matter to control document
  classification (e.g. `chapter`, `appendix`, `cover`). Without front matter,
  a path-based heuristic applies.
- **Configure fonts only via `fonts.yml`**: never reference system fonts
  directly. All typefaces must be registered in
  `gitbook_worker/defaults/fonts.yml`.
- **Use emojis freely**: colour emojis (🎨 🌈 ✨) are rendered natively in PDF.
  The publisher detects and converts them automatically.

#### Adding Another Language

1. Duplicate the structure from `de/` (`content/`, `book.json`, `publish.yml`,
   `publish/`).
2. Add an entry to `content.yaml`.
3. Sync shared defaults from `gitbook_worker/defaults/`.
4. Run `gitbook-worker validate --lang <id>`.
5. Document any specifics in `docs/contributor-new-language.md`.

Full walkthrough: [docs/contributor-new-language.md](docs/contributor-new-language.md).

### Repository Layout

| Path | Contents |
|---|---|
| `content.yaml` | Central language and source configuration |
| `<lang>/` (`de/`, `en/`) | Self-contained GitBook trees with content, config, and output |
| `gitbook_worker/` | Python package: publishing, conversion, QA, Docker helpers |
| `gitbook_worker/defaults/` | Shared defaults: `fonts.yml`, `frontmatter.yml`, `readme.yml` |
| `docs/` | User documentation, release notes, guides |
| `gitbook_worker/docs/` | Engineering docs (sprints, architecture, migrations) |
| `tests/` | pytest suites for publishing, orchestration, and emoji QA |
| `.github/workflows/` | CI/CD pipelines using the packaged CLI |
| `fonts-storage/` | Local font cache (not in Git, auto-populated) |

### Font Management & License Compliance

All fonts used by the publisher must be explicitly configured in
`gitbook_worker/defaults/fonts.yml` – no hardcoded fallbacks, no automatic
system font discovery. This ensures:

- **License Compliance**: every font license is tracked and documented.
- **Automatic Attribution**: `ATTRIBUTION.md` and `LICENSE-*` are generated from
  the configuration.
- **Reproducible Builds**: identical fonts across local, CI, and Docker
  environments.
- **Failure over Surprise**: the publisher aborts when fonts are missing rather
  than producing empty boxes.

Details: [gitbook_worker/docs/architecture/smart-font-stack.md](gitbook_worker/docs/architecture/smart-font-stack.md).

### Development

- Keep dependencies in `setup.cfg` and version in `gitbook_worker/__init__.py`
  in sync (currently 2.1.0).
- Tests: `pytest -q` from the repository root.
- Conventions: see `AGENTS.md` (formatting, logging, commit etiquette).
- Documentation: user docs → `docs/`, engineering docs → `gitbook_worker/docs/`.

### Further Documentation

| Topic | Document |
|---|---|
| Installation & Customer Start | [docs/customer-installation.md](docs/customer-installation.md) |
| Multilingual Content | [docs/multilingual-content-guide.md](docs/multilingual-content-guide.md) |
| Contributing a New Language | [docs/contributor-new-language.md](docs/contributor-new-language.md) |
| Configuring Document Types | [docs/Configure-Doc-Types.md](docs/Configure-Doc-Types.md) |
| Handbook (Reference) | [docs/HANDBOOK.md](docs/HANDBOOK.md) |
| Font Architecture | [gitbook_worker/docs/architecture/smart-font-stack.md](gitbook_worker/docs/architecture/smart-font-stack.md) |
| Configuration Reference | [docs/configuration-reference.md](docs/configuration-reference.md) |

<details>
<summary>📋 Release History</summary>

#### 🎉 v2.1.0 (February 7, 2026)

- **Font Attribution Generator**: new workflow step auto-creates `ATTRIBUTION.md` and `LICENSE-*` from `fonts.yml`.
- **Project Version on Title Page**: `project.version` in `publish.yml` is rendered on the PDF title page.
- **50+ example files** for `de` and `en` (citations, language samples, emoji categories, image tests).

→ [docs/releases/v2.1.0.md](docs/releases/v2.1.0.md)

#### 🔧 v2.0.6 (January 10, 2026, hotfix)

- Heading normaliser follows `SUMMARY.md` depth, fixes PDF ToC misalignment.
- `pypdf` added as runtime dependency.
- Release procedure documented.

→ [docs/releases/v2.0.6.md](docs/releases/v2.0.6.md)

#### v2.0.5 (January 8, 2026, hotfix)

- TeX log excerpt on Pandoc/LuaLaTeX failure.
- `--isolated` and `--logs-dir` for the orchestrator.
- Emoji heading LaTeX macro hardened.

→ [docs/releases/v2.0.5.md](docs/releases/v2.0.5.md)

#### v2.0.4 (December 31, 2025, hotfix)

- Converter uses fully qualified module path, avoiding collisions with local `tools` packages.
- Customer installation guide added.

→ [docs/releases/v2.0.4.md](docs/releases/v2.0.4.md)

#### v2.0.3 (December 31, 2025, hotfix)

- Emoji test artifacts moved to pytest temp directory.
- PEP 440 compliant versioning (2.0.3.post1).

→ [docs/releases/v2.0.3.post1.md](docs/releases/v2.0.3.post1.md)

#### v2.0.2 (December 31, 2025, hotfix)

- Doc-type summary alignment, template entries surfaced.
- Translator notes with explicit H1 headings.

→ [docs/releases/v2.0.2.md](docs/releases/v2.0.2.md)

#### v2.0.1 (December 29, 2025, hotfix)

- Manifest preflight: `project.license` enforced.
- Root handling and tool fallback for pip installs fixed.
- Dry-run safety improved.

→ [docs/releases/v2.0.1.md](docs/releases/v2.0.1.md)

#### v2.0.0 (December 5, 2025)

- **Multilingual architecture**: content via `content.yaml`, local and remote language trees.
- **Colour emoji rendering** with Twemoji Mozilla (COLR/CPAL).
- **Smart Font Stack**: deterministic font management with license compliance.
- **Docker volume-mount architecture** for fonts.
- **ERDA CC-BY CJK Font**: custom multilingual typeface.

→ [docs/releases/v2.0.0.md](docs/releases/v2.0.0.md)

</details>

---

*📄 Vollständige Dokumentation / Full documentation → [docs/](docs/) · [gitbook_worker/docs/](gitbook_worker/docs/)*
