# ERDA CJK Font - Verzeichnisstruktur

## 📁 Übersicht

```
.github/fonts/
│
├── 📄 README.md                    # Hauptdokumentation
├── 🔨 build_ccby_cjk_font.py      # Font-Builder (Hauptskript)
├── 🔤 erda-ccby-cjk.ttf           # Finale Font-Datei (CC BY 4.0)
│
├── 📚 docs/                        # Dokumentation
│   ├── README-fonts.md            # Ausführliche Font-Dokumentation
│   ├── LICENSE.txt                # CC BY 4.0 Lizenztext
│   ├── CODE-REVIEW-REPORT.md      # Code-Review-Bericht
│   └── FONT-CACHE-TROUBLESHOOTING.md  # Cache-Problem-Lösungen
│
├── 📜 scripts/                     # Hilfsskripte
│   ├── README.md                  # Script-Dokumentation
│   ├── clear-all-caches.ps1       # Windows Font-Cache löschen (Admin)
│   └── test-admin-cache-refresh.ps1  # Cache-Refresh testen (Admin)
│
├── 🧪 tests/                       # Test-Suite
│   ├── README.md                  # Test-Dokumentation
│   ├── test_chars.py              # Testet Zeichen in Font
│   ├── test_dict.py               # Testet HANZI_KANJI Dictionary
│   ├── debug_chars.py             # Debug-Tool für Zeichen
│   ├── check_translation.py       # Prüft Translation-Strings
│   └── test-font-version.html     # Browser-Test für Font
│
└── 🏗️ build/                       # Build-Artefakte (nicht versioniert)
    ├── .gitignore                 # Ignoriert Build-Artefakte
    ├── erda-ccby-cjk-test.ttf    # Test-Versionen
    └── __pycache__/               # Python Bytecode-Cache
```

## 🎯 Verwendungszweck der Verzeichnisse

### Root (`/`)
- **Hauptdateien** die direkt benötigt werden
- Font-Builder-Script
- Finale Font-Datei

### `docs/`
- Alle **Dokumentation** und **Lizenz-Dateien**
- README, Troubleshooting-Guides
- Code-Review-Berichte

### `scripts/`
- **Hilfsskripte** für Wartung und Testing
- Cache-Management
- Admin-Tools

### `tests/`
- **Test-Suite** für Font-Qualität
- Unit-Tests für Zeichen
- Debug-Tools
- Browser-Tests

### `build/`
- **Temporäre Dateien** und Build-Artefakte
- Test-Versionen der Font
- Python-Cache
- **Wird nicht versioniert** (.gitignore)

## 🔄 Workflow

### 1. Font entwickeln
```bash
# Zeichen zu HANZI_KANJI hinzufügen
vim build_ccby_cjk_font.py

# Font bauen
python build_ccby_cjk_font.py --output erda-ccby-cjk.ttf
```

### 2. Testen
```bash
# Tests ausführen
cd tests
python test_chars.py    # Prüft Zeichen
python test_dict.py     # Prüft Dictionary
```

### 3. Cache refreshen
```bash
# Windows (als Admin)
cd scripts
.\clear-all-caches.ps1
```

### 4. Integrieren
```yaml
# In publish.yml referenzieren
fonts:
  - name: ERDA CC-BY CJK
    path: .github/fonts/erda-ccby-cjk.ttf
```

## 📦 Git-Versionierung

**Versioniert:**
- ✅ `build_ccby_cjk_font.py` (Source)
- ✅ `erda-ccby-cjk.ttf` (Binary)
- ✅ `docs/` (Dokumentation)
- ✅ `scripts/` (Hilfsskripte)
- ✅ `tests/` (Tests)

**Nicht versioniert:**
- ❌ `build/` (Build-Artefakte)
- ❌ `__pycache__/` (Python-Cache)
- ❌ `*-test.ttf` (Test-Fonts)

## 🛡️ Best Practices

1. **Font-Änderungen** → Immer Tests ausführen
2. **Neue Zeichen** → Dictionary updaten, dann bauen
3. **Cache-Probleme** → Scripts in `scripts/` verwenden
4. **Dokumentation** → In `docs/` ablegen
5. **Tests** → In `tests/` mit relativen Pfaden

## 📝 Konventionen

### Dateinamen
- Scripts: `kebab-case.ps1` oder `snake_case.py`
- Docs: `UPPERCASE.md` oder `kebab-case.md`
- Tests: `test_*.py` oder `*_test.py`

### Kommentare
- **Deutsch** in Scripts (außer Code-Kommentare)
- **Englisch** in Python-Docstrings
- **Emoji** für visuelle Orientierung in README

### Versionierung
- Font-Version: `Version 1.0.YYYYMMDD.HHMMSS` (automatisch)
- Git-Tags: `v1.0.0` für Releases
- Semantic Versioning für Breaking Changes
