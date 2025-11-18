# ERDA GitBook Worker - Dockerfile Strategy & Best Practices

## Executive Summary

**Empfehlung:** Behalte **nur `Dockerfile.dynamic`** und `Dockerfile.python` (als lightweight Test-Image).

**Status:** 
- ✅ **`Dockerfile.dynamic`** → **BEHALTEN** (Best Practice, Production-Ready)
- ⚠️ **`Dockerfile`** → **DEPRECATE & ENTFERNEN** (Legacy, hardcodiert)
- ✅ **`Dockerfile.python`** → **BEHALTEN** (Lightweight für reine Python-Tests)

---

## 1. Analyse der vorhandenen Dockerfiles

### 1.1 `Dockerfile.dynamic` ⭐ (Best Practice)

**Status:** ✅ **PRODUCTION-READY - BEHALTEN**

**Charakteristiken:**
- **Smart Configuration:** Liest `fonts.yml` zur Build-Zeit
- **Automatische Validierung:** Fonts, Tools, Packages
- **License Compliance:** Automatische Prüfung gegen AGENTS.md
- **Dokumentation:** Build-Artefakte in `/opt/gitbook_worker/reports/`
- **Integrität:** SHA256-Checksums für alle Fonts
- **Transparency:** `--info` Kommando zeigt Build-Details

**Technische Merkmale:**
```dockerfile
# Dynamisches Setup
COPY .github/gitbook_worker/defaults/ /tmp/setup/defaults/
COPY .github/gitbook_worker/tools/ /tmp/setup/tools/
COPY .github/fonts/ /tmp/setup/fonts/

RUN python3 -m tools.docker.setup_docker_environment \
    --mode install --config defaults/fonts.yml

RUN python3 -m tools.docker.setup_docker_environment \
    --mode validate --report validation.json
```

**Vorteile:**
- ✅ **Single Source of Truth:** `fonts.yml` ist einzige Konfigurationsquelle
- ✅ **Konsistenz:** Docker-Image immer synchron mit lokaler Config
- ✅ **Wartbarkeit:** Keine Font-Duplikation im Dockerfile
- ✅ **Compliance:** AGENTS.md-konforme License-Prüfung
- ✅ **Qualität:** Automatische Integritätstests
- ✅ **Auditierbarkeit:** Build-Manifeste dokumentieren Installation

**Docker Tag:** `erda-smart-worker:latest`

---

### 1.2 `Dockerfile` (Legacy)

**Status:** ⚠️ **DEPRECATED - ENTFERNEN**

**Charakteristiken:**
- **Statische Konfiguration:** Fonts hardcodiert im Dockerfile
- **Manuelle Wartung:** Bei Font-Änderungen muss Dockerfile angepasst werden
- **Keine Validierung:** Keine automatischen Integritätstests
- **Inkonsistenz-Risiko:** Kann von `fonts.yml` abweichen
- **Duplikation:** Font-URLs und Checksums doppelt gepflegt

**Problematische Code-Stellen:**
```dockerfile
# PROBLEM: Hardcodiert
RUN wget -O /tmp/twemoji-linux.tar.gz \
    https://github.com/.../TwitterColorEmoji-SVGinOT-Linux-15.1.0.tar.gz && \
    echo "c8a5302ee4e4c2188ce785edd84c50c616a07f6e99fe1b91aecba4e1db341295" | sha256sum -c -

# PROBLEM: Manuell kopiert
COPY .github/gitbook_worker/tools/publishing/texmf/ /app/texmf
```

**Nachteile:**
- ❌ **Wartungsaufwand:** Jede Font-Änderung braucht Dockerfile-Update
- ❌ **Fehleranfällig:** Vergessene Updates führen zu Inkonsistenzen
- ❌ **Keine Compliance-Checks:** Lizenz-Verstöße nicht automatisch erkannt
- ❌ **Keine Dokumentation:** Keine Build-Artefakte oder Reports
- ❌ **Duplikation:** Font-Informationen in `fonts.yml` UND Dockerfile

**Docker Tag:** `erda-workflow-tools:latest` (deprecated)

---

### 1.3 `Dockerfile.python`

**Status:** ✅ **LIGHTWEIGHT TEST IMAGE - BEHALTEN**

**Charakteristiken:**
- **Minimalistisch:** Nur Python 3.12 + pytest + git
- **Schnell:** Klein, schneller Build (~2 Minuten vs. ~15 Minuten)
- **Zweck:** Reine Python-Unit-Tests ohne LaTeX/Pandoc
- **Use Case:** Schnelle CI-Tests, Entwickler-Workflow

**Code:**
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && apt-get clean
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip3 install --no-cache-dir pytest pytest-cov black

WORKDIR /workspace
```

**Vorteile:**
- ✅ **Schnell:** Build in <5 Minuten
- ✅ **Leichtgewichtig:** ~300 MB vs. ~4 GB
- ✅ **Fokussiert:** Nur für Python-Tests
- ✅ **CI-Optimiert:** Schnelle Feedback-Loops

**Use Cases:**
1. **Unit-Tests:** Python-Code-Tests ohne Publishing
2. **Pre-Commit:** Schnelle Validierung vor Push
3. **Entwickler-Workflow:** Lokale Tests ohne LaTeX-Installation
4. **CI Pipeline:** Erste Test-Phase (schnell)

**Docker Tag:** `erda-python-test:latest`

---

## 2. Best Practice Empfehlung

### 2.1 Strategie: Zwei-Image-Ansatz

```
┌─────────────────────────────────────────────────────────────────┐
│                         ERDA Docker Strategy                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐   ┌──────────────────────────────┐
│  Dockerfile.python           │   │  Dockerfile.dynamic          │
│  (Lightweight Test)          │   │  (Smart Full Stack)          │
├──────────────────────────────┤   ├──────────────────────────────┤
│ • Python 3.12                │   │ • Ubuntu 22.04               │
│ • pytest, black              │   │ • Python + LaTeX + Pandoc    │
│ • git                        │   │ • Dynamische Font-Config     │
│ • ~300 MB                    │   │ • Automatische Validierung   │
│ • Build: ~5 min              │   │ • License Compliance         │
│                              │   │ • ~4 GB                      │
│ Use Case:                    │   │ • Build: ~15 min             │
│ ✅ Unit-Tests                │   │                              │
│ ✅ Code-Qualität (black)     │   │ Use Case:                    │
│ ✅ Pre-Commit Checks         │   │ ✅ PDF-Publishing            │
│ ✅ CI Fast Feedback          │   │ ✅ Full Integration Tests    │
│                              │   │ ✅ Production Builds         │
│ Tag:                         │   │ ✅ GitHub Actions CI/CD      │
│ erda-python-test:latest      │   │                              │
└──────────────────────────────┘   │ Tag:                         │
                                    │ erda-smart-worker:latest     │
                                    └──────────────────────────────┘

                  ┌──────────────────────────────┐
                  │  Dockerfile (Legacy)         │
                  │  ❌ DEPRECATED - ENTFERNEN   │
                  └──────────────────────────────┘
```

### 2.2 Entscheidungsmatrix

| Kriterium | Dockerfile.python | Dockerfile.dynamic | Dockerfile (Legacy) |
|-----------|-------------------|--------------------|--------------------|
| **Build-Zeit** | ⚡ ~5 min | 🐌 ~15 min | 🐌 ~15 min |
| **Image-Größe** | 📦 ~300 MB | 📦 ~4 GB | 📦 ~4 GB |
| **Use Case** | Unit-Tests | Full Publishing | ❌ Obsolet |
| **Konfiguration** | Statisch (minimal) | ✅ Dynamisch | ❌ Statisch |
| **Validierung** | Keine | ✅ Automatisch | ❌ Keine |
| **License Check** | N/A | ✅ Ja | ❌ Nein |
| **Wartbarkeit** | ✅ Einfach | ✅ Einfach | ❌ Komplex |
| **Dokumentation** | ✅ Klar | ✅ Exzellent | ❌ Fehlt |
| **AGENTS.md Konform** | ✅ Ja | ✅ Ja | ⚠️ Unklar |
| **Empfehlung** | ✅ BEHALTEN | ✅ BEHALTEN | ❌ ENTFERNEN |

---

## 3. Migrations-Plan: Dockerfile entfernen

### Phase 1: Deprecation Warning (Sofort)

**Datei:** `Dockerfile` (Header hinzufügen)

```dockerfile
# =============================================================================
# ⚠️  DEPRECATED - DO NOT USE
# =============================================================================
# This Dockerfile is deprecated and will be removed in future versions.
# 
# Please use instead:
#   - Dockerfile.dynamic (for full publishing)
#   - Dockerfile.python (for lightweight tests)
#
# Migration Guide: See DOCKERFILE_STRATEGY.md
# =============================================================================

# ... existing content ...
```

### Phase 2: Dokumentation Update (Sofort)

**Dateien aktualisieren:**

1. **`README.md`** - Deprecation-Warnung
   ```markdown
   ## ⚠️ Deprecation Notice
   
   `Dockerfile` is deprecated. Use:
   - ✅ `Dockerfile.dynamic` (recommended, smart configuration)
   - ✅ `Dockerfile.python` (lightweight tests)
   ```

2. **`run_docker.py`** - Default auf `--use-dynamic` ändern
   ```python
   parser.add_argument(
       "--use-dynamic",
       action="store_true",
       default=True,  # CHANGED: Default ist jetzt dynamic
       help="Use Dockerfile.dynamic (recommended, default)"
   )
   
   parser.add_argument(
       "--use-legacy",
       action="store_true",
       help="Use legacy Dockerfile (deprecated, will be removed)"
   )
   ```

### Phase 3: CI/CD Migration (1 Woche)

**GitHub Actions aktualisieren:**

```yaml
# .github/workflows/docker-build.yml
jobs:
  test-fast:
    name: Fast Python Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Python Test Image
        run: docker build -f .github/gitbook_worker/tools/docker/Dockerfile.python -t test:latest .
      - name: Run Unit Tests
        run: docker run --rm -v $(pwd):/workspace test:latest pytest tests/

  test-full:
    name: Full Integration Tests
    runs-on: ubuntu-latest
    needs: test-fast
    steps:
      - uses: actions/checkout@v3
      - name: Build Smart Worker Image
        run: docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic -t worker:latest .
      - name: Run Integration Tests
        run: docker run --rm -v $(pwd):/workspace worker:latest pytest tests/ -v

  publish:
    name: Publish PDF
    runs-on: ubuntu-latest
    needs: test-full
    steps:
      - uses: actions/checkout@v3
      - name: Build Smart Worker Image
        run: docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic -t worker:latest .
      - name: Run Publishing
        run: docker run --rm -v $(pwd):/workspace worker:latest python3 -m tools.workflow_orchestrator
```

### Phase 4: Entfernung (2 Wochen)

**Schritte:**
1. Alle CI/CD-Jobs von `Dockerfile` migriert ✅
2. Keine aktiven Branches nutzen `Dockerfile` mehr ✅
3. Dokumentation aktualisiert ✅
4. File löschen:
   ```bash
   git rm .github/gitbook_worker/tools/docker/Dockerfile
   git commit -m "remove: Delete deprecated Dockerfile (legacy)
   
   Replaced by:
   - Dockerfile.dynamic (smart configuration, recommended)
   - Dockerfile.python (lightweight tests)
   
   See DOCKERFILE_STRATEGY.md for migration guide.
   
   Signed-off-by: ERDA Team <team@erda-project.org>"
   ```

---

## 4. Implementierungs-Details

### 4.1 `Dockerfile.dynamic` - Minimale Default-Konfiguration

**Prinzip:** Dockerfile enthält **nur Defaults**, die in `defaults/fonts.yml` definiert sind.

**Aktuelle Default-Konfiguration (`defaults/fonts.yml`):**

```yaml
version: "1.0.0"

fonts:
  # Minimal base configuration
  system:
    - name: "DejaVu Sans"
      license: "Bitstream Vera License (similar to MIT)"
      install_method: "system"
      packages:
        - "fonts-dejavu"
    
    - name: "Noto Color Emoji"
      license: "SIL Open Font License 1.1"
      install_method: "system"
      packages:
        - "fonts-noto-color-emoji"

  # Custom fonts (if any - empty by default)
  custom: {}

# License policy
allowed_licenses:
  - "CC BY 4.0"
  - "MIT"
  - "SIL Open Font License 1.1"
  - "Bitstream Vera License"

forbidden_licenses:
  - "OFL"  # Wrong abbreviation
  - "Apache"
  - "GPL"
  - "AGPL"
  - "LGPL"
  - "UFL"
  - "proprietary"
```

**Dockerfile bleibt generisch:**
```dockerfile
# Install configured fonts dynamically
RUN python3 -m tools.docker.setup_docker_environment \
    --mode install \
    --config /tmp/gitbook_worker_setup/.github/gitbook_worker/defaults/fonts.yml \
    --manifest /tmp/docker_font_installation.json \
    --verbose
```

**Ergebnis:**
- ✅ Dockerfile ist **generisch** und muss nie geändert werden
- ✅ Nur `defaults/fonts.yml` definiert Fonts
- ✅ Projekt-spezifische Fonts in `publish.yml` → `fonts_override`
- ✅ Automatische Merge-Hierarchie: `defaults/fonts.yml` → `publish.yml`

### 4.2 `Dockerfile.python` - Reine Test-Konfiguration

**Keine Änderungen nötig!**

Bleibt wie es ist:
- ✅ Minimal: Nur Python + pytest + git
- ✅ Schnell: Build in ~5 Minuten
- ✅ Fokussiert: Nur für Unit-Tests

---

## 5. Anwendungs-Dokumentation

### 5.1 Schnellstart für Entwickler

#### A. Lokale Entwicklung (Python Tests)

```bash
# Build lightweight test image
docker build -f .github/gitbook_worker/tools/docker/Dockerfile.python \
             -t erda-python-test:latest .

# Run unit tests
docker run --rm -v $(pwd):/workspace erda-python-test:latest \
    pytest .github/gitbook_worker/tests -v

# Run code quality checks
docker run --rm -v $(pwd):/workspace erda-python-test:latest \
    black --check .github/gitbook_worker/
```

**Use Case:** Schnelle Tests während der Entwicklung

#### B. Full Stack (PDF Publishing)

```bash
# Build smart worker image
docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic \
             -t erda-smart-worker:latest .

# Show build info
docker run --rm erda-smart-worker:latest --info

# Run publishing workflow
docker run --rm -v $(pwd):/workspace erda-smart-worker:latest \
    python3 -m tools.workflow_orchestrator \
    --root /workspace \
    --manifest publish.yml \
    --profile local
```

**Use Case:** Kompletter Publishing-Workflow

#### C. Helper Script (Empfohlen) ⭐

```bash
# Python tests (schnell)
python .github/gitbook_worker/tools/docker/run_docker.py test --use-python

# Full tests (langsam, aber vollständig)
python .github/gitbook_worker/tools/docker/run_docker.py test --use-dynamic

# Publishing
python .github/gitbook_worker/tools/docker/run_docker.py orchestrator --use-dynamic

# Interactive shell
python .github/gitbook_worker/tools/docker/run_docker.py shell --use-dynamic

# Build info
python .github/gitbook_worker/tools/docker/run_docker.py info --use-dynamic
```

**Use Case:** Bequemster Weg für alle Operationen

### 5.2 CI/CD Pipeline

#### A. GitHub Actions (Empfohlen)

```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  # Phase 1: Fast Python Tests (~5 min)
  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Python Test Image
        run: |
          docker build \
            -f .github/gitbook_worker/tools/docker/Dockerfile.python \
            -t erda-python-test:${{ github.sha }} .
      
      - name: Run Unit Tests
        run: |
          docker run --rm \
            -v $(pwd):/workspace \
            erda-python-test:${{ github.sha }} \
            pytest .github/gitbook_worker/tests -v -m "not slow"
      
      - name: Code Quality
        run: |
          docker run --rm \
            -v $(pwd):/workspace \
            erda-python-test:${{ github.sha }} \
            black --check .github/gitbook_worker/

  # Phase 2: Full Integration Tests (~15 min)
  test-integration:
    runs-on: ubuntu-latest
    needs: test-unit
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Smart Worker Image
        run: |
          docker build \
            -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic \
            -t erda-smart-worker:${{ github.sha }} .
      
      - name: Validate Build
        run: |
          docker run --rm erda-smart-worker:${{ github.sha }} --info
      
      - name: Run Integration Tests
        run: |
          docker run --rm \
            -v $(pwd):/workspace \
            erda-smart-worker:${{ github.sha }} \
            pytest .github/gitbook_worker/tests -v

  # Phase 3: Publishing (nur auf main branch)
  publish:
    runs-on: ubuntu-latest
    needs: test-integration
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Smart Worker Image
        run: |
          docker build \
            -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic \
            -t erda-smart-worker:latest .
      
      - name: Generate PDF
        run: |
          docker run --rm \
            -v $(pwd):/workspace \
            erda-smart-worker:latest \
            python3 -m tools.workflow_orchestrator \
            --root /workspace \
            --manifest publish.yml \
            --profile ci
      
      - name: Upload PDF
        uses: actions/upload-artifact@v3
        with:
          name: erda-book-pdf
          path: publish/das-erda-buch.pdf
```

**Vorteile:**
- ⚡ **Phase 1** (5 min): Schnelles Feedback bei Unit-Test-Fehlern
- 🔍 **Phase 2** (15 min): Vollständige Validierung
- 📦 **Phase 3**: Nur bei erfolgreichen Tests

#### B. GitLab CI

```yaml
stages:
  - test-fast
  - test-full
  - publish

variables:
  DOCKER_DRIVER: overlay2

# Phase 1: Fast Tests
test:unit:
  stage: test-fast
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f .github/gitbook_worker/tools/docker/Dockerfile.python -t test:latest .
    - docker run --rm -v $(pwd):/workspace test:latest pytest tests/ -v -m "not slow"

# Phase 2: Full Tests
test:integration:
  stage: test-full
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic -t worker:latest .
    - docker run --rm -v $(pwd):/workspace worker:latest pytest tests/ -v

# Phase 3: Publish
publish:pdf:
  stage: publish
  image: docker:latest
  services:
    - docker:dind
  only:
    - main
  script:
    - docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic -t worker:latest .
    - docker run --rm -v $(pwd):/workspace worker:latest python3 -m tools.workflow_orchestrator
  artifacts:
    paths:
      - publish/das-erda-buch.pdf
```

### 5.3 Font-Konfiguration anpassen

#### A. Neue Font hinzufügen

**Datei:** `.github/gitbook_worker/defaults/fonts.yml`

```yaml
fonts:
  custom:
    MyFont:
      name: "My Custom Font"
      license: "CC BY 4.0"  # Muss in allowed_licenses sein!
      license_url: "https://creativecommons.org/licenses/by/4.0/"
      install_method: "file"
      paths:
        - ".github/fonts/my-font/MyFont-Regular.ttf"
        - ".github/fonts/my-font/MyFont-Bold.ttf"
```

**Rebuild:**
```bash
# Image neu bauen mit neuer Font-Config
docker build -f Dockerfile.dynamic -t erda-smart-worker:latest .

# Prüfen ob Font installiert wurde
docker run --rm erda-smart-worker:latest fc-list | grep "My Custom Font"

# Build-Info anzeigen
docker run --rm erda-smart-worker:latest --info
```

**Keine Änderung am Dockerfile nötig!** ✅

#### B. Font entfernen

**Datei:** `.github/gitbook_worker/defaults/fonts.yml`

```yaml
fonts:
  custom:
    # MyFont: # ← Einfach auskommentieren oder löschen
```

**Rebuild:**
```bash
docker build -f Dockerfile.dynamic -t erda-smart-worker:latest .
```

#### C. Projekt-spezifische Font-Override

**Datei:** `publish.yml`

```yaml
fonts_override:
  custom:
    ProjectFont:
      name: "Project Specific Font"
      license: "MIT"
      install_method: "file"
      paths:
        - ".github/fonts/project-font/Font.ttf"
```

**Merge-Hierarchie:**
```
defaults/fonts.yml → publish.yml (fonts_override) → Docker Image
```

---

## 6. Troubleshooting

### Problem 1: Font nicht im Docker-Image

**Symptom:**
```bash
docker run --rm IMAGE fc-list | grep MyFont
# (keine Ausgabe)
```

**Lösung:**
1. Prüfe `fonts.yml`: Ist Font konfiguriert?
2. Prüfe Build-Log: Wurden Fonts installiert?
3. Check Build-Info:
   ```bash
   docker run --rm IMAGE --info
   # Suche nach MyFont in "installed_fonts"
   ```
4. Rebuild mit `--no-cache`:
   ```bash
   docker build --no-cache -f Dockerfile.dynamic -t IMAGE .
   ```

### Problem 2: License Violation

**Symptom:**
```
ERROR: LICENSE COMPLIANCE VIOLATION
Font 'BadFont': Forbidden license 'GPL'
Build failed with exit code 2
```

**Lösung:**
1. **Option A:** Font entfernen aus `fonts.yml`
2. **Option B:** Font mit kompatibler Lizenz ersetzen
3. **Option C:** Lizenz zu `allowed_licenses` hinzufügen (nur wenn AGENTS.md erlaubt!)

### Problem 3: Validation fehlgeschlagen

**Symptom:**
```
ERROR: Environment validation failed
See /opt/gitbook_worker/reports/docker_validation_report.json
```

**Lösung:**
1. Build-Info anzeigen:
   ```bash
   docker run --rm IMAGE --info
   ```
2. Prüfe `validation_report.json` auf Fehler
3. Häufige Ursachen:
   - Checksum Mismatch: Font-Datei geändert
   - Missing Tool: Paket nicht installiert
   - Font Cache: fc-cache fehlgeschlagen

### Problem 4: Image zu groß

**Symptom:**
```
erda-smart-worker:latest  5.2 GB
```

**Lösung:**
1. Multi-Stage-Build ist aktiv? (sollte ~4 GB sein)
2. Alte Images aufräumen:
   ```bash
   docker system prune -a
   ```
3. Für Tests: Nutze `Dockerfile.python` (nur ~300 MB)

---

## 7. Best Practices Zusammenfassung

### ✅ DO

1. **Nutze `Dockerfile.dynamic`** für Production/Publishing
2. **Nutze `Dockerfile.python`** für schnelle Unit-Tests
3. **Konfiguriere Fonts** in `fonts.yml`, nicht im Dockerfile
4. **Prüfe Build-Info** mit `--info` nach jedem Build
5. **CI/CD Split:** Fast tests (python) → Full tests (dynamic)
6. **Versioniere Images** mit Git-SHA oder Semver-Tags
7. **Dokumentiere** Custom-Fonts in `fonts.yml` mit License-Info
8. **Teste lokal** mit `run_docker.py` (bequemer Helper)

### ❌ DON'T

1. **Vermeide `Dockerfile`** (Legacy, deprecated)
2. **Hardcode keine Fonts** im Dockerfile
3. **Skippe nicht Validation** (könnte Probleme verschleiern)
4. **Verwende keine** inkompatibler Lizenzen (OFL, GPL, etc.)
5. **Baue nicht ohne Cache** unnötig (langsam)
6. **Ignoriere nicht** Build-Warnungen
7. **Mixe nicht** `--use-dynamic` und `--use-legacy`
8. **Vergiss nicht** Image-Tags (latest reicht nicht für Production)

---

## 8. Decision Record

**Datum:** 2025-11-11

**Entscheidung:** Zwei-Image-Strategie mit Deprecation von `Dockerfile`

**Begründung:**

| Kriterium | Begründung |
|-----------|------------|
| **Wartbarkeit** | `Dockerfile.dynamic` ist Single Source of Truth (fonts.yml) |
| **Compliance** | Automatische License-Checks verhindern AGENTS.md-Verstöße |
| **Qualität** | Integrierte Validierung erhöht Zuverlässigkeit |
| **Performance** | `Dockerfile.python` gibt schnelles Feedback (~5 min) |
| **Transparenz** | Build-Artefakte dokumentieren Installation |
| **Konsistenz** | Docker-Image immer synchron mit lokaler Config |

**Konsequenzen:**

✅ **Positiv:**
- Reduzierte Maintenance-Last (nur 1 konfigurierbares Dockerfile)
- Bessere CI/CD-Performance (Fast-Lane mit Dockerfile.python)
- Höhere Code-Qualität durch automatische Checks
- AGENTS.md-Compliance automatisch gesichert

⚠️ **Negativ (akzeptabel):**
- Initiales Lernen der neuen Struktur nötig
- Migration bestehender CI/CD-Jobs erforderlich
- Dockerfile.dynamic Build dauert ~15 min (aber einmalig)

**Verantwortlich:** ERDA GitBook Worker Team

**Status:** ✅ APPROVED

---

## 9. Lizenz-Konformität

Dieses Dokument und die beschriebenen Dockerfiles sind konform mit **AGENTS.md**:

- **Dokumentation:** CC BY-SA 4.0
- **Code (Dockerfiles):** MIT
- **Fonts (im Image):** Automatisch geprüft gegen allowed_licenses (CC BY 4.0, MIT, SIL OFL 1.1)
- **Compliance-Check:** Automatisch bei jedem Build

---

**Signed-off-by:** ERDA GitBook Worker Team <team@erda-project.org>

**DCO:** This strategy document and all referenced Dockerfiles comply with Developer Certificate of Origin (DCO) requirements.
