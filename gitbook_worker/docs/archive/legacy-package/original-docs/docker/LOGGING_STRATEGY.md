# Docker Logging Strategie

## Problem

Beim Ausführen des Orchestrators im Docker Container:
- Logs verschwinden oder sind schwer zugänglich
- Dateien werden als "to be removed/deleted" in Git markiert
- Debugging ist erschwert, da Logs im Container isoliert sind

## Lösung: Externes Log-Volume

### 1. Architektur

```
Host                          Docker Container
────────────────────────      ─────────────────────────
/workspace                 -> /workspace (read/write)
  ├── .github/
  ├── content/
  └── ...

/workspace/.docker-logs/   -> /docker-logs (write-only)
  ├── workflow.log
  ├── orchestrator.log
  └── ...
```

### 2. Umgebungsvariablen

- **`DOCKER_LOG_DIR`**: Externes Log-Verzeichnis (Host-Pfad oder Container-Pfad)
  - Default: Nicht gesetzt → Logs gehen nach `.github/logs/` (alter Modus)
  - Wenn gesetzt: Logs gehen in dieses Verzeichnis
  
- **`GITBOOK_WORKER_LOG_STDOUT_ONLY`**: Nur stdout logging
  - `"1"`: Nur stdout (für Docker build)
  - `"0"` oder nicht gesetzt: File + stdout (normaler Modus)

### 3. Implementierung

#### a) Logging-Konfiguration erweitern (`logging_config.py`)

```python
def get_log_directory() -> Path | None:
    """Determine the log directory based on environment."""
    import os
    
    # Check for external Docker log directory
    docker_log_dir = os.environ.get("DOCKER_LOG_DIR")
    if docker_log_dir:
        log_path = Path(docker_log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path
    
    # Default: use .github/logs/
    return GH_LOGS_DIR
```

#### b) Docker-Run-Skripte anpassen

**PowerShell (`run-in-docker.ps1`)**:
```powershell
# Erstelle externes Log-Verzeichnis
$LogDir = Join-Path $workDir ".docker-logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

docker run --rm `
    -v "${workDir}:/workspace" `
    -v "${LogDir}:/docker-logs" `
    -e DOCKER_LOG_DIR=/docker-logs `
    -e PYTHONPATH=/workspace `
    $IMAGE_TAG `
    <command>
```

**Bash (`run-in-docker.sh`)**:
```bash
LOG_DIR="$PWD/.docker-logs"
mkdir -p "$LOG_DIR"

docker run --rm \
    -v "$PWD:/workspace" \
    -v "$LOG_DIR:/docker-logs" \
    -e DOCKER_LOG_DIR=/docker-logs \
    -e PYTHONPATH=/workspace \
    "$IMAGE_TAG" \
    <command>
```

### 4. Git-Ignore-Konfiguration

```gitignore
# .gitignore
.docker-logs/
```

### 5. Vorteile

✅ **Logs persistieren** außerhalb des Containers  
✅ **Einfacher Zugriff** vom Host aus  
✅ **Keine Git-Verschmutzung** (logs in separatem Verzeichnis)  
✅ **Abwärtskompatibel** (funktioniert auch ohne Docker)  
✅ **Debugging** wird stark vereinfacht  

### 6. Verwendung

#### Lokal mit Docker
```powershell
.\run-in-docker.ps1 orchestrator -Profile local
# Logs sind verfügbar in .docker-logs/
```

#### Ohne Docker (direkte Ausführung)
```powershell
python -m tools.workflow_orchestrator --root . --manifest publish.yml --profile local
# Logs gehen nach .github/logs/ (wie bisher)
```

### 7. Diagnostik

Nach dem Lauf:
```powershell
# Logs prüfen
Get-Content .docker-logs/workflow.log -Tail 50

# Git-Status prüfen
git status

# Vergleich: Was hat sich geändert?
git diff
```

## Nächste Schritte

1. ✅ Dokumentation erstellt
2. ⏳ `logging_config.py` erweitern
3. ⏳ `run-in-docker.ps1` anpassen
4. ⏳ `run-in-docker.sh` anpassen
5. ⏳ `.gitignore` aktualisieren
6. ⏳ Test durchführen

## Lizenz

Dieses Dokument: **CC BY-SA 4.0**  
Code-Beispiele: **MIT**

Signed-off-by: ERDA GitBook Worker Team <team@erda-project.org>
