# Zusammenfassung: Docker Logging & Diagnostik-Lösung

## Problem

Beim Ausführen des Orchestrators im Docker-Container:
- ❌ Dateien (readme.md, etc.) werden als "to be removed/deleted" markiert
- ❌ Logs verschwinden im Container
- ❌ Debugging ist schwierig

## Implementierte Lösung

### 1. Externes Log-Volume ✅

**Dateien geändert:**
- `tools/logging_config.py`: Neue Funktion `get_log_directory()` mit `DOCKER_LOG_DIR` Support
- `scripts/run-in-docker.ps1`: Volume-Mount für `.docker-logs/`
- `scripts/run-in-docker.sh`: Volume-Mount für `.docker-logs/`
- `.gitignore`: `.docker-logs/` hinzugefügt

**Funktionsweise:**
```powershell
# Automatisch in run-in-docker.ps1/sh:
docker run -v "$PWD:/workspace" \
           -v "$PWD/.docker-logs:/docker-logs" \
           -e DOCKER_LOG_DIR=/docker-logs \
           ...
```

**Vorteile:**
- ✅ Logs persistieren außerhalb des Containers
- ✅ Einfacher Zugriff vom Host: `.docker-logs/workflow.log`
- ✅ Keine Git-Verschmutzung
- ✅ Abwärtskompatibel (funktioniert auch ohne Docker)

### 2. Diagnostik-Tool ✅

**Neue Dateien:**
- `tools/docker/docker_diagnostics.py`: Python-Tool für File-Tracking
- `scripts/diagnose-docker.ps1`: PowerShell-Wrapper für automatisierte Diagnostik

**Funktionsweise:**
```powershell
# Automatisiert:
.\diagnose-docker.ps1 -Profile local

# Oder manuell:
python -m tools.docker.docker_diagnostics capture-before
.\run-in-docker.ps1 orchestrator
python -m tools.docker.docker_diagnostics capture-after
python -m tools.docker.docker_diagnostics analyze
```

**Was wird getracked:**
- 📁 Dateien hinzugefügt/entfernt
- ✏️ Dateiinhalt geändert (SHA256)
- ⚠️ Git-Status geändert
- 🔒 File-Permissions geändert
- 👤 File-Ownership geändert

### 3. Dokumentation ✅

**Neue Dateien:**
- `docs/docker/LOGGING_STRATEGY.md`: Strategie & Architektur
- `docs/docker/DEBUGGING.md`: Anwendungs-Guide & Troubleshooting

## Nutzung

### Einfacher Lauf (mit Logging)
```powershell
.\run-in-docker.ps1 orchestrator -Profile local
# Logs verfügbar in: .docker-logs/workflow.log
```

### Diagnostik-Lauf (Problem analysieren)
```powershell
.\diagnose-docker.ps1 -Profile local
# Erstellt:
#   .docker-logs/snapshot-before.json
#   .docker-logs/snapshot-after.json
#   .docker-logs/analysis.json
#   .docker-logs/workflow.log
```

### Logs prüfen
```powershell
# Letzte 50 Zeilen
Get-Content .docker-logs/workflow.log -Tail 50

# Vollständig
Get-Content .docker-logs/workflow.log

# Analyse
Get-Content .docker-logs/analysis.json | ConvertFrom-Json
```

## Nächste Schritte

### Sofort möglich:
1. ✅ Docker-Lauf mit Logging testen:
   ```powershell
   .\run-in-docker.ps1 orchestrator -Profile local
   ```

2. ✅ Diagnostik testen:
   ```powershell
   .\diagnose-docker.ps1 -Profile local
   ```

### Zur Problemlösung:
1. **Diagnostik-Lauf durchführen** mit `diagnose-docker.ps1`
2. **Analyse prüfen**: Welche Dateien haben Git-Status geändert?
3. **Logs prüfen**: Was hat der Orchestrator gemacht?
4. **Root Cause identifizieren**:
   - File-Permissions Problem? → Container User/UID prüfen
   - Git-Operationen Problem? → `gitbook_style.py` Git-Befehle prüfen
   - Volume-Mount Problem? → Docker-Konfiguration prüfen

## Technische Details

### Umgebungsvariablen

| Variable | Wert | Zweck |
|----------|------|-------|
| `DOCKER_LOG_DIR` | `/docker-logs` | Externes Log-Verzeichnis im Container |
| `GITBOOK_WORKER_LOG_STDOUT_ONLY` | `1` | Nur stdout (Docker build) |

### Log-Verzeichnis-Priorität

1. `DOCKER_LOG_DIR` (wenn gesetzt) → für Docker-Läufe
2. `GH_LOGS_DIR` (default) → für lokale Läufe

### Snapshot-Format

```json
{
  "timestamp": "2025-11-11T...",
  "git_branch": "release_candidate",
  "git_commit": "abc123...",
  "files": {
    "content/README.md": {
      "path": "content/README.md",
      "exists": true,
      "size": 1234,
      "sha256": "abc...",
      "git_status": "tracked",
      "permissions": "-rw-r--r--",
      "owner": "user"
    }
  }
}
```

## Lizenz

- **Dokumentation**: CC BY-SA 4.0
- **Code**: MIT

## Commit Message

```
feat: Add Docker logging and diagnostics tools

Implemented comprehensive solution for Docker orchestrator debugging:

1. External Log Volume:
   - Modified logging_config.py to support DOCKER_LOG_DIR
   - Updated run-in-docker.ps1/sh with volume mounts
   - Logs persist in .docker-logs/ outside container
   - Added .docker-logs/ to .gitignore

2. Diagnostics Tool:
   - New docker_diagnostics.py for file state tracking
   - Automated diagnose-docker.ps1 wrapper
   - Tracks: files, git status, permissions, ownership
   - Detailed analysis with visual output

3. Documentation:
   - DOCKER_LOGGING_STRATEGY.md: Architecture & strategy
   - DEBUGGING.md: Usage guide & troubleshooting

Key Features:
✅ Logs accessible outside container
✅ File changes tracked before/after Docker runs
✅ Git status changes identified
✅ Permissions/ownership issues detected
✅ Automated workflow with diagnose-docker.ps1

Usage:
  .\run-in-docker.ps1 orchestrator
  .\diagnose-docker.ps1 -Profile local

Files:
  - .github/gitbook_worker/tools/logging_config.py
  - .github/gitbook_worker/tools/docker/docker_diagnostics.py
  - .github/gitbook_worker/tools/docker/readme.md
  - .github/gitbook_worker/scripts/run-in-docker.ps1
  - .github/gitbook_worker/scripts/run-in-docker.sh
  - .github/gitbook_worker/scripts/diagnose-docker.ps1
  - .github/gitbook_worker/docs/docker/README.md
  - .github/gitbook_worker/docs/docker/LOGGING_STRATEGY.md
  - .github/gitbook_worker/docs/docker/DEBUGGING.md
  - .github/gitbook_worker/docs/docker/IMPLEMENTATION_SUMMARY.md
  - .gitignore

Signed-off-by: ERDA GitBook Worker Team <team@erda-project.org>
```

Signed-off-by: ERDA GitBook Worker Team <team@erda-project.org>
