# Best Practice: Dynamische Docker-Konfiguration für GitBook Worker

## Übersicht

Dieses Dokument beschreibt den Best-Practice-Ansatz für ein **dynamisch konfiguriertes Docker-Image**, das keine hardcodierten Fonts oder Konfigurationen enthält, sondern zur Build-Zeit die aktuelle `gitbook_worker`-Konfiguration auswertet und anwendet.

## Problembeschreibung

### Vorher (Statische Konfiguration)
❌ **Probleme:**
- Fonts hardcodiert im Dockerfile
- Inkonsistenzen zwischen Docker-Image und lokaler Entwicklung
- Bei Änderung der Font-Konfiguration muss Dockerfile manuell angepasst werden
- Keine automatische Validierung der Konfiguration
- License-Compliance nicht automatisch geprüft

```dockerfile
# SCHLECHT: Statisch hardcodiert
RUN wget -O /tmp/twemoji.tar.gz https://github.com/.../twemoji-15.1.0.tar.gz
RUN echo "c8a5302ee4e4c2188ce785edd84c50c616a07f6e99fe1b91aecba4e1db341295" | sha256sum -c -
COPY .github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf /usr/share/fonts/...
```

### Nachher (Dynamische Konfiguration)
✅ **Vorteile:**
- Konfiguration aus `fonts.yml` ausgelesen
- Docker-Image immer konsistent mit gitbook_worker Setup
- Automatische License-Compliance-Prüfung
- Integrierte Integritätstests
- Single Source of Truth: `fonts.yml`

```dockerfile
# GUT: Dynamisch konfiguriert
COPY .github/gitbook_worker/defaults/ /tmp/gitbook_worker_setup/defaults/
COPY .github/gitbook_worker/tools/ /tmp/gitbook_worker_setup/tools/
COPY .github/fonts/ /tmp/gitbook_worker_setup/fonts/

RUN python3 -m tools.docker.setup_docker_environment \
    --mode install --config /tmp/gitbook_worker_setup/defaults/fonts.yml
```

## Architektur

### Komponenten

```
┌─────────────────────────────────────────────────────────────────┐
│                         Dockerfile.dynamic                       │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 1. System Dependencies Installation                     │    │
│  │    - pandoc, texlive, python3, fontconfig, etc.        │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 2. Copy Configuration Files                             │    │
│  │    - defaults/fonts.yml                                 │    │
│  │    - tools/docker/setup_docker_environment.py          │    │
│  │    - .github/fonts/                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 3. Dynamic Font Installation                            │    │
│  │    setup_docker_environment.py --mode install          │    │
│  │                                                         │    │
│  │    ├─ Load fonts.yml                                   │    │
│  │    ├─ Verify License Compliance (AGENTS.md)            │    │
│  │    ├─ Install Fonts to /usr/share/fonts/              │    │
│  │    ├─ Update Font Cache (fc-cache)                    │    │
│  │    └─ Generate Installation Manifest                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 4. Environment Validation                               │    │
│  │    setup_docker_environment.py --mode validate         │    │
│  │                                                         │    │
│  │    ├─ Verify Font Files & Checksums                   │    │
│  │    ├─ Check Font Cache (fc-list)                      │    │
│  │    ├─ Test Required Tools (pandoc, xelatex, etc.)     │    │
│  │    ├─ Verify Python Packages                          │    │
│  │    └─ Generate Validation Report                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 5. Build Artifacts Preservation                         │    │
│  │    /opt/gitbook_worker/reports/                        │    │
│  │    ├─ docker_font_installation.json                    │    │
│  │    └─ docker_validation_report.json                    │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Dateifluss

```
fonts.yml (Configuration)
    │
    ├─> FontConfigLoader
    │       │
    │       └─> Parse & Validate
    │               │
    │               └─> FontConfig Objects
    │                       │
    │                       ├─> License Compliance Check
    │                       │       (AGENTS.md Enforcement)
    │                       │
    │                       └─> DockerFontInstaller
    │                               │
    │                               ├─> Copy Fonts to Docker Image
    │                               ├─> Update Font Cache (fc-cache)
    │                               └─> Generate Manifest
    │
    └─> DockerEnvironmentValidator
            │
            ├─> Verify Font Files (Checksums)
            ├─> Check Font Cache (fc-list)
            ├─> Test Tools (pandoc, xelatex, etc.)
            └─> Generate Validation Report
```

## Implementation

### 1. Setup-Modul: `setup_docker_environment.py`

**Hauptfunktionen:**

#### A. Font Installation (`DockerFontInstaller`)

```python
class DockerFontInstaller:
    """Installs fonts into Docker image according to gitbook_worker configuration."""
    
    def check_license_compliance(self) -> None:
        """Verify all fonts have compatible licenses (AGENTS.md compliance)."""
        # Prüft: CC BY 4.0, MIT, SIL OFL 1.1
        # Blockiert: OFL, Apache, GPL, UFL, proprietary
    
    def install_font(self, key: str, font: FontConfig) -> bool:
        """Install a single font into Docker image."""
        # Kopiert Fonts nach /usr/share/fonts/truetype/gitbook_worker/
        # Berechnet SHA256 Checksums
        # Protokolliert Installation
    
    def update_font_cache(self) -> None:
        """Update system font cache after installation."""
        # Führt fc-cache -f -v aus
    
    def generate_manifest(self, output_path: Path) -> None:
        """Generate installation manifest for verification."""
        # Erstellt JSON mit allen installierten Fonts + Checksums
```

**Ausgabe-Manifest (`docker_font_installation.json`):**
```json
{
  "version": "1.0.0",
  "config_source": "/tmp/gitbook_worker_setup/defaults/fonts.yml",
  "config_version": "1.0.0",
  "installed_fonts": [
    {
      "key": "CJK",
      "name": "ERDA CC-BY CJK",
      "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
      "license_url": "https://creativecommons.org/licenses/by/4.0/",
      "files": [
        {
          "source": ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf",
          "target": "/usr/share/fonts/truetype/gitbook_worker/cjk/erda-ccby-cjk.ttf",
          "size": 15728640,
          "sha256": "a1b2c3d4e5f6..."
        }
      ]
    }
  ]
}
```

#### B. Environment Validation (`DockerEnvironmentValidator`)

```python
class DockerEnvironmentValidator:
    """Validates Docker image setup and configuration."""
    
    def validate_fonts(self, manifest_path: Path) -> bool:
        """Validate installed fonts against manifest."""
        # Prüft Existenz aller Font-Dateien
        # Verifiziert SHA256 Checksums
        # Überprüft Font-Cache (fc-list)
    
    def validate_required_tools(self) -> bool:
        """Validate required system tools are installed."""
        # Testet: python3, pandoc, xelatex, lualatex, fc-cache, git
    
    def validate_python_packages(self) -> bool:
        """Validate required Python packages are installed."""
        # Testet: yaml, pytest, pathvalidate, markdown, bs4, pypandoc
    
    def generate_report(self, output_path: Path) -> None:
        """Generate validation report."""
        # Erstellt JSON mit PASS/FAIL Status + Fehler/Warnungen
```

**Ausgabe-Report (`docker_validation_report.json`):**
```json
{
  "version": "1.0.0",
  "status": "PASS",
  "errors": [],
  "warnings": [],
  "error_count": 0,
  "warning_count": 0
}
```

### 2. Dockerfile Integration

```dockerfile
# --- Dynamic Font Configuration ---
# Copy necessary configuration files
COPY .github/gitbook_worker/defaults/ /tmp/gitbook_worker_setup/defaults/
COPY .github/gitbook_worker/tools/ /tmp/gitbook_worker_setup/tools/
COPY .github/fonts/ /tmp/gitbook_worker_setup/fonts/
COPY publish.yml /tmp/gitbook_worker_setup/

# Set Python path
ENV PYTHONPATH=/tmp/gitbook_worker_setup

# Install fonts dynamically
RUN cd /tmp/gitbook_worker_setup && \
    python3 -m tools.docker.setup_docker_environment \
        --mode install \
        --config /tmp/gitbook_worker_setup/defaults/fonts.yml \
        --manifest /tmp/docker_font_installation.json \
        --verbose

# Validate environment
RUN cd /tmp/gitbook_worker_setup && \
    python3 -m tools.docker.setup_docker_environment \
        --mode validate \
        --manifest /tmp/docker_font_installation.json \
        --report /tmp/docker_validation_report.json \
        --verbose

# Preserve build artifacts
RUN mkdir -p /opt/gitbook_worker/reports && \
    mv /tmp/docker_font_installation.json /opt/gitbook_worker/reports/ && \
    mv /tmp/docker_validation_report.json /opt/gitbook_worker/reports/
```

## License Compliance (AGENTS.md)

### Erlaubte Lizenzen
✅ **Automatisch akzeptiert:**
- `CC BY 4.0` (Creative Commons Attribution 4.0 International)
- `MIT`
- `SIL Open Font License 1.1`

### Verbotene Lizenzen
❌ **Build wird abgebrochen:**
- `OFL` (falsche Abkürzung, sollte "SIL Open Font License 1.1" sein)
- `Apache` / `Apache-2.0`
- `GPL` / `AGPL` / `LGPL`
- `UFL`
- `proprietary`

### Prüfmechanismus

```python
def check_license_compliance(self) -> None:
    """Verify all fonts have compatible licenses (AGENTS.md compliance)."""
    violations = []
    
    for font in all_fonts:
        if font.license in FORBIDDEN_LICENSES:
            violations.append(f"Font '{font.name}': Forbidden license '{font.license}'")
    
    if violations:
        raise LicenseViolationError(violations)
```

**Bei Verstoß:**
```
ERROR: LICENSE COMPLIANCE VIOLATION
======================================================================
Font 'Bad Font' (CUSTOM): Forbidden license 'proprietary'

Allowed licenses: CC BY 4.0, MIT, SIL Open Font License 1.1
Forbidden licenses: OFL, Apache, GPL, UFL, proprietary
======================================================================
Build aborted due to license policy violation (AGENTS.md).
Exit Code: 2
```

## Integritätstests

### Font File Integrity
✅ **SHA256 Checksums:**
- Jede Font-Datei wird beim Install gehasht
- Bei Validation werden Checksums verglichen
- Erkennt manipulierte oder korrupte Dateien

```python
def _calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()
```

### Font Cache Integrity
✅ **fc-list Verification:**
- Prüft, ob installierte Fonts im System-Cache sind
- Warnung bei fehlenden Cache-Einträgen

```python
def _validate_font_cache(self, manifest: Dict) -> None:
    """Verify fonts are in system font cache."""
    result = subprocess.run(["fc-list", ":", "family", "file"], capture_output=True)
    
    for font in installed_fonts:
        if font.name.lower() not in result.stdout.lower():
            self.warnings.append(f"Font '{font.name}' not found in font cache")
```

### Tool Availability
✅ **Required Tools Check:**
```python
required_tools = {
    "python3": "--version",
    "pandoc": "--version",
    "xelatex": "--version",
    "lualatex": "--version",
    "fc-cache": "--version",
    "fc-list": "--version",
    "git": "--version",
}
```

### Python Package Availability
✅ **Import Test:**
```python
required_packages = [
    "yaml",
    "pytest",
    "pathvalidate",
    "markdown",
    "bs4",
    "pypandoc",
]

for package in required_packages:
    __import__(package)  # Raises ImportError if missing
```

## Vorteile des Ansatzes

### 1. Single Source of Truth
- `fonts.yml` definiert alle Fonts
- Keine Duplikation im Dockerfile
- Änderungen an einem Ort

### 2. Automatische Konsistenz
- Docker-Image immer synchron mit lokaler Config
- Kein manuelles Update des Dockerfiles nötig

### 3. License Compliance
- Automatische Prüfung bei jedem Build
- Verhindert versehentliche Lizenzversletzungen
- AGENTS.md-konform

### 4. Qualitätssicherung
- Integrität aller Fonts geprüft (Checksums)
- Tool-Verfügbarkeit validiert
- Python-Packages getestet
- Build-Artefakte dokumentiert

### 5. Wartbarkeit
- Neue Fonts: nur `fonts.yml` ändern
- Font-Update: nur `fonts.yml` ändern
- Lizenzänderung: nur `ALLOWED_LICENSES` anpassen

### 6. Transparenz
- Installation Manifest zeigt alle installierten Fonts
- Validation Report dokumentiert Prüfergebnisse
- Einsehbar via `docker run --rm IMAGE --info`

## Verwendung

### Build

```bash
# Neues Image mit dynamischer Konfiguration bauen
docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic \
             -t erda-workflow-tools:latest .
```

### Informationen anzeigen

```bash
# Build-Informationen und Validation-Report anzeigen
docker run --rm erda-workflow-tools:latest --info
```

**Ausgabe:**
```
=============================================================
ERDA GitBook Worker Docker Image
=============================================================
Built with dynamic configuration from gitbook_worker

Configuration:
{
  "version": "1.0.0",
  "installed_fonts": [...]
}

Validation:
{
  "status": "PASS",
  "errors": [],
  "warnings": []
}
=============================================================
```

### Tests ausführen

```bash
docker run --rm -v $(pwd):/workspace erda-workflow-tools:latest \
    python3 -m pytest .github/gitbook_worker/tests -v
```

### Orchestrator ausführen

```bash
docker run --rm -v $(pwd):/workspace erda-workflow-tools:latest \
    python3 -m tools.workflow_orchestrator \
    --root /workspace \
    --manifest publish.yml \
    --profile local
```

## Migration vom alten Dockerfile

### Schritt 1: Fonts aus Dockerfile entfernen

❌ **Entfernen:**
```dockerfile
# ALT: Hardcodiert
RUN wget -O /tmp/twemoji.tar.gz https://github.com/.../twemoji.tar.gz
RUN echo "abc123..." | sha256sum -c -
RUN tar -xzf /tmp/twemoji.tar.gz ...
COPY .github/fonts/erda-ccby-cjk/... /usr/share/fonts/...
RUN fc-cache -f -v
```

### Schritt 2: Dynamisches Setup hinzufügen

✅ **Hinzufügen:**
```dockerfile
# NEU: Dynamisch
COPY .github/gitbook_worker/defaults/ /tmp/gitbook_worker_setup/defaults/
COPY .github/gitbook_worker/tools/ /tmp/gitbook_worker_setup/tools/
COPY .github/fonts/ /tmp/gitbook_worker_setup/fonts/

RUN python3 -m tools.docker.setup_docker_environment --mode both
```

### Schritt 3: Testen

```bash
# Image bauen
docker build -f Dockerfile.dynamic -t test:latest .

# Validierung prüfen
docker run --rm test:latest --info

# Tests ausführen
docker run --rm -v $(pwd):/workspace test:latest \
    python3 -m pytest .github/gitbook_worker/tests -v
```

## Fehlerbehandlung

### Build schlägt fehl: License Violation

**Problem:**
```
ERROR: LICENSE COMPLIANCE VIOLATION
Font 'MyFont': Forbidden license 'GPL'
```

**Lösung:**
1. Font in `fonts.yml` entfernen oder
2. Font mit kompatibler Lizenz ersetzen oder
3. Lizenz in `ALLOWED_LICENSES` hinzufügen (nur wenn AGENTS.md-konform!)

### Build schlägt fehl: Font nicht gefunden

**Problem:**
```
ERROR: Font file not found: .github/fonts/missing.ttf
```

**Lösung:**
1. Font-Datei in `.github/fonts/` ablegen oder
2. Pfad in `fonts.yml` korrigieren oder
3. Font als System-Font deklarieren: `paths: []`

### Validation schlägt fehl: Checksum Mismatch

**Problem:**
```
ERROR: Checksum mismatch for font.ttf: expected abc123..., got def456...
```

**Lösung:**
1. Font-Datei auf Integrität prüfen
2. Bei Absicht: Manifest neu generieren mit `--mode install`

### Font nicht im Cache

**Problem:**
```
WARNING: Font 'MyFont' not found in font cache
```

**Lösung:**
1. Meist harmlos (Font wird trotzdem gefunden)
2. Prüfen mit: `docker run IMAGE fc-list | grep MyFont`
3. Bei Bedarf: `fc-cache -f -v` manuell ausführen

## Erweiterungen

### Zusätzliche Validierungen

```python
def validate_latex_configuration(self) -> bool:
    """Validate LaTeX can use installed fonts."""
    # Test: xelatex kann Fonts verwenden
    test_doc = r"\documentclass{article}\usepackage{fontspec}\setmainfont{ERDA CC-BY CJK}\begin{document}Test\end{document}"
    # Kompiliere Testdokument...
```

### Manifest-Erweiterung

```python
manifest = {
    "version": "1.0.0",
    "build_timestamp": datetime.now().isoformat(),
    "builder_version": "1.2.3",
    "compliance_check": {
        "agents_md": "passed",
        "dco": "required",
    },
    # ... existing fields
}
```

### CI/CD Integration

```yaml
# .github/workflows/docker-build.yml
- name: Build Docker Image
  run: docker build -f Dockerfile.dynamic -t $IMAGE_TAG .

- name: Validate Build
  run: |
    docker run --rm $IMAGE_TAG --info > build_info.json
    
    # Parse JSON und prüfe status == "PASS"
    python3 -c "
    import json
    with open('build_info.json') as f:
        # Parse validation section
        # Assert status == 'PASS'
    "

- name: Extract Build Artifacts
  run: |
    docker run --rm $IMAGE_TAG cat /opt/gitbook_worker/reports/docker_validation_report.json \
      > validation_report.json
    
    # Artifact hochladen für Audit
```

## Compliance-Checkliste

- [x] ✅ Keine hardcodierten Fonts im Dockerfile
- [x] ✅ Konfiguration aus `fonts.yml` geladen
- [x] ✅ License Compliance automatisch geprüft (AGENTS.md)
- [x] ✅ Font-Integrität validiert (SHA256)
- [x] ✅ Font-Cache geprüft (fc-list)
- [x] ✅ Tool-Verfügbarkeit getestet
- [x] ✅ Python-Packages validiert
- [x] ✅ Build-Artefakte dokumentiert
- [x] ✅ Validation-Report generiert
- [x] ✅ Exit-Codes für CI/CD (0=OK, 1=Error, 2=License)

## Zusammenfassung

Dieser Best-Practice-Ansatz transformiert das Docker-Image von einem **statisch konfigurierten** zu einem **dynamisch konfigurierten** System:

1. **Konfiguration**: `fonts.yml` ist Single Source of Truth
2. **Installation**: Python-Modul installiert Fonts automatisch
3. **Validierung**: Integrität und Compliance automatisch geprüft
4. **Transparenz**: Manifeste und Reports dokumentieren Build
5. **Wartbarkeit**: Änderungen nur an einem Ort nötig

Das Ergebnis ist ein **"Out-of-the-Box Ready"** Docker-Image, das:
- ✅ Immer mit gitbook_worker-Konfiguration synchron ist
- ✅ AGENTS.md-konform (License Compliance)
- ✅ Qualitätsgesichert (automatische Tests)
- ✅ Wartbar (keine Duplikation)
- ✅ Transparent (dokumentierte Build-Artefakte)

---

**Signed-off-by:** ERDA GitBook Worker Team <team@erda-project.org>
