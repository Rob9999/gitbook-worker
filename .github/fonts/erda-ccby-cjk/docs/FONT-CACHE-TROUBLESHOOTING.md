# 🔧 Font Cache Troubleshooting Guide

## Problem: Font Nicht Aktualisiert

Wenn Sie eine neue Version der ERDA CJK Font gebaut haben, aber die alte Version noch angezeigt wird, liegt das an verschiedenen Cache-Ebenen in Windows und Anwendungen.

## 🎯 Schnelle Lösung (Empfohlen)

### Option 1: Automatisches Cache-Clearing (Erfordert Admin)

```powershell
# Als Administrator ausführen:
.\clear-all-caches.ps1
```

### Option 2: Python-Skript mit Cache-Refresh

```bash
# Font bauen und Cache refreshen
python build_ccby_cjk_font.py --refresh-cache --install

# Als Administrator für vollständigen Refresh:
# (Rechtsklick auf PowerShell → "Als Administrator ausführen")
```

---

## 📦 Windows Font Cache Ebenen

Windows cached Fonts an **mehreren Orten**:

### 1. **System Font Cache** 🏛️
   - **Location:** `%WINDIR%\System32\FNTCACHE.DAT`
   - **Purpose:** System-weiter Font-Cache
   - **Clear:** Nur mit Admin-Rechten löschbar

### 2. **User Font Cache** 👤
   - **Location:** `%LOCALAPPDATA%\Microsoft\Windows\Fonts\*.fot`
   - **Purpose:** User-installierte Fonts
   - **Clear:** Ohne Admin-Rechte löschbar

### 3. **Windows Caches Folder** 📁
   - **Location:** `%LOCALAPPDATA%\Microsoft\Windows\Caches\*.dat`
   - **Purpose:** Allgemeine Windows Caches
   - **Clear:** Ohne Admin-Rechte löschbar

### 4. **FontCache Service Cache** ⚙️
   - **Location:** `%WINDIR%\ServiceProfiles\LocalService\AppData\Local\FontCache\`
   - **Files:** `*.dat`, `*.tmp`, `*.fot`
   - **Purpose:** Windows FontCache Service
   - **Clear:** Erfordert Admin + Service-Restart

### 5. **FontCache-S-1-5-21 Folders** 🔐
   - **Location:** `%WINDIR%\ServiceProfiles\LocalService\AppData\Local\FontCache-S-1-5-21*\`
   - **Purpose:** User-spezifische Font-Caches per SID
   - **Clear:** Erfordert Admin

### 6. **Temp Font Caches** ⏱️
   - **Location:** `%TEMP%\font*.tmp`, `*.fot`
   - **Purpose:** Temporäre Font-Daten
   - **Clear:** Meist ohne Admin

### 7. **Application Caches** 📱
   - **Chrome/Edge:** `%LOCALAPPDATA%\[Browser]\User Data\Default\Cache\`
   - **Firefox:** `%APPDATA%\Mozilla\Firefox\Profiles\*.default\cache2\`
   - **Office:** Eigene Font-Caches
   - **PDF Readers:** Adobe/Foxit haben eigene Caches

---

## 🛠️ Manuelle Cache-Clearing Methoden

### Methode 1: FontCache Service Neu Starten (Admin)

```powershell
# Als Administrator:
net stop FontCache
timeout /t 2
net start FontCache
```

### Methode 2: Cache-Dateien Manuell Löschen (Admin)

```powershell
# Als Administrator in PowerShell:

# System Cache
Remove-Item "$env:WINDIR\System32\FNTCACHE.DAT" -Force

# User Caches
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\*.fot" -Force
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Caches\*.dat" -Force

# Service Caches
Remove-Item "$env:WINDIR\ServiceProfiles\LocalService\AppData\Local\FontCache\*" -Force
Remove-Item "$env:WINDIR\ServiceProfiles\LocalService\AppData\Local\FontCache-S-1-5-21*\*" -Force

# Temp Caches
Remove-Item "$env:TEMP\font*.tmp" -Force
```

### Methode 3: WM_FONTCHANGE Broadcast (Programmatisch)

Das Python-Skript sendet automatisch `WM_FONTCHANGE` an alle Windows:

```python
import ctypes
user32 = ctypes.windll.user32
HWND_BROADCAST = 0xFFFF
WM_FONTCHANGE = 0x001D
user32.SendMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
```

### Methode 4: Browser-Caches Löschen

**Chrome/Edge:**
1. `Ctrl+Shift+Delete`
2. "Cached images and files" auswählen
3. "Clear data"
4. `Ctrl+F5` (Hard Refresh)

**Firefox:**
1. `Ctrl+Shift+Delete`
2. "Cache" auswählen
3. "Clear Now"
4. `Ctrl+F5`

---

## 🔍 Font-Version Überprüfen

### Option 1: HTML Test Page

Öffnen Sie `test-font-version.html` im Browser:
- Zeigt die geladene Font-Version
- Testet alle CJK-Zeichen
- JavaScript-Console zeigt Font-Status

### Option 2: Font-Properties in Windows

1. Rechtsklick auf `erda-ccby-cjk.ttf`
2. "Properties" → "Details" Tab
3. Suchen Sie "Product version" oder "File version"
4. Sollte Timestamp zeigen: `Version 1.0.20251104.HHMMSS`

### Option 3: Browser DevTools

1. Öffnen Sie eine Seite mit der Font
2. `F12` → "Network" Tab
3. Filter: `ttf`
4. Reload (`Ctrl+F5`)
5. Klick auf `erda-ccby-cjk.ttf`
6. "Headers" → "Response Headers" → "Last-Modified"

---

## ✅ Vollständige Troubleshooting Checkliste

Wenn die Font immer noch nicht aktualisiert wird:

- [ ] **Font neu gebaut** mit neuem Timestamp (`python build_ccby_cjk_font.py`)
- [ ] **WM_FONTCHANGE broadcast** gesendet (`--refresh-cache` flag)
- [ ] **FontCache Service** neu gestartet (als Admin)
- [ ] **Cache-Dateien gelöscht** (`clear-all-caches.ps1` als Admin)
- [ ] **Browser-Cache geleert** (`Ctrl+Shift+Delete`)
- [ ] **Alle Anwendungen geschlossen** (Browser, Office, PDF Reader)
- [ ] **Hard Refresh** in Browser (`Ctrl+F5`)
- [ ] **Windows neu gestartet** (für system-weite Änderungen)

---

## 🔬 Erweiterte Diagnostics

### Font-Version aus TTF-Datei auslesen

```bash
# Mit fontTools
python -c "from fontTools.ttLib import TTFont; font = TTFont('erda-ccby-cjk.ttf'); print(font['name'].getDebugName(5))"
```

### Alle geladenen Fonts in Browser anzeigen

```javascript
// In Browser Console (F12)
document.fonts.ready.then(() => {
    for (const font of document.fonts.values()) {
        console.log(`${font.family} - ${font.status}`);
    }
});
```

### Windows Font Registry Check

```powershell
# Prüfen Sie ob Font in Registry ist:
Get-ItemProperty "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts" | Select-String "ERDA"
```

---

## 🎓 Warum So Viele Caches?

### Performance vs. Aktualität Trade-off

1. **System Cache (FNTCACHE.DAT)**: Lädt beim Boot, sehr schnell, sehr persistent
2. **Service Caches**: FontCache Service für schnelle Font-Enumeration
3. **User Caches**: Pro-User Isolierung
4. **Application Caches**: Jede App optimiert für eigene Use-Cases
5. **Temp Caches**: Kurzlebige Font-Daten während Rendering

### Font-Versioning ist Kritisch

- Windows cached nach **Font-Name + Version + Timestamp**
- Ohne Version-Änderung wird Cache nicht invalidiert
- Deshalb fügt das Skript jetzt **Timestamp in Version** ein:
  ```
  Version 1.0.20251104.200610
            └─ YYYYMMDD.HHMMSS
  ```

---

## 📚 Weitere Ressourcen

- [Microsoft Font Cache Documentation](https://learn.microsoft.com/en-us/windows/win32/gdi/fonts-and-text)
- [WM_FONTCHANGE Message](https://learn.microsoft.com/en-us/windows/win32/gdi/wm-fontchange)
- [FontTools Documentation](https://fonttools.readthedocs.io/)

---

**Lizenz:** MIT  
**Projekt:** ERDA - European Resilient Democratic Alliance  
**Maintainer:** ERDA Development Team
