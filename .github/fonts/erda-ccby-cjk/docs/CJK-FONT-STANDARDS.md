# CJK Font Standards & Best Practices
**Version:** 1.0  
**Datum:** 08. November 2025  
**Zweck:** Referenz für CJK-Font-Entwicklung

---

## 1. CJK Font-Formate: Industry Standards

### 1.1 Grid-Größen (Bitmap-Fonts)

| Grid | Auflösung | Use Case | Beispiele | Bewertung ERDA |
|------|-----------|----------|-----------|----------------|
| **8×8** | 64 px² | Terminal, Retro | GNU Unifont | ✅ Aktuell |
| **12×12** | 144 px² | Code-Editor | Terminus | 🟡 Nützlich |
| **16×16** | 256 px² | Standard-Text | SimSun Bitmap | ✅ Empfohlen |
| **24×24** | 576 px² | High-DPI | MS Gothic | 🟢 Optional |
| **32×32** | 1024 px² | Large Display | Custom | ⚪ Nicht nötig |

#### Vergleich: Lesbarkeit nach Grid-Größe

```
8×8 Beispiel (本):
  ...#....
  ########
  ...#....
  ########
  ...#....
  ..###...
  .#.#.#..
  #..#..#.

Bewertung: ⚠️ Minimal erkennbar, nur für einfache Zeichen

16×16 Beispiel (本):
  ......####......
  .....######.....
  ................
  ################
  ................
  ......####......
  ......####......
  ################
  ................
  .....######.....
  ....########....
  ...##....##.....
  ..##......##....
  .##........##...
  ##..........##..
  ................

Bewertung: ✅ Klar erkennbar, ausreichend für normalen Text
```

**Empfehlung für ERDA:**
- **Primär:** 16×16 (beste Balance Qualität/Größe)
- **Sekundär:** 8×8 (Kompatibilität, Retro)
- **Optional:** 24×24 (High-DPI-Displays)

---

### 1.2 Monospace vs. Proportional

#### Monospace (Fixed-Width)

**Eigenschaften:**
- Alle Glyphen haben gleiche Breite
- CJK-Zeichen: Typisch 1em (quadratisch)
- ASCII: Typisch 0.5em (Halbbreite)

**Vorteile:**
```
✅ Einfache Implementierung
✅ Terminal-freundlich
✅ Tabellen-Layout perfekt
✅ Code-Editor-geeignet
```

**Nachteile:**
```
⚠️ Verschwendeter Platz bei schmalen Zeichen
⚠️ Unnatürlicher Text-Flow
⚠️ Größere Font-Files
```

**Beispiel:**
```
Monospace (8×8 Grid):
"i" nimmt gleich viel Platz wie "m"
│i│m│
└─┴─┘
8×8 8×8
```

#### Proportional (Variable-Width)

**Eigenschaften:**
- Glyphen haben individuelle Breiten
- Optimierte Platznutzung
- Natürlicherer Text-Flow

**Typical Width Ratios:**
```
CJK Ideographs:  1.0em (1000 units)
Latin Capital:   0.7em (700 units)
Latin Lowercase: 0.6em (600 units)
Narrow (i,l,1):  0.3em (300 units)
```

**Beispiel:**
```
Proportional:
"i" ist schmaler als "m"
│i│m  │
└┘└───┘
300  700
```

**Empfehlung für ERDA:**
- **Phase 1:** Monospace (einfacher Start)
- **Phase 2:** Proportional für ASCII
- **Phase 3:** Vollständig proportional

---

### 1.3 TrueType Hinting

#### Was ist Hinting?

Hinting = Anweisungen für Rasterizer, wie Glyphen bei verschiedenen Größen gerendert werden sollen.

**Ohne Hinting (12px):**
```
本 → ⬛⬛⬛⬛ (verschwommen)
     ⬛  ⬛
     ⬛⬛⬛⬛
```

**Mit Hinting (12px):**
```
本 → ████ (scharf)
     █  █
     ████
```

#### Hinting-Typen

##### 1. Autohinting (FreeType)
```python
# Automatisch, keine manuelle Arbeit
# Qualität: 70-80%
```

##### 2. TrueType Instructions
```python
# Manuell programmiert
# Qualität: 95%+
# Aufwand: Sehr hoch

fb.setupGasp({
    8: 2,    # Grid-fitting
    16: 7,   # Grid-fitting + Smoothing
    65535: 7
})
```

##### 3. PostScript Hints
```python
# Für Type 1/CFF Fonts
# Nicht relevant für TrueType
```

**Empfehlung für ERDA:**
- **Phase 1:** Kein Hinting (Bitmap-Font funktioniert ohne)
- **Phase 2:** Basic GASP-Table
- **Phase 3:** Erweiterte TrueType-Instructions

---

## 2. Character-Coverage: Standards & Best Practices

### 2.1 Unicode-Blöcke (CJK-Relevant)

| Block | Range | Chars | Status ERDA | Priorität |
|-------|-------|-------|-------------|-----------|
| **Basic Latin** | U+0000-007F | 128 | ⚠️ Teilweise | P0 |
| **Latin-1 Supplement** | U+0080-00FF | 128 | ❌ Fehlt | P1 |
| **CJK Symbols & Punct** | U+3000-303F | 64 | ⚠️ Teilweise | P0 |
| **Hiragana** | U+3040-309F | 96 | ⚠️ 27/96 | P0 |
| **Katakana** | U+30A0-30FF | 96 | ⚠️ 27/96 | P0 |
| **Hangul Compatibility** | U+3130-318F | 96 | ❌ Fehlt | P2 |
| **CJK Unified (Ext A)** | U+3400-4DBF | 6.592 | ❌ Fehlt | P3 |
| **CJK Unified** | U+4E00-9FFF | 20.992 | ⚠️ 137 | P1 |
| **Hangul Syllables** | U+AC00-D7AF | 11.172 | ✅ Algo | P1 |
| **CJK Compatibility** | U+F900-FAFF | 512 | ❌ Fehlt | P2 |
| **Halfwidth Forms** | U+FF00-FFEF | 240 | ❌ Fehlt | P2 |

**Totale CJK-Coverage (vollständig):** ~40.000 Zeichen  
**Minimale Produktions-Coverage:** ~5.000 Zeichen  
**ERDA Aktuell:** ~300 Zeichen

---

### 2.2 Frequency-Based Coverage (Empfehlung)

#### Chinesisch (Simplified/Traditional)

##### Option A: HSK (Hanyu Shuiping Kaoshi)
```
HSK 1: 150 Zeichen   (Anfänger)
HSK 2: 300 Zeichen   (Grundstufe)
HSK 3: 600 Zeichen   (Mittelstufe)
HSK 4: 1.200 Zeichen (Obere Mittelstufe)
HSK 5: 2.500 Zeichen (Fortgeschritten)
HSK 6: 5.000 Zeichen (Sehr fortgeschritten)
```

**Coverage-Effekt:**
- HSK 1-3 (600 chars): ~75% Alltagstexte
- HSK 1-4 (1.200 chars): ~90% Zeitungen
- HSK 1-6 (5.000 chars): ~99% Literatur

##### Option B: GB 2312 (China Standard)
```
Level 1: 3.755 häufigste Zeichen (99.9% Coverage)
Level 2: 3.008 seltene Zeichen
Total: 6.763 Zeichen
```

##### Option C: Big5 (Taiwan)
```
Level 1: 5.401 häufige Zeichen
Level 2: 7.652 seltene Zeichen
Total: 13.053 Zeichen (Traditional Chinese)
```

**Empfehlung für ERDA:**
```
Phase 1: Top 500 (HSK 1-3 + häufigste)
Phase 2: Top 1.500 (HSK 1-4)
Phase 3: Top 5.000 (HSK 1-6 oder GB 2312 Level 1)
```

#### Japanisch (Kanji)

##### Jōyō Kanji (常用漢字)
```
2.136 Kanji (Schul-Pflicht in Japan)
→ Alle Zeitungen, Behörden, Schulbücher
→ 95%+ Coverage japanischer Texte
```

##### Jinmeiyō Kanji (人名用漢字)
```
863 zusätzliche Kanji (für Namen)
→ Total: 2.999 Kanji
```

##### Frequency-Based
```
Top 500: ~80% Coverage
Top 1.000: ~90% Coverage
Top 2.000: ~95% Coverage
Jōyō (2.136): ~95%+ Coverage
```

**Empfehlung für ERDA:**
```
Phase 1: Top 500 häufigste Kanji
Phase 2: Top 1.500 (inkl. häufige Namen)
Phase 3: Jōyō Kanji (2.136)
```

#### Koreanisch (Hangul)

##### Häufigkeit
```
Top 100 Silben: ~50% aller Texte
Top 500 Silben: ~80% aller Texte
Top 1.000 Silben: ~90% aller Texte
Top 2.000 Silben: ~95% aller Texte
Alle 11.172: 100% (aber viele quasi ungenutzt)
```

##### KS X 1001 (Korea Standard)
```
2.350 häufigste Hangul-Silben
→ 90%+ Coverage koreanischer Texte
```

**Besonderheit:** ERDA hat bereits algorithmische Generierung aller 11.172 Silben ✅

**Empfehlung:**
```
✅ Aktuell: Alle 11.172 (algorithmisch) → beibehalten
Optional: Pre-compute Top 1.000 für bessere Qualität
```

---

### 2.3 Industry-Standard Character-Sets

#### Pan-CJK Fonts (Beispiele)

##### Noto Sans CJK
```
Total: ~65.000 Glyphen
├── CJK Unified: 20.992
├── CJK Ext. A: 6.592
├── CJK Ext. B-G: ~30.000
├── Hiragana: 93
├── Katakana: 96
├── Hangul: 11.172
└── Latin/Symbols: ~5.000
```

##### Source Han Sans
```
Total: ~65.000 Glyphen (identisch zu Noto)
Regional Variants: 4 (JP, CN, TW, KR)
```

##### Microsoft YaHei (雅黑)
```
Total: ~35.000 Glyphen
Focus: Simplified Chinese
```

**Realistische Ziele für ERDA:**
```
Minimal:  1.000 Glyphen (Lizenztext + Basic)
Standard: 5.000 Glyphen (Produktionsreif)
Extended: 10.000 Glyphen (Comprehensive)
```

---

## 3. Technische Standards

### 3.1 OpenType Features

#### Empfohlene Features für CJK

```python
# features.fea (OpenType Feature File)

# GSUB (Glyph Substitution)
feature vert {
    # Vertical Writing (wichtig für Japanisch)
    sub uni3001 by uni3001.vert;  # Komma
    sub uni3002 by uni3002.vert;  # Punkt
} vert;

feature vrt2 {
    # Vertical Writing (erweitert)
    # ...
} vrt2;

feature locl {
    # Locale-specific forms
    script hani;
    language JAN;  # Japanisch
    sub uni9AA8 by uni9AA8.jp;  # 骨 (japan. Variante)
    
    language CHN;  # Chinesisch
    sub uni9AA8 by uni9AA8.cn;  # 骨 (chin. Variante)
} locl;

# GPOS (Glyph Positioning)
feature kern {
    # Kerning für Latin
    pos A V -50;
    pos T o -30;
} kern;
```

**Empfehlung für ERDA:**
- **Phase 1:** Keine Features (nicht erforderlich für Bitmap)
- **Phase 2:** `vert` für vertikale Schreibrichtung
- **Phase 3:** `locl` für regionale Varianten

---

### 3.2 Font Tables (TrueType)

#### Mandatory Tables

| Table | Beschreibung | ERDA Status |
|-------|-------------|-------------|
| `cmap` | Character-to-Glyph-Mapping | ✅ |
| `glyf` | Glyph-Daten (Konturen) | ✅ |
| `head` | Font-Header | ✅ |
| `hhea` | Horizontal-Header | ✅ |
| `hmtx` | Horizontal-Metriken | ✅ |
| `maxp` | Maximum-Profile | ✅ |
| `name` | Font-Namen | ✅ |
| `post` | PostScript-Informationen | ✅ |

#### Optional aber empfohlen

| Table | Beschreibung | ERDA Status | Priorität |
|-------|-------------|-------------|-----------|
| `OS/2` | OS/2 & Windows-Metriken | ✅ | P0 |
| `gasp` | Grid-fitting & Anti-Aliasing | ❌ | P1 |
| `GPOS` | Glyph-Positionierung | ❌ | P2 |
| `GSUB` | Glyph-Substitution | ❌ | P2 |
| `cvt ` | Control-Value-Table | ❌ | P2 |
| `prep` | Pre-Program (Hinting) | ❌ | P2 |
| `VORG` | Vertical-Origin | ❌ | P3 |

---

### 3.3 Encoding & Unicode

#### cmap-Formate

```python
# Format 4: BMP (U+0000-FFFF)
# → Standard für CJK Basic
cmap_format_4 = {
    0x4E00: "uni4E00",  # 一
    0x672C: "uni672C",  # 本
    # ...
}

# Format 12: Full Unicode (U+0000-10FFFF)
# → Für CJK Extensions
cmap_format_12 = {
    0x20000: "uni20000",  # 𠀀 (Ext. B)
    # ...
}
```

**Empfehlung für ERDA:**
- **Aktuell:** Format 4 (BMP) ✅
- **Future:** Format 12 für Extensions

---

## 4. Beste Formate für ERDA

### 4.1 Empfohlene Grid-Größen

#### Priorität 1: 16×16 (Standard)
```
Begründung:
✅ Beste Balance: Qualität vs. Dateigröße
✅ Klar lesbar bei 12-16pt
✅ Ausreichend Details für CJK-Striche
✅ Industry-Standard für Bitmap-CJK

Zielgruppe:
- Normale Dokumente
- PDF-Export
- Web-Rendering (mit @font-face)

Dateigröße: ~200-300 KB (5.000 Glyphen)
```

#### Priorität 2: 8×8 (Retro/Terminal)
```
Begründung:
✅ Bereits implementiert
✅ Minimale Dateigröße (~90 KB)
✅ Terminal-geeignet
✅ Retro-Ästhetik

Zielgruppe:
- Terminal-Emulators
- Retro-Systeme
- Eingebettete Systeme (Low-Memory)

Use-Case: Beibehalten als "Classic"-Variante
```

#### Priorität 3: 24×24 (High-DPI)
```
Begründung:
✅ Sehr hohe Qualität
✅ Gut für 4K/5K-Displays
⚠️ Größere Dateigröße (~500 KB)

Zielgruppe:
- High-DPI-Displays
- Druck-Qualität
- Premium-Anwendungen

Use-Case: Optional für "Pro"-Variante
```

---

### 4.2 Empfohlene Character-Sets

#### Minimal Set (1.000 Glyphen)
```
✅ Vollständige Hiragana (93)
✅ Vollständige Katakana (96)
✅ Top 500 Hanzi (GB 2312 Level 1)
✅ Top 200 Hangul (häufigste Silben)
✅ Basic Latin (128)
✅ CJK Symbols & Punctuation (64)
✅ Zusätzliche Interpunktion (~119)

Total: ~1.000 Zeichen
Dateigröße (16×16): ~150 KB
Coverage: 80-90% Lizenztext + Basic-Dokumente
```

#### Standard Set (5.000 Glyphen)
```
✅ Minimal Set (1.000)
✅ Top 3.000 Hanzi (GB 2312 Level 1)
✅ Top 1.000 Hangul (KS X 1001)
✅ Latin-1 Supplement (128)
✅ CJK Compatibility (100)
✅ Fullwidth Forms (240)

Total: ~5.000 Zeichen
Dateigröße (16×16): ~300 KB
Coverage: 95%+ allgemeine Dokumente
```

#### Extended Set (10.000+ Glyphen)
```
✅ Standard Set (5.000)
✅ Jōyō Kanji komplett (2.136)
✅ GB 2312 komplett (6.763)
✅ Alle Hangul-Silben (11.172)
✅ CJK Extension A (teilweise)

Total: ~10.000-15.000 Zeichen
Dateigröße (16×16): ~600-800 KB
Coverage: 99%+ professionelle Anwendungen
```

---

### 4.3 Spezifische Empfehlungen für ERDA

#### Phase 1: Foundation (Q4 2025)
```
Format:
├── 8×8 Monospace (beibehalten)
└── 16×16 Monospace (neu)

Coverage:
├── Vollständige Hiragana/Katakana
├── Top 500 Hanzi
├── Top 200 Hangul
└── Basic Latin + CJK Symbols

Ziel: 1.000 Glyphen
Build-Zeit: <0.05s (8×8), <0.10s (16×16)
```

#### Phase 2: Production (Q1 2026)
```
Format:
├── 8×8 Monospace
├── 16×16 Monospace
└── 16×16 Proportional (neu)

Coverage:
├── Phase 1 (1.000)
└── +4.000 Top Hanzi/Hangul

Ziel: 5.000 Glyphen
Build-Zeit: <0.20s (alle Formate)
```

#### Phase 3: Professional (Q2 2026)
```
Format:
├── 8×8 Monospace
├── 16×16 Monospace
├── 16×16 Proportional
├── 24×24 Monospace (neu)
└── 24×24 Proportional (neu)

Coverage:
├── Phase 2 (5.000)
├── Jōyō Kanji komplett
├── GB 2312 komplett
└── Alle Hangul (11.172)

Ziel: 15.000+ Glyphen
Build-Zeit: <0.50s (Cache aktiviert)
```

---

## 5. Häufigste CJK-Zeichen (Top 5.000)

### 5.1 Top 100 Hanzi (nach Häufigkeit)

#### Häufigkeitsklasse 1 (1-20)
```
的 一 是 在 不 了 有 和 人 这
中 大 为 上 个 国 我 以 要 他
```

**Bedeutung:** Diese 20 Zeichen machen ~10% aller chinesischen Texte aus.

#### Häufigkeitsklasse 2 (21-50)
```
时 来 用 们 生 到 作 地 于 出
就 分 对 成 会 可 主 发 年 动
同 工 也 能 下 过 子 说 产 种
```

#### Häufigkeitsklasse 3 (51-100)
```
面 而 方 后 多 定 行 学 法 所
民 得 经 十 三 之 进 着 等 部
度 家 电 力 里 如 水 化 高 自
二 理 起 小 物 现 实 加 量 都
两 体 制 机 当 使 点 从 业 本
```

**Coverage-Effekt:**
- Top 100: ~30% aller Texte
- Top 500: ~75% aller Texte
- Top 1.000: ~85% aller Texte
- Top 2.000: ~95% aller Texte
- Top 5.000: ~99% aller Texte

---

### 5.2 Vollständige Kana-Listen

#### Hiragana (93 Zeichen)

##### Basic Hiragana (46)
```
あ い う え お
か き く け こ
さ し す せ そ
た ち つ て と
な に ぬ ね の
は ひ ふ へ ほ
ま み む め も
や    ゆ    よ
ら り る れ ろ
わ          を
ん
```

##### Dakuten/Handakuten (25)
```
が ぎ ぐ げ ご
ざ じ ず ぜ ぞ
だ ぢ づ で ど
ば び ぶ べ ぼ
ぱ ぴ ぷ ぺ ぽ
```

##### Kleine Kana (6)
```
ぁ ぃ ぅ ぇ ぉ
ゃ ゅ ょ
```

##### Kombinationen (Yōon) (33)
```
きゃ きゅ きょ
しゃ しゅ しょ
ちゃ ちゅ ちょ
にゃ にゅ にょ
ひゃ ひゅ ひょ
みゃ みゅ みょ
りゃ りゅ りょ
ぎゃ ぎゅ ぎょ
じゃ じゅ じょ
びゃ びゅ びょ
ぴゃ ぴゅ ぴょ
```

##### Obsolet (3)
```
ゐ ゑ ゔ
```

**Total: 93 Zeichen**

#### Katakana (96 Zeichen)
Analog zu Hiragana, plus:
```
・ (Nakaten: Trennzeichen)
ー (Chōonpu: Längungszeichen)
ヴ (vu-Sound für Fremdwörter)
```

**Total: 96 Zeichen**

---

### 5.3 Häufigste Hangul-Silben

#### Top 20 Hangul
```
이 가 의 에 은 을 한 는 으 로
있 그 하 기 도 다 를 어 이 들
```

**Coverage:** ~25% aller koreanischen Texte

#### Top 100 Hangul
```
(siehe KS X 1001 Frequency Table)
```

**Coverage:** ~50% aller koreanischen Texte

#### Top 1.000 Hangul
```
(siehe KS X 1001 Standard)
```

**Coverage:** ~90% aller koreanischen Texte

**Empfehlung:**
- ERDA hat bereits alle 11.172 Silben (algorithmisch) ✅
- Optional: Pre-compute Top 1.000 mit manuellen Bitmaps für bessere Qualität

---

## 6. Tools & Resources

### 6.1 Character-Frequency-Datenbanken

#### Chinesisch
- **Jun Da's Frequency List**: http://lingua.mtsu.edu/chinese-computing/statistics/
- **HSK Official**: http://www.chinesetest.cn/
- **GB 2312 Standard**: Chinese National Standard

#### Japanisch
- **Jōyō Kanji List**: https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/
- **Frequency Data**: BCCWJ (Balanced Corpus of Contemporary Written Japanese)

#### Koreanisch
- **KS X 1001**: Korean Industrial Standard
- **Sejong Corpus**: National Institute of Korean Language

---

### 6.2 Bitmap-Design-Tools

```
1. FontForge (Open-Source)
   → GUI für Font-Editing
   → Bitmap-Import

2. BDF (Bitmap Distribution Format)
   → Text-basiertes Bitmap-Format
   → Einfach zu editieren

3. GNU Unifont Hex
   → Hex-basiertes Format
   → Skript-freundlich

4. Custom Python-Tools
   → ASCII-Art zu Bitmap
   → Template-Generatoren
```

---

### 6.3 Testing & Validation

```python
# Font-Validierung
from fontTools.ttLib import TTFont

def validate_cjk_font(font_path: str):
    font = TTFont(font_path)
    
    # Check required tables
    required = ["cmap", "glyf", "head", "hhea", "hmtx", "maxp", "name", "post"]
    for table in required:
        assert table in font, f"Missing table: {table}"
    
    # Check CJK coverage
    cmap = font.getBestCmap()
    cjk_count = sum(1 for code in cmap if 0x4E00 <= code <= 0x9FFF)
    print(f"CJK Unified Ideographs: {cjk_count}")
    
    # Check Kana coverage
    hiragana_count = sum(1 for code in cmap if 0x3040 <= code <= 0x309F)
    katakana_count = sum(1 for code in cmap if 0x30A0 <= code <= 0x30FF)
    print(f"Hiragana: {hiragana_count}/93")
    print(f"Katakana: {katakana_count}/96")
```

---

## 7. Zusammenfassung & Empfehlungen

### ✅ Sollte ERDA implementieren

1. **16×16 Grid-Format** (Priorität 1)
   - Beste Balance: Qualität vs. Dateigröße
   - Industry-Standard für Bitmap-CJK
   - Klar lesbar bei normalen Schriftgrößen

2. **Top 500-1.000 Hanzi** (Priorität 1)
   - 75-85% Coverage chinesischer/japanischer Texte
   - Ausreichend für Lizenztexte + normale Dokumente
   - Machbarer Aufwand (~40 Stunden)

3. **Vollständige Kana** (Priorität 1)
   - Hiragana: 27 → 93 Zeichen
   - Katakana: 27 → 96 Zeichen
   - Essentiell für japanische Texte
   - Geringer Aufwand (~12 Stunden)

4. **Character-Index-System** (Priorität 1)
   - 50% Performance-Boost
   - Bessere Wartbarkeit
   - Basis für Erweiterungen

5. **Config-System** (Priorität 1)
   - Flexible Grid-Größen
   - Einfache Character-Set-Anpassung
   - Mehrere Build-Profile

### 🟡 Optional, aber nützlich

1. **24×24 Grid-Format** (Priorität 2)
   - High-DPI-Qualität
   - Druck-geeignet
   - Größere Dateien (~500 KB)

2. **Proportional-Font-Variante** (Priorität 2)
   - Natürlicherer Text-Flow
   - Bessere Lesbarkeit bei Latin-Text
   - Höherer Implementierungs-Aufwand

3. **Top 5.000 Hanzi** (Priorität 2)
   - 99% Coverage
   - Professionelle Anwendungen
   - Sehr hoher Aufwand (~200 Stunden)

4. **Glyph-Cache-System** (Priorität 2)
   - Schnellere Builds (80%+ Cache-Hits)
   - Nützlich bei vielen Builds
   - Moderate Komplexität

### ⚪ Nicht prioritär

1. **CJK Extension A/B/C** (Priorität 3)
   - Seltene Zeichen
   - Hoher Aufwand
   - Niedrige Coverage-Verbesserung

2. **OpenType Features** (Priorität 3)
   - Nicht essentiell für Bitmap-Fonts
   - Nützlich für vertikale Schreibrichtung (optional)

3. **32×32 oder höher** (Priorität 3)
   - Sehr große Dateien
   - Nur für spezielle Anwendungen

---

**Empfohlene Roadmap:**
1. **Sprint 1:** Character-Index, Config-System, Code-Cleanup
2. **Sprint 2:** 16×16 Format, Top 500 Hanzi, Vollständige Kana
3. **Sprint 3:** Cache-System, Top 1.000 Hanzi, Proportional-Variante

**Realistisches Ziel nach 6 Wochen:**
- ✅ 8×8 + 16×16 Formate
- ✅ ~1.500 Glyphen (inkl. vollständige Kana)
- ✅ 90%+ Coverage für ERDA-Use-Cases
- ✅ Production-ready für GitBook-PDF-Export

---

**Dokument-Ende**  
**Letzte Aktualisierung:** 08. November 2025
