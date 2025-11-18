# GitBook Worker Package

Ein wiederverwendbares Package zur automatisierten PDF-Generierung aus GitBook-Markdown-Projekten.

## Design-Philosophie

**GitBook Worker ist als eigenständiges, übertragbares Package konzipiert**, das in jedes Repository eingefügt werden kann, um automatisch hochwertige PDF-Dokumentationen zu erstellen.

### Kern-Prinzip: Vollständige Selbstständigkeit

Alle Komponenten, die zum Betrieb des GitBook Workers benötigt werden, befinden sich **innerhalb des `.github/gitbook_worker` Ordners**:

- ✅ **Dokumentation** (`docs/`) - Anleitungen, Best Practices, Strategien
- ✅ **Beispiele** (`examples/`, falls vorhanden) - Konfigurationsbeispiele
- ✅ **Skripte** (`scripts/`) - Wrapper-Skripte, Helper-Tools
- ✅ **Module** (`tools/`) - Python-Module und CLI-Tools
- ✅ **Tests** (`tests/`) - Unit-Tests für alle Komponenten
- ✅ **Defaults** (`defaults/`) - Standard-Konfigurationen
- ✅ **Workflow-Vorlagen** (geplant: `workflows/`) - GitHub Actions Templates

### Vorteile dieser Struktur

1. **Portabilität**: Einfaches Kopieren des kompletten `.github/gitbook_worker` Ordners in ein neues Projekt
2. **Isolation**: Keine Abhängigkeiten zu projektspezifischen Dateien außerhalb des Ordners
3. **Versionierung**: Das gesamte Package kann als Einheit versioniert werden
4. **Anpassbarkeit**: Anwender können das Package nach ihren Bedürfnissen feinjustieren
5. **Wartbarkeit**: Alle Komponenten sind an einem zentralen Ort

## Verwendung

### Installation in einem neuen Projekt

1. **Kopieren Sie den kompletten Ordner** in Ihr Repository:
   ```bash
   # Von einem bestehenden Projekt
   cp -r /pfad/zum/erda-book/.github/gitbook_worker /ihr/projekt/.github/
   ```

2. **Passen Sie die Konfiguration an** Ihre Bedürfnisse an:
   - Editieren Sie `defaults/docker_config.yml` für Docker-Namen
   - Erstellen Sie `docker_config.yml` im Repo-Root für Überschreibungen
   - Konfigurieren Sie `publish.yml` im Repo-Root mit Ihren Büchern

3. **Nutzen Sie die bereitgestellten Tools**:
   ```bash
   # Docker-Namen abrufen
   ./.github/gitbook_worker/scripts/docker-names.ps1 get-all-names \
     --context prod --publish-name my-book
   
   # PDF generieren (mit den bereitgestellten Tools)
   python ./.github/gitbook_worker/tools/publishing/pdf_builder.py
   ```

### Anpassung an Projekt-Bedürfnisse

Nach dem Kopieren können Sie **alle Komponenten feinjustieren**:

- **Dokumentation**: Ergänzen Sie projekt-spezifische Hinweise in `docs/`
- **Skripte**: Passen Sie Wrapper-Skripte an Ihre CI/CD-Pipeline an
- **Module**: Erweitern Sie die Python-Module mit projekt-spezifischer Logik
- **Defaults**: Ändern Sie Standard-Konfigurationen nach Bedarf

## Struktur

```
.github/gitbook_worker/
├── README.md                    # Diese Datei - Design & Verwendung
├── defaults/                    # Standard-Konfigurationen
│   └── docker_config.yml        # Docker-Naming-Defaults
├── docs/                        # Dokumentation
│   ├── docker/                  # Docker-spezifische Dokumentation
│   │   ├── README.md            # Docker-Dokumentations-Index
│   │   ├── DOCKERFILE_STRATEGY.md   # Docker-Image-Strategie
│   │   ├── LOGGING_STRATEGY.md      # Docker-Logging-Architektur
│   │   ├── DEBUGGING.md             # Docker-Debugging-Guide
│   │   └── IMPLEMENTATION_SUMMARY.md # Implementierungs-Zusammenfassung
│   ├── docker-names-*.md        # Docker-Naming-System
│   └── ...                      # Weitere Dokumentation
├── scripts/                     # Ausführbare Skripte
│   ├── docker-names.ps1         # Docker-Namen CLI (PowerShell)
│   └── docker-names.sh          # Docker-Namen CLI (Bash)
├── tests/                       # Unit-Tests
│   ├── conftest.py              # Pytest-Konfiguration
│   ├── test_smart_merge.py      # Tests für Docker-Naming
│   └── ...                      # Weitere Tests
├── tools/                       # Python-Module
│   ├── __init__.py              # Package-Definition
│   ├── docker/                  # Docker-Tools
│   │   ├── __init__.py
│   │   ├── smart_merge.py       # Konfigurationsmerge
│   │   └── cli.py               # Command-Line Interface
│   ├── publishing/              # Publishing-Tools
│   │   └── ...
│   └── utils/                   # Hilfs-Utilities
│       └── ...
└── workflows/                   # (Geplant) GitHub Actions Templates
    └── build-pdf.yml.template
```

## Komponenten

### Docker-Naming-System

Konfigurierbares, mehrschichtiges YAML-basiertes System für Docker-Image- und Container-Namen:

- **Python API**: `from gitbook_worker.tools.docker import smart_merge`
- **CLI**: `python -m gitbook_worker.tools.docker.cli`
- **Wrapper**: `.github/gitbook_worker/scripts/docker-names.{ps1,sh}`

Dokumentation:
- [docker-names-README.md](docs/docker-names-README.md) - API/CLI-Referenz
- [docker-names-INTEGRATION.md](docs/docker-names-INTEGRATION.md) - Integrationsbeispiele
- [docker-names-MIGRATION.md](docs/docker-names-MIGRATION.md) - Migrationsleitfaden

### Docker-Image-Strategie

Mehrere Dockerfile-Varianten für verschiedene Anwendungsfälle:

- **Dockerfile.dynamic** - Smart configuration aus fonts.yml (empfohlen)
- **Dockerfile.python** - Leichtgewichtig für Tests (~5 min Build, ~300 MB)
- **Dockerfile** - Legacy (deprecated)

Dokumentation: [docs/docker/DOCKERFILE_STRATEGY.md](docs/docker/DOCKERFILE_STRATEGY.md)

### Docker-Logging & Diagnostik

Externes Log-Volume und Diagnostik-Tools für Docker-basierte Orchestrator-Läufe:

- **Externes Log-Volume** - Logs persistieren in `.docker-logs/` außerhalb des Containers
- **Diagnostik-Tool** - File-State-Tracking zur Identifizierung von Git-Status-Änderungen
- **Automated Wrapper** - `diagnose-docker.ps1` für vollautomatische Analyse

Dokumentation: [docs/docker/](docs/docker/) (Index)
- [LOGGING_STRATEGY.md](docs/docker/LOGGING_STRATEGY.md) - Architektur und Strategie
- [DEBUGGING.md](docs/docker/DEBUGGING.md) - Anwendungsguide und Troubleshooting
- [IMPLEMENTATION_SUMMARY.md](docs/docker/IMPLEMENTATION_SUMMARY.md) - Implementierungsdetails

### Publishing-Tools

Python-Module zur PDF-Generierung aus GitBook-Markdown:

- Font-Management und Emoji-Unterstützung
- PDF-Rendering mit Calibre
- Konfigurierbare Styling-Optionen

Dokumentation: Siehe `tools/publishing/` und `docs/`

## Entwicklung

### Tests ausführen

```bash
# Alle Tests
pytest .github/gitbook_worker/tests -v

# Spezifische Tests
pytest .github/gitbook_worker/tests/test_smart_merge.py -v

# Mit Coverage
pytest .github/gitbook_worker/tests --cov=gitbook_worker
```

### Module verwenden

Setzen Sie `PYTHONPATH` auf `.github`:

```python
# In Ihrem Code
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".github"))

from gitbook_worker.tools.docker import smart_merge
```

Oder verwenden Sie die bereitgestellten Wrapper-Skripte, die `PYTHONPATH` automatisch setzen.

## Anforderungen

### System-Anforderungen

- Python 3.8+
- Docker (für Container-basierte PDF-Generierung)
- Git (für Versionskontrolle)

### Python-Abhängigkeiten

```bash
# Im Projekt-Root
pip install -r requirements.txt

# Oder nur für GitBook Worker
pip install pyyaml  # Für YAML-Konfiguration
```

## Lizenz

Dieses Package folgt der Lizenzierung des ERDA-Projekts:

- **Code/Skripte/Module**: MIT License
- **Dokumentation**: CC BY-SA 4.0

Details siehe `LICENSE-CODE` und `LICENSE` im Repository-Root.

## Beiträge

Bei Verbesserungen oder Erweiterungen des GitBook Workers:

1. Stellen Sie sicher, dass **alle Komponenten innerhalb `.github/gitbook_worker/` bleiben**
2. Aktualisieren Sie diese README.md bei strukturellen Änderungen
3. Fügen Sie Tests für neue Funktionen hinzu
4. Dokumentieren Sie Änderungen in den entsprechenden `docs/` Dateien
5. Signieren Sie Ihre Commits mit `Signed-off-by:` (DCO)

## Support & Dokumentation

- **Design-Entscheidungen**: Diese README.md
- **Docker-Dokumentation**: `docs/docker/` (kompletter Index mit allen Docker-Themen)
- **Docker-Naming**: `docs/docker-names-*.md`
- **API-Referenz**: Docstrings in `tools/**/*.py`
- **Beispiele**: Siehe `docs/*-INTEGRATION.md`

## Versions-Historie

- **v1.0.0** (November 2025) - Initiale Version mit Docker-Naming-System
  - Smart Merge Konfiguration
  - Multi-Layer YAML-Merge
  - CLI und Python API
  - Vollständige Dokumentation

---

**Entwickelt für**: ERDA Book Project  
**Maintainer**: ERDA GitBook Worker Team  
**Status**: Produktiv
