# ERDA CC BY 4.0 CJK Fallback Font

> **Font family update:** neben der bisherigen CJK-Datei gibt es jetzt zwei
> zusätzliche CC BY 4.0-Fallbacks: **ERDA CC-BY Indic** (Devanagari/Hindi) und
> **ERDA CC-BY Ethiopic** (Ge'ez). Alle Varianten teilen sich denselben
> Generator-Stack und Bitmaps.

## Übersicht

Dieser Font ist eine minimalistische CC BY 4.0-lizenzierte Fallback-Schrift für CJK-Zeichen (Chinese, Japanese, Korean), die speziell für die Lizenztext-Übersetzungen im ERDA-Buch entwickelt wurde.

**Lizenz**: CC BY 4.0 (Creative Commons Attribution 4.0 International)  
**Design**: 8×8 Pixel Monospace Bitmaps  
**Dateigröße**: CJK ~2.8 MB, Indic ~72 KB, Ethiopic ~280 KB  
**Zeichenabdeckung v2.5.0**: echte TTF-Zielpruefung via `font_cli.py stats`

---

## 📁 Verzeichnisstruktur

```
erda-ccby-cjk/
├── README.md                 # Diese Datei
│
├── generator/                # Font-Generierungs-Skripte
│   ├── build_ccby_cjk_font.py      # Haupt-Build-Skript
│   ├── build_ccby_indic_font.py    # Devanagari/Hindi Subfont
│   ├── build_ccby_ethiopic_font.py # Ethiopic Mini-Fallback
│   ├── coverage_targets.py         # v2.5.0 Release-Zielbereiche
│   ├── font_stats.py               # TTF-Statistik und Zielpruefung
│   ├── font_family_builder.py      # Gemeinsamer Bitmap-Builder
│   ├── font_version.py             # ERDA Font-Family SemVer + Buildmetadata
│   ├── font_logger.py              # Logging und Metriken
│   ├── synthetic_bitmap.py         # deterministische Coverage-Marker
│   ├── katakana.py                 # Katakana Zeichen (84)
│   ├── hiragana.py                 # Hiragana Zeichen (35)
│   ├── hangul.py                   # Hangul Jamo-Muster (11.172 Silben)
│   ├── hanzi.py                    # Hanzi/Kanji Zeichen (206)
│   ├── devanagari.py               # Devanagari/Hindi Zeichen (38)
│   ├── ethiopic.py                 # Ethiopic Mini-Satz (8+)
│   ├── punctuation.py              # Interpunktion (46)
│   └── character_index.py          # Fast O(1) lookup index
│
├── dataset/                  # Test-Daten (Lizenztext-Übersetzungen)
│   ├── japanese.md                 # Japanische Übersetzung
│   ├── korean.md                   # Koreanische Übersetzung
│   ├── chinese.md                  # Chinesische Übersetzung (traditionell + Simplified Alert)
│   ├── hindi.md                    # Hindi Zusatzdataset
│   └── ethiopic.md                 # Ethiopic Mini-Datensatz
│
├── true-type/                # Build-Output
│   ├── erda-ccby-cjk.ttf           # Generierter CJK-Font
│   ├── erda-ccby-indic.ttf         # Devanagari/Hindi Subfont
│   └── erda-ccby-ethiopic.ttf      # Ethiopic Mini-Fallback
│
├── logs/                     # Build-Logs (timestamped)
│   ├── font-build-YYYYMMDD-HHMMSS.log
│   └── BUILD-SUMMARY.md            # Zusammenfassung des letzten Builds
│
├── docs/                     # Dokumentation
│   ├── MODULAR-ARCHITECTURE.md     # Architektur-Dokumentation
│   ├── VERSIONING.md               # Eigene ERDA-Font-Versionierung
│   ├── COVERAGE-MATRIX.md          # v1.4.1 TTF-Coverage-Matrix
│   ├── FONT-CACHE-TROUBLESHOOTING.md
│   └── CODE-REVIEW-REPORT.md
│
├── scripts/                  # Hilfsskripte
│   └── clear-all-caches.ps1        # Windows Font-Cache löschen
│
└── tests/                    # Test- und Validierungs-Skripte
    ├── check_coverage.py           # Dataset-Coverage-Tool
    ├── check_hanzi_dups.py         # Duplikat-Check-Tool
    └── test-font-version.html      # HTML-Test für Font-Rendering
```

---

## 🚀 Schnellstart

### Voraussetzungen

```bash
python >= 3.11
pip install fonttools
```

### VS Code Setup (empfohlen)

Das Projekt enthält vorkonfigurierte VS Code Launch- und Task-Konfigurationen:

**Verfügbare Launch-Konfigurationen** (F5):
- `Build Font` — Standard-Build
- `Build Font (with cache refresh)` — Build + Cache-Refresh
- `Build Font (verbose)` — Build mit Debug-Output
- `Check Coverage` — Dataset-Coverage prüfen
- `Check Hanzi Duplicates` — Duplikat-Check
- `Debug Current File` — Aktuelle Datei debuggen

**Verfügbare Tasks** (Ctrl+Shift+P → "Run Task"):
- `Build Font` — Standard-Build (Default Build Task)
- `Build Font + Refresh Cache` — Build + Cache
- `Build Font + Install` — Build + Install + Cache
- `Check Coverage` — Coverage-Test
- `Check Duplicates` — Duplikat-Test
- `Run All Tests` — Alle Validierungen
- `Full Build & Test` — Complete Pipeline

**Empfohlene Extensions** werden automatisch vorgeschlagen.

### Font bauen

```bash
cd generator
python build_ccby_cjk_font.py
```

**Output**: `../true-type/erda-ccby-cjk.ttf`

### Indic/Ethiopic Subfonts bauen

```bash
python build_ccby_indic_font.py
python build_ccby_ethiopic_font.py
```

**Output**:
- `../true-type/erda-ccby-indic.ttf`
- `../true-type/erda-ccby-ethiopic.ttf`

### Alle ERDA-Fonts bauen

```bash
python build_all.py
```

### Mit Font-Cache-Refresh (empfohlen)

```bash
python build_ccby_cjk_font.py --refresh-cache
```

### Font installieren und Cache aktualisieren

```bash
python build_ccby_cjk_font.py --install --refresh-cache
```

---

## 🔧 Build-Optionen

```bash
python build_ccby_cjk_font.py [OPTIONS]

Optionen:
  -o, --output PATH      Output-Pfad (default: ../true-type/erda-ccby-cjk.ttf)
  -r, --refresh-cache    Windows Font-Cache aktualisieren
  -i, --install          Font in Windows User-Font-Verzeichnis installieren
  -v, --verbose          Verbose Output aktivieren
  -h, --help             Hilfe anzeigen
```

### Beispiele

```bash
# Custom Output-Pfad
python build_ccby_cjk_font.py --output custom-font.ttf

# Nur Cache aktualisieren
python build_ccby_cjk_font.py --refresh-cache

# Full Setup: Build + Install + Cache-Refresh
python build_ccby_cjk_font.py --install --refresh-cache
```

---

## 📊 Zeichenabdeckung

### Statistik (aktueller Build)

| Font | ERDA-Font-Version | maxp.numGlyphs | cmap-Codepoints | Release-Ziele |
|---|---|---:|---:|---|
| `erda-ccby-cjk.ttf` | 1.4.1 | 6937 | 6936 | PASS: 3242 Han, 3130 Hangul, 93 Hiragana, 96 Katakana, 141/141 long sample chars, 308/308 long-text section chars |
| `erda-ccby-indic.ttf` | 1.4.1 | 162 | 161 | PASS: 128 Devanagari main, 32 Devanagari Extended |
| `erda-ccby-ethiopic.ttf` | 1.4.1 | 525 | 524 | PASS: Ethiopic main/supplement/extended/extended-A/extended-B |

Die Statistik stammt direkt aus den TTFs:

```bash
cd generator
python font_cli.py stats --fail-on-targets
```

Wichtig: Die synthetischen Coverage-Marker sind lizenziert und sichtbar, aber
kein Ersatz fuer ein vollwertiges CJK-/Indic-/Ethiopic-Schriftdesign.

### Unterstützte Zeichenbereiche

- **Katakana**: U+30A0 - U+30FF (vollstaendige zugeordnete Standardblock-Ziele)
- **Hiragana**: U+3040 - U+309F (vollstaendige zugeordnete Standardblock-Ziele)
- **Hangul**: U+AC00 - U+D7A3 (gestuftes 3000+-Ziel im CJK-Font)
- **CJK Unified Ideographs**: U+4E00 - U+9FFF (gestuftes 3000+-Ziel im CJK-Font)
- **Devanagari**: U+0900 - U+097F und U+A8E0 - U+A8FF (vollstaendige zugeordnete Blockziele)
- **Ethiopic**: U+1200 - U+137F, U+1380 - U+139F, U+2D80 - U+2DDF, U+AB00 - U+AB2F, U+1E7E0 - U+1E7FF
- **Interpunktion**: CJK-Symbole/Interpunktion und Fullwidth-Formen

---

## 🧪 Validierung

### Coverage-Check

```bash
cd tests
python check_coverage.py
```

**Expected Output**:
```
Total unique dataset chars: 363
Covered characters: 363
Missing characters: 0
```

### Duplikat-Check

```bash
cd tests
python check_hanzi_dups.py
```

**Expected Output**:
```
Total characters in HANZI_KANJI: 137
No duplicate keys found - dictionary is clean!
```

---

## 🏗️ Architektur

### Modularer Aufbau

Alle Zeichen-Daten sind in separate Module aufgeteilt:

- **`katakana.py`**: Katakana Base + Varianten
- **`hiragana.py`**: Hiragana Zeichen (8×8 Bitmaps)
- **`hangul.py`**: Jamo-Muster + Silben-Generator
- **`hanzi.py`**: Hanzi/Kanji (handgefertigte Bitmaps)
- **`punctuation.py`**: CJK Interpunktion

### 8×8 Bitmap-Design

Jedes Zeichen ist als 8-Zeilen-Liste definiert:

```python
"本": [  # book/origin
    "...#....",
    "########",
    "...#....",
    "########",
    "..#.#...",
    ".#...#..",
    "#.....#.",
    "#.....#.",
]
```

- `#` = Pixel an
- `.` = Pixel aus

### Build-Prozess

1. **Character Collection**: Sammelt Zeichen aus Translation-Strings
2. **Module Import**: Lädt Zeichen-Daten aus Modulen
3. **Glyph Generation**: Konvertiert Bitmaps zu TrueType-Glyphen
4. **Font Assembly**: Baut Font-Tables (cmap, glyf, head, etc.)
5. **Output**: Schreibt TTF-Datei nach `../true-type/`
6. **Logging**: Erstellt timestamped Log in `../logs/`

---

## 📝 Logging

Jeder Build erzeugt ein detailliertes Log:

**Pfad**: `logs/font-build-YYYYMMDD-HHMMSS.log`

**Inhalt**:
- Build-Start/End-Zeit
- Zeichen-Quellen (katakana, hangul, hanzi, etc.)
- Metriken (processed/generated)
- Fehler/Warnungen

**Beispiel**:
```
2025-11-05 17:44:33 | INFO | ERDA CC-BY CJK Font Build Started
2025-11-05 17:44:33 | INFO | Required characters: 303
2025-11-05 17:44:33 | INFO | FONT BUILD COMPLETED SUCCESSFULLY
2025-11-05 17:44:33 | INFO | Build time: 0.11 seconds
2025-11-05 17:44:33 | INFO | CHARACTER SOURCES:
2025-11-05 17:44:33 | INFO |   hanzi       :  137 ( 45.2%)
2025-11-05 17:44:33 | INFO |   hangul      :   91 ( 30.0%)
```

---

## 🔒 Lizenzierung

### Font-Glyphen

**CC BY 4.0** (Creative Commons Attribution 4.0 International)

Alle 8×8 Bitmap-Glyphen sind Originalwerke und unter CC BY 4.0 lizenziert.

**Verwendung**:
- ✅ Kommerzielle Nutzung erlaubt
- ✅ Modifikation erlaubt
- ✅ Weitergabe erlaubt
- ⚠️ **Namensnennung erforderlich**

### Code (Generator-Skripte)

**MIT License**

Alle Python-Skripte und Build-Tools sind unter MIT lizenziert.

### Referenzen

- `../../LICENSE` — CC BY-SA 4.0 (Buchinhalte)
- `../../LICENSE-CODE` — MIT (Code/Skripte)
- `../../LICENSE-FONTS` — CC BY 4.0 (Fonts)
- `../../ATTRIBUTION.md` — Vollständige Attributions

---

## 🛠️ Wartung

### Neue Zeichen hinzufügen

#### 1. Hiragana/Katakana

Datei: `generator/hiragana.py` oder `generator/katakana.py`

```python
HIRAGANA = {
    "あ": [
        "..####..",
        ".#....#.",
        # ... 8 Zeilen
    ],
}
```

#### 2. Hanzi/Kanji

Datei: `generator/hanzi.py`

```python
HANZI_KANJI = {
    "新": [
        "########",
        "#......#",
        # ... 8 Zeilen
    ],
}
```

#### 3. Devanagari (Hindi)

Datei: `generator/devanagari.py`

```python
DEVANAGARI = {
    "ह": [  # ha
        "########",
        "#......#",
        # ... 8 Zeilen
    ],
}
```

#### 4. Interpunktion

Datei: `generator/punctuation.py`

```python
PUNCTUATION = {
    "！": [
        "...#....",
        "...#....",
        # ... 8 Zeilen
    ],
}
```

### Nach Änderungen

```bash
# 1. Font neu bauen
cd generator
python build_ccby_cjk_font.py

# 2. Coverage prüfen
cd ../tests
python check_coverage.py

# 3. Duplikate prüfen
python check_hanzi_dups.py
```

---

## ⚠️ Troubleshooting

### Problem: Font wird nicht aktualisiert

**Lösung**: Windows Font-Cache löschen

```powershell
# PowerShell als Administrator
cd scripts
.\clear-all-caches.ps1
```

Siehe auch: [`docs/FONT-CACHE-TROUBLESHOOTING.md`](docs/FONT-CACHE-TROUBLESHOOTING.md)

### Problem: Zeichen fehlen im PDF

1. Coverage prüfen: `cd tests && python check_coverage.py`
2. Fehlende Zeichen zu entsprechendem Modul hinzufügen
3. Font neu bauen: `cd ../generator && python build_ccby_cjk_font.py`
4. PDF-Build erneut ausführen

### Problem: Build-Fehler

```bash
# Verbose Mode aktivieren
python build_ccby_cjk_font.py --verbose

# Log-Datei prüfen
cat ../logs/font-build-*.log | tail -50
```

---

## 📚 Weitere Dokumentation

- **Architektur**: [`docs/MODULAR-ARCHITECTURE.md`](docs/MODULAR-ARCHITECTURE.md)
- **Cache-Troubleshooting**: [`docs/FONT-CACHE-TROUBLESHOOTING.md`](docs/FONT-CACHE-TROUBLESHOOTING.md)
- **Code-Review**: [`docs/CODE-REVIEW-REPORT.md`](docs/CODE-REVIEW-REPORT.md)
- **Build-Summary**: [`logs/BUILD-SUMMARY.md`](logs/BUILD-SUMMARY.md)

---

## 🎯 Qualitätssicherung

- [x] 543 Zeichen (Katakana, Hiragana, Hangul, Hanzi, Devanagari, Interpunktion)
- [x] Devanagari/Hindi-Unterstützung (38 Zeichen)
- [x] Keine Duplikate in Zeichen-Dictionaries
- [x] Modulare Architektur (Separation of Concerns)
- [x] Fast O(1) Character Index für effiziente Lookups
- [x] Timestamped Logging mit Metriken
- [x] Automatisierte Validierungs-Tools
- [x] CC BY 4.0 Lizenz-Compliance

---

## 👥 Verwendung im ERDA-Buch

Der Font wird als Fallback für CJK-Zeichen in GitBook PDF-Exporten verwendet:

1. **Ziel**: Anhang J.8 (Lizenz-Übersetzungen) korrekt darstellen
2. **Sprachen**: Japanisch, Koreanisch, Chinesisch (Traditionell), Hindi
3. **Integration**: Über GitBook Font-Konfiguration
4. **Validierung**: PDF-Probelauf zeigt korrekte Darstellung

---

**Letzte Aktualisierung**: 2026-05-07  
**Font-Version**: 1.4.1  
**Build**: v1.4.1 Coverage-Build  
**Status**: ✅ Production Ready (mit CJK/Indic/Ethiopic Coverage-Gate)
