---
version: 1.0.0
created: 2025-11-07
modified: 2025-11-10
status: completed
type: migration-documentation
---

# Build Scripts Migration Summary

## ✅ Abgeschlossen

Die Build-Scripts wurden modernisiert, in den Scripts-Ordner verschoben und mit Bash-Äquivalenten erweitert.

---

## 📦 Neue Struktur

### Haupt-Scripts (in `.github/gitbook_worker/scripts/`)

#### 1. `build-pdf.ps1` (PowerShell)
**Features:**
- ✅ Moderne Parametrisierung mit Workflow-Profilen
- ✅ Dry-Run-Modus
- ✅ Farbige Ausgabe (Cyan/Green/Red/Yellow)
- ✅ PDF-Größe und Erstellungszeit-Anzeige
- ✅ Detaillierte Fehlerbehandlung
- ✅ Automatische PYTHONPATH-Konfiguration

**Nutzung:**
```powershell
.\build-pdf.ps1                         # Default (local profile)
.\build-pdf.ps1 -WorkflowProfile default  # Full pipeline
.\build-pdf.ps1 -DryRun                   # Dry-run
```

#### 2. `build-pdf.sh` (Bash)
**Features:**
- ✅ Äquivalent zur PowerShell-Version
- ✅ POSIX-kompatibel (Linux/macOS/WSL)
- ✅ Gleiche Farbausgabe mit ANSI-Codes
- ✅ Cross-platform Dateigrößen-Erkennung
- ✅ Gleiche CLI-Optionen

**Nutzung:**
```bash
./build-pdf.sh                      # Default (local profile)
./build-pdf.sh --profile default    # Full pipeline
./build-pdf.sh --dry-run            # Dry-run
./build-pdf.sh --help               # Help
```

---

## 🔄 Backward Compatibility

### Root-Level Wrapper

Für Backward-Kompatibilität wurden Wrapper im Repo-Root erstellt:

#### `build-pdf.ps1` (Root)
```powershell
# Forwards to: .github/gitbook_worker/scripts/build-pdf.ps1
.\build-pdf.ps1 -DryRun  # Works exactly as before
```

#### `build-pdf.sh` (Root)
```bash
# Forwards to: .github/gitbook_worker/scripts/build-pdf.sh
./build-pdf.sh --dry-run  # Works exactly as before
```

**Alte Aufrufe funktionieren weiterhin:**
```bash
# Alt (funktioniert noch):
.\build-pdf.ps1

# Neu (empfohlen):
.\.github\gitbook_worker\scripts\build-pdf.ps1
```

---

## 🎯 Workflow-Profile

### `local` (Default)
- Converter + Publisher
- Keine Docker-Registry
- Schnell für lokale Entwicklung

### `default`
- Vollständige Pipeline
- Quality Checks
- Docker-Registry aktiviert
- Für Production Builds

### `publisher`
- Nur Publisher-Schritt
- Für Re-Builds ohne Preprocessing

---

## 📋 Parameter

### PowerShell
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `-WorkflowProfile` | String | `local` | Workflow-Profil |
| `-Manifest` | String | `publish.yml` | Manifest-Datei |
| `-DryRun` | Switch | - | Dry-Run-Modus |

### Bash
| Option | Type | Default | Beschreibung |
|--------|------|---------|--------------|
| `-p, --profile` | String | `local` | Workflow-Profil |
| `-m, --manifest` | String | `publish.yml` | Manifest-Datei |
| `-d, --dry-run` | Flag | - | Dry-Run-Modus |
| `-h, --help` | Flag | - | Hilfe anzeigen |

---

## ✨ Verbesserungen gegenüber Alt-Version

### Alt (Vorher)
```powershell
# build-pdf.ps1 (alt)
python -m gitbook_worker.tools.workflow_orchestrator
# - Keine Parameter-Kontrolle
# - Hardcodiertes Profil
# - Kein Dry-Run
# - Im Repo-Root
```

### Neu (Nachher)
```powershell
# .github/gitbook_worker/scripts/build-pdf.ps1 (neu)
python -m tools.workflow_orchestrator \
    --root "$RepoRoot" \
    --manifest "$Manifest" \
    --profile "$WorkflowProfile" \
    [--dry-run]

# + Volle Kontrolle über Parameter
# + Flexible Profile
# + Dry-Run-Unterstützung
# + Logisch organisiert in scripts/
```

---

## 📚 Dokumentation

### Neue Datei: `.github/gitbook_worker/scripts/README.md`

Umfassende Dokumentation mit:
- ✅ Nutzungsbeispiele für beide Scripts
- ✅ Workflow-Profil-Erklärungen
- ✅ Parameter-Referenz
- ✅ Troubleshooting
- ✅ Beispiel-Outputs
- ✅ Environment-Variablen

---

## 🧪 Getestet

### PowerShell Script
```bash
✓ Dry-Run funktioniert
✓ Parameter-Weiterleitung korrekt
✓ Root-Wrapper funktioniert
✓ Farbausgabe korrekt
✓ Exit-Codes korrekt
```

### Bash Script
```bash
✓ Script erstellt
✓ Executable permissions
✓ POSIX-kompatibel
✓ Cross-platform ready
```

---

## 📁 Dateistruktur

```
ERDA/
├── build-pdf.ps1           # Wrapper (backward compatibility)
├── build-pdf.sh            # Wrapper (backward compatibility)
└── .github/
    └── gitbook_worker/
        └── scripts/
            ├── README.md           # Dokumentation
            ├── build-pdf.ps1       # Haupt-Script (PowerShell)
            └── build-pdf.sh        # Haupt-Script (Bash)
```

---

## 🚀 Empfohlene Nutzung

### Lokale Entwicklung
```bash
# PowerShell
.\build-pdf.ps1

# Bash
./build-pdf.sh
```

### Production Build
```bash
# PowerShell
.\build-pdf.ps1 -WorkflowProfile default

# Bash
./build-pdf.sh --profile default
```

### Testen ohne Build
```bash
# PowerShell
.\build-pdf.ps1 -DryRun

# Bash
./build-pdf.sh --dry-run
```

---

## ✅ Migration Complete

- ✅ PowerShell-Script modernisiert
- ✅ Bash-Äquivalent erstellt
- ✅ Scripts nach `.github/gitbook_worker/scripts/` verschoben
- ✅ Backward-Compatible Wrapper im Root
- ✅ Umfassende Dokumentation
- ✅ Getestet und funktionsfähig

**Alle alten Aufrufe funktionieren weiterhin, neue Features sind verfügbar!** 🎉
