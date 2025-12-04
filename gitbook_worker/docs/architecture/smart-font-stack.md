---
version: 0.2.0
date: 2025-11-29
history:
  - "2025-11-29: Initial smart font stack concept (GitHub Copilot)."
   - "2025-11-29: Erste Implementierung (smart_font_stack.py + fonts sync CLI)."
---

# Smart Font Stack & Installer Concept

## Hintergrund & Zielbild
- **Was existiert heute?** `gitbook_worker/defaults/fonts.yml` liefert die kanonische Definition aller Schriftrollen. `font_config.py` lädt diese Definition (inkl. Overrides aus `publish.yml`) und `publisher.py` registriert Fonts bei Pandoc/LuaLaTeX. Es gibt jedoch keinen standardisierten Prozess, um Schriftdateien plattformübergreifend herunterzuladen, lokal zu speichern und wiederzuverwenden.
- **Was fehlt?** Tests scheitern, sobald Fonts nicht bereits im System vorhanden sind. Außerdem verbietet der Workflow das Überschreiben der Default-Datei im Repo.
- **Zielsetzung:** Ein deterministischer, wiederholbarer Installer, der exakt die Schriften aus `fonts.yml → publish.yml` beschafft, lokal (oder im Container) persistiert, anschließend ein temporäres Laufzeit-`fonts.meta.yml` erzeugt und dieses nahtlos in den bestehenden Loader integriert. Das Konzept muss für lokale Entwickler:innen, CI-Läufe, Docker-Container und das geplante PyPI-Paket identisch funktionieren.

## Leitprinzipien

### 1. Single Source of Truth
`gitbook_worker/defaults/fonts.yml` bleibt unverändert. Repository-spezifische oder benutzerdefinierte Anpassungen passieren ausschließlich via `publish.yml` bzw. optionalen CLI-Parametern.

### 2. Deterministische Reproduzierbarkeit
Jeder Lauf produziert dieselbe Font-Struktur, sofern Version und URLs gleich bleiben. Hashes der Downloads sichern Integrität.

### 3. Plattformabstraktion
Ein gemeinsames API, das Windows/macOS/Linux (nativ) und Docker-Container gleich behandelt.

### 4. Lokale Cache-Strategie
Fonts landen in einem wohldefinierten Cache (`%LOCALAPPDATA%\gitbook-worker\fonts`, `~/Library/Application Support/gitbook-worker/fonts`, `~/.cache/gitbook-worker/fonts`). Container nutzen `/var/cache/gitbook-worker/fonts`.

### 5. No Hardcoded Font Fallbacks (License Compliance)
**CRITICAL DESIGN DECISION**: The publisher MUST NEVER use unconfigured system fonts as automatic fallbacks. All fonts must be explicitly configured in `fonts.yml` to ensure:

- **License Compliance**: Every font's license (CC-BY, MIT, OFL, etc.) is tracked and documented
- **Attribution Requirements**: We can always generate proper attribution for all fonts used in published documents
- **Reproducible Builds**: Identical font configuration across local development, CI/CD, and Docker environments
- **Legal Safety**: No risk of inadvertently using proprietary or restricted fonts

If a configured font is not available, the build MUST fail with a clear error message and installation instructions. Silent fallbacks to system fonts (like "Noto Color Emoji", "Segoe UI Emoji", etc.) are explicitly forbidden.

This principle applies to:
- Publisher font selection (`publisher.py::_select_emoji_font`)
- Docker image font installation (`Dockerfile.dynamic`)
- Font configuration loader (`font_config.py`)
- Smart font stack installer (`smart_font_stack.py`)

The entire font management infrastructure exists to guarantee we can fulfill attribution obligations and license requirements for every font in every published document.

## Schichtenmodell der Font-Konfiguration
1. **Base Layer:** `gitbook_worker/defaults/fonts.yml` (keine Änderungen im Repo).
2. **Manifest Layer:** `publish.yml → fonts` überschreibt Pfade/Namen projektabhängig.
3. **Smart Layer (neu):** Runtime-Generator erzeugt `fonts.meta.yml` in einem Temp-Verzeichnis. Diese Datei spiegelt die final verwendeten Pfade (Cache oder Systempfade) wider und wird beim Start des Publishers eingebunden (z.B. über `SMART_FONT_CONFIG`-Env oder CLI-Flag `--font-config`).
4. **Session Layer (optional):** Ad-hoc Overrides via CLI für Einzeltests.

## Geplanter Ablauf "Smart Font Stack"
1. **Font-Selektion:** `FontConfigLoader` (Base + Manifest) liefert die gewünschten Fonts (Name + Download-URL + Pfad-Kandidaten).
2. **Existenzprüfung:**
   - Prüfe in dieser Reihenfolge:
     1. Bereits konfigurierte Pfade aus Manifest/Base.
     2. OS-spezifische Standardpfade (`C:\Windows\Fonts`, `/System/Library/Fonts`, `/usr/share/fonts`, `texmf-local`).
     3. Git-Repository-Assets (`.github/fonts/**`).
     4. GitBook Worker Cache.
   - Optional: Verwende `fc-list`/`Get-FontInfo`/`atsutil` wenn verfügbar, um installierte Fonts zu erkennen.
3. **Download & Installation:**
   - Falls kein Treffer: Lade Datei von `download_url` (oder `url`) nach `CACHE/<font-key>/<version>/<filename>`.
   - Validierung über SHA256 (optional in `fonts.yml` ergänzen).
   - Extrahiere Archive (zip/tgz) falls nötig und filtere unterstützte Formate (`.ttf`, `.otf`, `.ttc`).
4. **Registrierung im Cache:**
   - Speichere Metadaten (Name, Version, Quelle, Lizenz) in `CACHE/index.json`.
   - Halte pro Font-Key eine Liste aller lokal verfügbaren Dateien.
5. **Meta-Konfiguration erzeugen:**
   - Schreibe `fonts.meta.yml` mit identischer Struktur wie `fonts.yml`, aber mit absolut aufgelösten Pfaden (inkl. Cache).
   - Setze Umgebungsvariable oder CLI-Argument, sodass `FontConfigLoader` diese Datei zuerst findet (z.B. via `SMART_FONT_CONFIG_PATH`).
6. **Font-Registrierung:**
   - Publisher nutzt wie bisher `FontConfigLoader` → `get_font_paths`, bekommt jedoch garantiert existente Dateien.
   - Nach der Registrierung `fc-cache`/`mktexlsr` (je nach Plattform) nur noch ausführen, wenn neue Dateien installiert wurden.

## Plattform-/Umgebungs-spezifische Details
- **Windows:**
  - Favorisierte Cache-Pfade: `%LOCALAPPDATA%\gitbook-worker\fonts`.
  - Optionaler Schritt: Fonts zusätzlich per `Add-FontResourceEx` temporär anmelden, wenn LuaLaTeX sie sonst nicht sieht.
  - TeX Live: Kopie in `%USERPROFILE%\texmf-local\fonts\truetype\gitbook-worker` + `mktexlsr`.
- **macOS:**
  - Cache: `~/Library/Application Support/gitbook-worker/fonts`.
  - Registrierung via `atsutil databases -remove` nur wenn nötig.
- **Linux / Docker:**
  - Cache: `~/.cache/gitbook-worker/fonts` bzw. `/var/cache/gitbook-worker/fonts`.
  - Nach Download `fc-cache -f` ausführen. Im Container können Fonts read-only gemountet werden.

## Integration in gitbook_worker
1. **Neues Modul `smart_font_stack.py`:**
   - Public API: `prepare_fonts(manifest_fonts=None, cache_dir=None) -> Path` (liefert Pfad zur Meta-Datei) und `ensure_font(font_key) -> Path`.
   - Erkennt Laufzeitumgebung (Windows/macOS/Linux/Docker) via `platform` + `cgroup`-Check.
2. **Publisher-Hook:**
   - Vor `_register_font(...)` den Smart-Installer triggern (nur einmal pro Run) und `reset_font_config()` mit `SMART_FONT_CONFIG_PATH` setzen.
3. **CLI-Werkzeug:**
   - `gitbook-worker fonts sync [--lang de --profile local]` um Fonts vorab zu installieren (nützlich für CI und Devs ohne Tests).
4. **Tests:**
   - Unit-Test für Cache-Resolver (mithilfe temporärer Verzeichnisse).
   - Integration-Test in Docker (optional) über GitHub Actions, damit `pytest -m integration` auch remote Fonts zieht.

## Aktueller Stand (Implementiert)
- `gitbook_worker/tools/publishing/smart_font_stack.py` implementiert den Resolver inkl. Download, Cache (`~/.cache/gitbook-worker/fonts` etc.) und der Laufzeit-Datei `fonts.meta.yml`, die automatisch von `publisher.py` konsumiert wird.
- `gitbook_worker/tools/publishing/fonts_cli.py` stellt `python -m gitbook_worker.tools.publishing.fonts_cli sync` bereit, um Fonts unabhängig vom Publisher vorzubereiten.
- Über `setup.cfg` existiert nun der Console-Entry `gitbook-worker-fonts sync …`; zusätzlich kann VS Code via `launch.json` (Config *Fonts: Sync (de manifest)*) denselben Befehl ausführen.
- `FontConfig` versteht neue Felder `version` und `sha256`; Letzteres ermöglicht Hash-Prüfungen nach dem Download.
- Tests (`tests/test_smart_font_stack.py`) decken sowohl den Resolver als auch den CLI-Weg ab.

## Schemaerweiterung für `fonts.yml`
- Jeder Font-Eintrag kann optional `version` (freie Zeichenkette) und `sha256` (Hex-Digest) führen.
- Diese Werte werden in `fonts.meta.yml` durchgereicht und vom Smart-Installer zur Validierung genutzt.
- Beispiel:
  ```yaml
  fonts:
    EMOJI:
      name: "Twemoji Mozilla"
      download_url: "https://github.com/13rac1/twemoji-color-font/.../TwitterColorEmoji-SVGinOT.ttf"
      sha256: "<HEX>"
      version: "15.1.0"
  ```
- Für bestehende Pfad-basierte Fonts (z.B. ERDA CC-BY) sind diese Felder optional, helfen aber bei der Release-Dokumentation.

## Temporäre Meta-Datei
- Speicherort: `tempfile.TemporaryDirectory()` oder `$RUN_DIR/.smart-fonts/fonts.meta.yml`.
- Struktur entspricht exakt `fonts.yml`, ergänzt jedoch `resolved_path` + `cache_state` (z.B. `downloaded`, `system`, `repo`).
- Nach dem Lauf löschen (außer `--persist-font-meta` Flag für Debugging).

## Verbindung zum PyPI-Paket
- Derselbe Smart-Installer gehört später ins `setup.cfg` als optionaler Console-Entry (`gitbook-worker fonts sync`).
- Beim `pip install gitbook-worker` kann ein Post-Install-Hinweis oder optionaler Extras-Tag (`pip install gitbook-worker[fonts]`) bereitgestellt werden, der das Sync-Kommando ausführt.
- Dokumentation (README + docs/multilingual-content-guide) verlinkt auf diesen Prozess, damit Anwender:innen wissen, wie Fonts nachinstalliert werden.

## Offene Fragen & nächste Schritte
1. **Lizenz-Verteilung:** Dürfen alle Fonts automatisiert heruntergeladen werden? Prüfen, ob Redistribution erlaubt ist oder ob wir Nutzer:innen auf externe Quellen verweisen müssen.
2. **Checksum-Verwaltung:** Ergänzung von `sha256` im `fonts.yml`, um Supply-Chain-Sicherheit zu erhöhen.
3. **Plattform-Treiber:** Benötigen wir für Windows/macOS spezielle APIs, um Fonts ohne Admin-Rechte verfügbar zu machen (z.B. `AddFontResourceEx`, CoreText)?
4. **Konfigurierbarkeit:** Soll der Cache-Pfad via Env (`GITBOOK_WORKER_FONT_CACHE`) überschreibbar sein?
5. **Rollback-Strategie:** Wie gehen wir mit kaputten Downloads oder Version-Rolls um? Vorschlag: `CACHE/<font-key>/<hash>` + Atomic Rename.
6. **Monitoring:** Logging + Telemetrie (z.B. wie oft Fonts installiert werden) für spätere DX-Verbesserungen.

Dieses Konzept legt die Grundlage für eine zuverlässige, automatisierbare Font-Bereitstellung, die sowohl lokale Entwickler:innen als auch eine zukünftige PyPI-Distribution unterstützt. Empfehlungen und offene Fragen dienen als Backlog für die kommende Implementierungsphase.
