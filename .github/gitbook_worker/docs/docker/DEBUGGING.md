# Docker Debugging & Diagnostics

Diese Tools helfen beim Debugging von Problemen mit Docker-basierten Orchestrator-Läufen.

## Problem

Beim Ausführen des Orchestrators im Docker-Container können folgende Probleme auftreten:
- Dateien werden als "to be removed/deleted" in Git markiert
- Logs sind schwer zugänglich
- File-Permissions/Ownership ändern sich unerwartet
- Debugging ist erschwert

## Lösung

### 1. Externes Log-Volume

**Automatisch aktiviert** in allen `run-in-docker.*` Skripten:
- Logs werden in `.docker-logs/` geschrieben (außerhalb des Containers)
- Einfacher Zugriff vom Host aus
- Keine Git-Verschmutzung

```powershell
# Orchestrator ausführen
.\run-in-docker.ps1 orchestrator -Profile local

# Logs prüfen
Get-Content .docker-logs/workflow.log -Tail 50
```

### 2. Diagnostik-Tool

Trackt Dateiänderungen vor/während/nach Docker-Ausführung.

#### Manuelle Nutzung

```powershell
# 1. Before-Snapshot
python -m tools.docker.docker_diagnostics capture-before

# 2. Docker ausführen
.\run-in-docker.ps1 orchestrator -Profile local

# 3. After-Snapshot
python -m tools.docker.docker_diagnostics capture-after

# 4. Analyse
python -m tools.docker.docker_diagnostics analyze
```

#### Automatisierte Nutzung

```powershell
# Alles in einem Schritt
.\diagnose-docker.ps1 -Profile local
```

Dies führt automatisch aus:
1. Before-Snapshot
2. Docker-Orchestrator
3. After-Snapshot
4. Analyse mit Bericht

### 3. Analyse-Ausgabe

Das Tool zeigt:
- **📁 Files ADDED**: Neue Dateien
- **🗑️ Files REMOVED**: Gelöschte Dateien
- **✏️ Files MODIFIED**: Geänderte Dateien (mit Git-Status)
- **⚠️ Git STATUS CHANGED**: Dateien mit geändertem Git-Status
- **🔒 PERMISSIONS CHANGED**: Geänderte File-Permissions
- **👤 OWNER CHANGED**: Geänderte File-Ownership

Beispiel:
```
⚠️  Git STATUS CHANGED: 2
  ! content/README.md
    Before: tracked
    After:  D  (deleted)
  ! assets/readme.md
    Before: tracked
    After:  D  (deleted)
```

## Umgebungsvariablen

### `DOCKER_LOG_DIR`

Externes Log-Verzeichnis (Container-Pfad):
```bash
docker run -v "$PWD:/workspace" \
           -v "$PWD/.docker-logs:/docker-logs" \
           -e DOCKER_LOG_DIR=/docker-logs \
           erda-workflow-tools:latest \
           <command>
```

### `GITBOOK_WORKER_LOG_STDOUT_ONLY`

Nur stdout-Logging (für Docker build):
```dockerfile
ENV GITBOOK_WORKER_LOG_STDOUT_ONLY=1
```

## Dateien

- `docker_diagnostics.py`: Diagnostik-Tool (Python)
- `diagnose-docker.ps1`: Automatisiertes Wrapper-Skript (PowerShell)
- `run-in-docker.ps1`: Docker-Run-Skript mit Log-Volume (PowerShell)
- `run-in-docker.sh`: Docker-Run-Skript mit Log-Volume (Bash)
- `DOCKER_LOGGING_STRATEGY.md`: Detaillierte Strategie-Dokumentation

## Troubleshooting

### Problem: Logs verschwinden

**Lösung**: Prüfen Sie, ob `DOCKER_LOG_DIR` gesetzt ist:
```powershell
docker run ... -e DOCKER_LOG_DIR=/docker-logs ...
```

### Problem: Dateien als "deleted" markiert

**Lösung**: Diagnostik-Tool ausführen:
```powershell
.\diagnose-docker.ps1 -Profile local
```

Prüfen Sie:
- File-Permissions (🔒)
- File-Ownership (👤)
- Git-Status-Änderungen (⚠️)

### Problem: Git-Status nach Docker-Lauf

**Lösung**: 
1. Logs in `.docker-logs/workflow.log` prüfen
2. Analyse in `.docker-logs/analysis.json` prüfen
3. Git-Diff vor/nach Docker-Lauf vergleichen

```powershell
# Git-Status vor Docker
git status > .docker-logs/git-status-before.txt

# Docker ausführen
.\run-in-docker.ps1 orchestrator

# Git-Status nach Docker
git status > .docker-logs/git-status-after.txt

# Vergleich
Compare-Object (Get-Content .docker-logs/git-status-before.txt) `
               (Get-Content .docker-logs/git-status-after.txt)
```

## Best Practices

1. **Immer externes Log-Volume nutzen** (automatisch in Skripten)
2. **Bei Problemen: Diagnostik-Tool ausführen**
3. **Logs regelmäßig prüfen**: `.docker-logs/workflow.log`
4. **Git-Status vor/nach Docker-Lauf vergleichen**

## Lizenz

- **Dokumentation**: CC BY-SA 4.0
- **Code**: MIT

Signed-off-by: ERDA GitBook Worker Team <team@erda-project.org>
