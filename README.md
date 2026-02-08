# GitBook Worker (v2.1.0)

🇩🇪 [Deutsch](#-deutsch) · 🇬🇧 [English](#-english)

---

## 🇩🇪 Deutsch

**Aktuelles Release**: v2.1.0 (7. Februar 2026) – [Release Notes](docs/releases/v2.1.0.md)

GitBook Worker liefert die mehrsprachige 2.x-Linie. Das Python-Paket wird über
`pip install -e .` installiert, und die Publishing-Pipeline wird durch `content.yaml`
gesteuert, die jeden Sprachbaum auflistet (z. B. `de/`, `en/`). Das CLI wählt eine
Sprache über `--lang` und führt die Orchestrierungs-/Publishing-Schritte für diesen
Inhaltsbaum aus.

> Kundenguide (Installation & Start): siehe [docs/customer-installation.md](docs/customer-installation.md).

### 🎉 Neu in v2.1.0

- **Font-Attribution-Generator**: Neuer `generate_attribution`-Workflow-Schritt erzeugt automatisch `ATTRIBUTION.md` und `LICENSE-*`-Dateien aus `fonts.yml` für lizenzkonformes Publizieren.
- **Projektversion auf Titelseite**: Optionales `project.version` in `publish.yml` (oder `"version"` in `book.json`) wird auf der PDF-Titelseite neben dem Datum angezeigt, z. B. *2026-01-08 · Version 1.0.0*.
- **Umfangreicher Beispielinhalt**: 50+ mehrsprachige Beispieldateien (Zitate, erweitertes Markdown, 100+ Sprachproben, Emoji-Kategorien, Bildtests) für `de` und `en`.
- Release-Tag: `release-v.2.1.0`; Paketversion: 2.1.0.

Siehe [docs/releases/v2.1.0.md](docs/releases/v2.1.0.md) für das vollständige Changelog.

### 🔧 Änderungen in v2.0.6 (Hotfix)

- Heading-Normalizer folgt nun der `SUMMARY.md`-Tiefe und behält dokumentinterne Kaskaden bei – behebt PDF-ToC-Versatz.
- `ProjectMetadata` toleriert fehlende Daten (Standard `None`) und behält den Policy-Standard bei.
- `pypdf` zu Laufzeitabhängigkeiten hinzugefügt für CLI-Tools, die PDF-Hilfsmittel importieren.
- Release-Prozedur dokumentiert in `gitbook_worker/docs/how-to-release/release-procedure.md`.
- Release-Tag: `release-v.2.0.6-hotfix`; Paketversion: 2.0.6.post1.

Siehe [docs/releases/v2.0.6.md](docs/releases/v2.0.6.md) für Details.

<details>
<summary>🔙 Highlights aus v2.0.5 und v2.0.0</summary>

#### v2.0.5 (Hotfix)
- Publisher gibt relevanten TeX-`.log`-Ausschnitt bei Pandoc/LuaLaTeX-Fehler aus.
- Orchestrator erhielt `--isolated` und `--logs-dir`, wählt automatisch `<root>/content.yaml`.
- Emoji-Überschriften: LaTeX-Makro-Behandlung gehärtet, um Bookmark-Abstürze mit `hyperref` zu vermeiden.

#### v2.0.0
**Kritischer Fix**: Farb-Emoji-Rendering mit **Twemoji Mozilla v0.7.0** (COLR/CPAL).

**Docker-Architektur**: Volume-Mount-Font-Verwaltung statt statischem COPY.

**Lizenz-Compliance**: Alle Fonts erzwungen über `gitbook_worker/defaults/fonts.yml`.

**Wichtige Änderungen**:
- ✅ Farb-Emojis rendern korrekt in PDF-Ausgabe (🎨 🌈 ✨)
- ✅ Docker Volume-Mount-Architektur für Fonts (keine Rebuilds nötig)
- ✅ Explizite Font-Konfigurationserzwingung via `fonts.yml`
- ✅ Windows/Linux Pfadkompatibilität für Docker Desktop
- ⚠️ Breaking: Docker-Font-Verwaltung geändert (siehe Release Notes)

Siehe [docs/releases/v2.0.5.md](docs/releases/v2.0.5.md) · [docs/releases/v2.0.0.md](docs/releases/v2.0.0.md)
</details>

### Schnellstart

### Schnellstart

```bash
python -m pip install --upgrade pip
pip install -e .

# Orchestrator für das deutsche Buch ausführen
gitbook-worker run --lang de --profile default

# Manifest validieren ohne Pipeline-Lauf
gitbook-worker validate --lang de

# Andere Sprache wählen (sofern in content.yaml definiert)
gitbook-worker run --lang en --step publisher
```

`content.yaml` ist die zentrale Quelle für verfügbare Sprachen:

```yaml
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: Deutscher Basisinhalt
  - id: ua
    type: git
    uri: github.com:rob9999@democratic-social-wins
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

Der Orchestrator liest diese Datei automatisch; Remote-Einträge nutzen künftig
`credentialRef` zum Abrufen privater Inhalte über Umgebungsgeheimnisse oder CI-Secrets.

### Remote-Inhaltsquellen

- Einträge mit `type: git` werden automatisch nach `.gitbook-content/<lang-id>` geklont,
  sobald `gitbook-worker ... --lang <id>` ausgeführt wird.
- Zugangsdaten werden über die in `credentialRef` benannte Umgebungsvariable bereitgestellt.
  Die Variable kann einen absoluten Pfad zu einem SSH-Privatschlüssel oder den Schlüsselinhalt
  selbst enthalten. Inline-Schlüssel werden mit restriktiven Berechtigungen nach
  `.gitbook-content/keys/<lang>.key` geschrieben und über `GIT_SSH_COMMAND` verwendet.
- Fehlt der Zugang, bricht das CLI mit einer klaren Fehlermeldung ab, damit Geheimnisse
  niemals in Manifeste gelangen.
- Um einen bestehenden Checkout wiederzuverwenden (z. B. CI-Cache), setze `GITBOOK_CONTENT_ROOT`
  auf den Pfad des vorbereiteten Sprachbaums; das CLI überspringt dann das Klonen.

### Weiteren Sprachbaum hinzufügen

1. Struktur von `de/` duplizieren (oder von einem leeren Remote-Repo starten), damit die neue
   Sprache `content/`, `book.json`, `publish/` und optionale Assets hat.
2. Eintrag in `content.yaml` mit neuer Sprach-`id`, `type` und `uri` ergänzen. Für Remote-Quellen
   `credentialRef` definieren und Secret außerhalb von Git speichern.
3. Gemeinsame Defaults (Front Matter, Fonts, README-Snippets) aus `gitbook_worker/defaults/`
   synchronisieren, damit PDF/HTML-Ausgabe den anderen Sprachen entspricht.
4. `gitbook-worker validate --lang <id>` (oder `run`) ausführen, um sicherzustellen, dass
   Manifeste und Publish-Targets aufgelöst werden.
5. Besonderheiten in `docs/contributor-new-language.md` dokumentieren, damit das Team die
   Einrichtung nachvollziehen kann.

Die vollständige Anleitung für Beitragende steht in `docs/contributor-new-language.md`.

### Repository-Aufbau

- `content.yaml` – listet jede Sprache/Inhaltsquelle samt Credential-Handles.
- `<lang>/` (z. B. `de/`, `en/`) – eigenständige GitBook-Bäume mit `content/`,
  `book.json`, `publish/`, `CITATION.cff` usw.
- `gitbook_worker/` – Python-Paket mit Publishing, Konvertierung, QA und Docker-Helfern.
- `docs/` – Nutzer-Guides (z. B. `docs/multilingual-content-guide.md`,
  `docs/contributor-new-language.md`, `docs/releases/v2.1.0.md`).
- `gitbook_worker/docs/` – Engineering-Dokumente wie Sprintpläne, Migrationen, RFCs und
  das archivierte Legacy-Paket-Snapshot unter `gitbook_worker/docs/archive/`.
- `tests/` – pytest-Suiten für Publishing, Orchestrierung und Emoji-QA.
- `.github/workflows/` – CI-Einstiegspunkte mit dem paketierten CLI.
- `tools/` – veralteter Import-Shim für Legacy-`tools.*`-Pfade (Kompatibilität).

### GitHub-Actions-Vorlagen

Workflows unter `.github/workflows/` bauen das Docker-Image aus
`gitbook_worker/tools/docker/Dockerfile.dynamic` und rufen denselben Orchestrator-
Einstiegspunkt auf, der auch lokal genutzt wird. Diese Workflows kopieren oder
erweitern, um das Paket in andere Repositories zu integrieren. Das statische Image
(`gitbook_worker/tools/docker/Dockerfile`) bleibt für Air-Gap-Runner verfügbar;
die Hilfsskripte verwenden standardmäßig die dynamische Variante, damit Font- und
LaTeX-Abhängigkeiten mit CI synchron bleiben.

### Font-Verwaltung & Lizenz-Compliance

**Kritische Designentscheidung**: Alle vom Publisher genutzten Fonts MÜSSEN explizit in
`gitbook_worker/defaults/fonts.yml` konfiguriert sein. Keine hardcodierten Font-Fallbacks
oder automatische Systemfont-Erkennung erlaubt. Dies stellt sicher:

- **Lizenz-Compliance**: Jede Font-Lizenz (CC-BY, MIT, OFL etc.) wird nachverfolgt und dokumentiert
- **Attributionspflichten**: Korrekte Attribution kann jederzeit für alle genutzten Fonts generiert werden
- **Reproduzierbare Builds**: Identische Font-Konfiguration in lokaler, CI/CD- und Docker-Umgebung
- **Keine versteckten Abhängigkeiten**: Publisher schlägt explizit fehl, wenn konfigurierte Fonts nicht verfügbar sind

Die `Dockerfile.dynamic` liest `fonts.yml` und installiert nur konfigurierte Fonts. Jeder Font-Eintrag
benötigt `name`, `license`, `license_url` und entweder `download_url` oder `paths`. Siehe
`gitbook_worker/defaults/fonts.yml` für das vollständige Font-Register und
`gitbook_worker/docs/architecture/smart-font-stack.md` für die Architektur.

### Entwicklung

- Abhängigkeiten in `setup.cfg` ergänzen und `__version__` in `gitbook_worker/__init__.py`
  synchron zum Release halten (aktuell 2.1.0).
- Tests lokal mit `pytest -q` aus dem Repository-Root ausführen; sprachspezifische Fixtures
  liegen unter `de/`, sodass CI jeden Baum unabhängig mounten kann.
- Bevorzugte Einstiegspunkte: `python -m gitbook_worker.tools.workflow_orchestrator ...` oder
  das Konsolenskript `gitbook-worker` mit `--lang <id>`.
- Remote-Sprachen werden unter `.gitbook-content/` gecacht, damit wiederholte Läufe denselben
  Checkout wiederverwenden und trotzdem Updates ziehen.
- Repository-weite Konventionen stehen in der Root-`AGENTS.md`; es gibt keine verschachtelten Overrides.
- Dokumentenablage: Nutzer-Docs in `docs/`, Engineering-Docs in `gitbook_worker/docs/`.

#### Docker-Builds

Um Builds in einem isolierten Docker-Container auszuführen (empfohlen für reproduzierbare CI-ähnliche Umgebung):

```bash
# Image bauen und Orchestrator im Container ausführen
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile default --use-dynamic --rebuild

# Oder das Convenience-Skript verwenden
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

**Wichtig**: Die `workflow_orchestrator`-CLI hat eine `--profile docker`-Option, aber dies ist nur ein
Profilname – es löst KEINE Docker-Ausführung aus. Um innerhalb von Docker auszuführen, nutze das
`run_docker.py`-Modul, das das Image baut, einen Container startet, den Workspace nach `/workspace`
mountet und den Orchestrator darin ausführt.

---

## 🇬🇧 English

**Latest Release**: v2.1.0 (February 7, 2026) – [Release Notes](docs/releases/v2.1.0.md)

GitBook Worker ships the multi-language 2.x line. The Python package installs via
`pip install -e .`, and the publishing pipeline is driven by `content.yaml`, which lists
every language tree (e.g., `de/`, `en/`). The CLI picks a language via `--lang` and runs
the orchestration/publishing steps for that content root.

> Customer guide (installation & getting started): see [docs/customer-installation.md](docs/customer-installation.md).

### 🎉 What's New in v2.1.0

- **Font Attribution Generator**: New `generate_attribution` workflow step auto-creates `ATTRIBUTION.md` and `LICENSE-*` files from `fonts.yml`, ensuring license compliance without manual effort.
- **Project Version on Title Page**: New optional `project.version` in `publish.yml` (or `"version"` in `book.json`) is rendered on the PDF title page alongside the date, e.g. *2026-01-08 · Version 1.0.0*.
- **Comprehensive Example Content**: 50+ multilingual example files (citations, advanced Markdown, 100+ language samples, emoji categories, image tests) for both `de` and `en`.
- Release tag: `release-v.2.1.0`; packaging version: 2.1.0.

See [docs/releases/v2.1.0.md](docs/releases/v2.1.0.md) for the full changelog.

### 🔧 What Changed in v2.0.6 (hotfix)

- Heading normalizer now follows `SUMMARY.md` depth while preserving in-document cascades, fixing PDF ToC misalignment.
- `ProjectMetadata` tolerates missing dates (default `None`) and retains policy default.
- Added `pypdf` to runtime dependencies for CLI tools that import PDF utilities.
- Documented release procedure in `gitbook_worker/docs/how-to-release/release-procedure.md`.
- Release tag: `release-v.2.0.6-hotfix`; packaging version: 2.0.6.post1.

See [docs/releases/v2.0.6.md](docs/releases/v2.0.6.md) for details.

<details>
<summary>🔙 Highlights from v2.0.5 and v2.0.0</summary>

#### v2.0.5 (hotfix)
- Publisher prints relevant TeX `.log` excerpt on Pandoc/LuaLaTeX failure.
- Orchestrator gained `--isolated` and `--logs-dir`, auto-picks `<root>/content.yaml`.
- Emoji headings: hardened LaTeX macro handling to avoid bookmark crashes with `hyperref`.

#### v2.0.0
**Critical Fix**: Color emoji rendering using **Twemoji Mozilla v0.7.0** (COLR/CPAL).

**Docker Architecture**: Volume-mount font management instead of static COPY.

**License Compliance**: All fonts enforced via `gitbook_worker/defaults/fonts.yml`.

**Key Changes**:
- ✅ Color emojis render correctly in PDF output (🎨 🌈 ✨)
- ✅ Docker volume-mount architecture for fonts (no rebuilds needed)
- ✅ Explicit font configuration enforcement via `fonts.yml`
- ✅ Windows/Linux path compatibility for Docker Desktop
- ⚠️ Breaking: Docker font management changed (see release notes)

See [docs/releases/v2.0.5.md](docs/releases/v2.0.5.md) · [docs/releases/v2.0.0.md](docs/releases/v2.0.0.md)
</details>

### Quick Start

```bash
python -m pip install --upgrade pip
pip install -e .

# Run the orchestrator against the German book
gitbook-worker run --lang de --profile default

# Validate a manifest without running the pipeline
gitbook-worker validate --lang de

# Pick a different language (if defined in content.yaml)
gitbook-worker run --lang en --step publisher
```

`content.yaml` is the single source of truth for available languages:

```yaml
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: German baseline content
  - id: ua
    type: git
    uri: github.com:rob9999@democratic-social-wins
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

The orchestrator reads this file automatically; remote entries will later use
`credentialRef` to fetch private content via env secrets or CI secret stores.

### Remote Content Sources

- Entries with `type: git` are cloned automatically into `.gitbook-content/<lang-id>`
  whenever you run `gitbook-worker ... --lang <id>`.
- Provide credentials through the environment variable named in `credentialRef`. The
  variable can contain either an absolute path to an SSH private key or the key contents
  themselves. Inline keys are written to `.gitbook-content/keys/<lang>.key` with
  restrictive permissions and used via `GIT_SSH_COMMAND`.
- If the credential is missing, the CLI aborts with a clear error so secrets never leak
  into manifests.
- To reuse an existing checkout (for example a CI cache), set `GITBOOK_CONTENT_ROOT` to
  the path of the prepared language tree and the CLI will skip cloning.

### Add Another Language Tree

1. Duplicate the structure from `de/` (or start from an empty remote repo) so the new
   language has `content/`, `book.json`, `publish/`, and optional assets.
2. Append an entry to `content.yaml` with the new language `id`, `type`, and `uri`. For
   remote sources, define a `credentialRef` and store the secret outside git.
3. Sync shared defaults (front matter, fonts, README snippets) from
   `gitbook_worker/defaults/` so PDF/HTML output matches the other languages.
4. Run `gitbook-worker validate --lang <id>` (or `run`) to ensure manifests and publish
   targets resolve.
5. Document any special steps in `docs/contributor-new-language.md` so the rest of the
   team can reproduce the setup.

The dedicated contributor walkthrough lives in `docs/contributor-new-language.md`.

### Repository Layout

- `content.yaml` – lists every language/content source plus credential handles.
- `<lang>/` (e.g., `de/`, `en/`) – self-contained GitBook trees containing `content/`,
  `book.json`, `publish/`, `CITATION.cff`, etc.
- `gitbook_worker/` – Python package with publishing, conversion, QA, and Docker helpers.
- `docs/` – user-facing guides (e.g., `docs/multilingual-content-guide.md`,
  `docs/contributor-new-language.md`, `docs/releases/v2.1.0.md`).
- `gitbook_worker/docs/` – engineering docs such as sprint plans, migrations, RFCs, and
  the archived legacy package snapshot under `gitbook_worker/docs/archive/`.
- `tests/` – pytest suites covering publishing, orchestration, and emoji QA.
- `.github/workflows/` – CI entrypoints using the packaged CLI.
- `tools/` – deprecated import shim for legacy `tools.*` paths (kept for compatibility).

### GitHub Actions Templates

Workflows under `.github/workflows/` build the Docker image from
`gitbook_worker/tools/docker/Dockerfile.dynamic` and call the same orchestrator
entrypoint used locally. Copy or extend these workflows to integrate the package
into other repositories. The static image (`gitbook_worker/tools/docker/Dockerfile`)
remains available for air-gapped runners; the helper scripts default to the
dynamic variant so font and LaTeX dependencies stay in sync with CI.

### Font Management & License Compliance

**Critical Design Decision**: All fonts used by the publisher MUST be explicitly configured in
`gitbook_worker/defaults/fonts.yml`. No hardcoded font fallbacks or automatic system font
discovery is allowed. This ensures:

- **License Compliance**: Every font's license (CC-BY, MIT, OFL, etc.) is tracked and documented
- **Attribution Requirements**: We can always generate proper attribution for all fonts used
- **Reproducible Builds**: Identical font configuration across local, CI/CD, and Docker environments
- **No Hidden Dependencies**: Publisher fails explicitly if configured fonts are unavailable

The `Dockerfile.dynamic` reads `fonts.yml` and installs only the configured fonts. Each font entry
must include `name`, `license`, `license_url`, and either `download_url` or `paths`. See
`gitbook_worker/defaults/fonts.yml` for the complete font registry and
`gitbook_worker/docs/architecture/smart-font-stack.md` for the architecture.

### Development

- Add dependencies to `setup.cfg` and keep `__version__` in `gitbook_worker/__init__.py` in sync
  with the packaged release (currently 2.1.0).
- Run tests locally with `pytest -q` from the repository root; language-specific fixtures live
  under `de/` so CI can mount each tree independently.
- Preferred entrypoints: `python -m gitbook_worker.tools.workflow_orchestrator ...` or the
  console script `gitbook-worker` with `--lang <id>`.
- Remote languages are cached under `.gitbook-content/` so repeated runs reuse the same
  checkout while still pulling updates.
- Repository-wide conventions live in the root `AGENTS.md`; there are no nested overrides.
- Documentation placement: user docs in `docs/`, engineering docs in `gitbook_worker/docs/`.

#### Docker Builds

To run builds in an isolated Docker container (recommended for reproducible CI-like environment):

```bash
# Build image and run orchestrator inside container
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile default --use-dynamic --rebuild

# Or use the convenience script
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

**Important**: The `workflow_orchestrator` CLI has a `--profile docker` option but this is just a
profile name—it does NOT trigger Docker execution. To run inside Docker, use the `run_docker.py`
module which builds the image, starts a container, mounts your workspace to `/workspace`, and
executes the orchestrator inside.

---

*📄 Vollständige Dokumentation / Full documentation → [docs/](docs/) · [gitbook_worker/docs/](gitbook_worker/docs/)*
