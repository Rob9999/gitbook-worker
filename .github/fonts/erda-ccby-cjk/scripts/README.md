# ERDA CJK Font Scripts

## Verfügbare Scripts

### `clear-all-caches.ps1` (Windows)
Löscht alle Windows Font-Caches und startet den FontCache-Service neu.

**Verwendung:**
```powershell
# Als Administrator ausführen!
.\clear-all-caches.ps1
```

**Was wird gelöscht:**
- `%USERPROFILE%\AppData\Local\Microsoft\Windows\Fonts\*.dat`
- `%USERPROFILE%\AppData\Local\Microsoft\Windows\Caches\*.cache`
- `%TEMP%\*.tmp` (Font-bezogen)
- fontconfig-Cache (`fc-cache -f`)
- LuaTeX-Cache (`~/.texlive*/texmf-var/luatex-cache/`)

**Nach dem Ausführen:**
1. Anwendungen neu starten (Browser, PDF-Reader, Office)
2. Browser-Caches leeren (Ctrl+Shift+Delete)
3. ggf. Windows neu starten

---

### `test-admin-cache-refresh.ps1` (Windows)
Testet ob das Script Admin-Rechte hat und versucht den FontCache-Service neu zu starten.

**Verwendung:**
```powershell
# Als Administrator ausführen!
.\test-admin-cache-refresh.ps1
```

**Output:**
```
✓ Running as Administrator
✓ FontCache service found
✓ FontCache service stopped
✓ FontCache service started
✓ Font cache refresh completed
```

---

## Neue Scripts hinzufügen

### PowerShell (Windows)
```powershell
#!/usr/bin/env pwsh
# Description: Your script description

# Your code here
Write-Host "✓ Done"
```

### Bash (Linux/macOS)
```bash
#!/usr/bin/env bash
# Description: Your script description

# Your code here
echo "✓ Done"
```

### Python (Cross-platform)
```python
#!/usr/bin/env python3
"""Your script description."""

import platform

def main():
    system = platform.system()
    print(f"Running on: {system}")
    # Your code here
    print("✓ Done")

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

**Problem:** "FontCache service konnte nicht gestoppt werden"
- **Lösung:** Script als Administrator ausführen

**Problem:** "fc-cache nicht gefunden"
- **Lösung:** Fontconfig installieren:
  - Windows: Teil von TeXLive oder MiKTeX
  - Linux: `sudo apt install fontconfig`
  - macOS: `brew install fontconfig`

**Problem:** Font wird nicht aktualisiert
- **Lösung:**
  1. Alle Anwendungen schließen
  2. `clear-all-caches.ps1` ausführen
  3. Windows neu starten
  4. PDF/Browser-Cache leeren

Siehe auch: [../docs/FONT-CACHE-TROUBLESHOOTING.md](../docs/FONT-CACHE-TROUBLESHOOTING.md)
