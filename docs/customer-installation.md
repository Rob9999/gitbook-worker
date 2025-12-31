---
version: 1.0.0
date: 2025-12-31
status: draft
history:
  - "init: 2025-12-31"
---

# Kundenguide: Installation & Start des GitBook Worker

Ziel: Sicherstellen, dass immer unsere gelieferte Version des `gitbook_worker` genutzt wird – auch wenn auf derselben Maschine alte Projekte mit eigenen `tools/`-Modulen liegen.

## 1) Saubere Python-Umgebung (pro Projekt)
1. In das Projektverzeichnis wechseln (z. B. `C:\RAMProjects\ERDA`).
2. Virtuelle Umgebung anlegen und aktivieren (Windows PowerShell):
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Alte Pakete entfernen, falls vorhanden:
   ```powershell
   pip uninstall -y gitbook-worker tools
   ```
4. Unsere Version installieren:
   - Mit Wheel (empfohlen):
     ```powershell
     pip install --no-deps --force-reinstall dist/gitbook_worker-2.0.4.post1-py3-none-any.whl
     ```
   - Oder direkt aus dem gelieferten Repo:
     ```powershell
     pip install --no-deps --force-reinstall .
     ```

## 2) Prüfen, was wirklich importiert wird
Nach der Installation kontrollieren, dass keine fremden `tools`-Module gezogen werden:
```powershell
python - <<'PY'
import gitbook_worker, tools
print("gitbook_worker:", gitbook_worker.__file__)
print("tools shim     :", tools.__file__)
PY
```
Die Pfade müssen in das aktivierte `.venv` zeigen (z. B. `...\.venv\Lib\site-packages\gitbook_worker\...`).

## 3) Orchestrator starten
Beispiel für die deutsche Ausgabe mit lokalem Profil (zieht `de/publish.yml` aus `content.yaml` automatisch):
```powershell
python -m gitbook_worker.tools.workflow_orchestrator run --root C:\RAMProjects\ERDA --profile local --lang de
```
Typische Varianten:
- Nur Converter/PDF-Pipeline: `--step converter` oder `--step publisher`
- Dry-Run: `--dry-run` (führt keine externen Schritte aus)
- Anderes Manifest explizit: `--manifest de/publish.yml` (überschreibt die automatische Auflösung aus `content.yaml`)

## 4) Docker-Run (optional, wenn Docker Desktop verfügbar)
```powershell
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile local --use-dynamic --lang de --root C:\RAMProjects\ERDA
```
Hinweise:
- Fonts werden zur Laufzeit über Volume-Mounts injiziert; `fonts-storage/` und `.github/fonts/` müssen vorhanden sein.
- Auf Windows erfolgt die Pfad-Umsetzung automatisch (Docker Desktop).

## 5) Häufige Stolpersteine
- **Falsches Modul "tools"**: Immer das `.venv` aktivieren und ggf. `pip uninstall tools` ausführen.
- **Kein Manifest gefunden**: `--manifest` relativ zum Repo-Root angeben (z. B. `de/publish.yml`) oder Flag weglassen, dann greift `content.yaml`.
- **LuaTeX/Fonts fehlen**: Sicherstellen, dass `luaotfload-tool --update --force` einmalig gelaufen ist (wird im Test-Fixture getan, kann aber lokal nötig sein).

## 6) Schnell-Checkliste für Support
- `.venv` aktiv? (`where python` zeigt auf Projekt-`.venv`)
- `gitbook_worker.__version__` = 2.0.4.post1?
- `tools.__file__` verweist auf `.venv\Lib\site-packages\gitbook_worker\tools\__init__.py`?
- Orchestrator-Log zeigt `manifest=...\de\publish.yml` und `tools_dir=...site-packages\gitbook_worker\tools`?
