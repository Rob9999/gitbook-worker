---
title: Appendix B – Emoji- & Schriftabdeckung
description: Nachweis geeigneter Fonts für alle Schriftzeichen und farbigen Emojis im Beispielinhalt.
date: 2024-06-05
version: 1.0
doc_type: appendix
appendix_id: "B"
category: "technical"
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erstfassung mit Font-Matrix und Testhinweisen.
---

# Appendix B – Emoji- & Schriftabdeckung

Dieser Anhang dokumentiert die Schriftabdeckung für die vielfältigen Unicode-Inhalte, die im gesamten Dokument verwendet werden, einschließlich Emoji-Rendering und mehrsprachiger Textunterstützung.

## Schriftstapel

Das Dokument verwendet einen sorgfältig konfigurierten Schriftstapel:

### Primäre Textschriften

**DejaVu Serif / DejaVu Sans**

- **Abdeckung**: Lateinisch, Kyrillisch, Griechisch, Basis-IPA
- **Zweck**: Hauptfließtext und Überschriften
- **Lizenz**: Frei (Bitstream Vera Derivat)
- **Unicode-Blöcke**: ~3.000 Glyphen für gängige Schriften

### Emoji-Schriften

**Twemoji Mozilla (COLRv1)**

- **Abdeckung**: Volle Emoji 13.0+ Unterstützung
- **Format**: COLRv1 (Farbschrift-Format)
- **Zweck**: Primäres Emoji-Rendering
- **Lizenz**: CC BY 4.0
- **Rendering**: Native Farbe in modernen Systemen

**Twitter Color Emoji (Fallback)**

- **Abdeckung**: Emoji 12.0
- **Format**: CBDT/CBLC (Bitmap-Farbe)
- **Zweck**: Fallback für ältere Systeme
- **Lizenz**: CC BY 4.0 / MIT

## Getestete Emoji-Kategorien

Umfassende Tests über alle Unicode-Emoji-Kategorien:

### 😀 Menschen & Emotionen

- Gesichter: 😀 😃 😄 😁 😅
- Hände: 👋 🤚 🖐 ✋ 🖖
- Menschen: 👶 👧 🧒 👦 👨
- Hauttöne: 👋🏻 👋🏼 👋🏽 👋🏾 👋🏿

### 🐕 Tiere & Natur

- Säugetiere: 🐕 🐈 🐎 🐄 🐖
- Vögel: 🐓 🐔 🐤 🐣 🐥
- Pflanzen: 🌲 🌳 🌴 🌵 🌾
- Wetter: ☀️ ⛅ ☁️ ⛈️ 🌧️

### 🍕 Essen & Trinken

- Zubereitetes Essen: 🍕 🍔 🍟 🌭 🥪
- Früchte: 🍎 🍊 🍋 🍌 🍉
- Getränke: ☕ 🍵 🥤 🍺 🍷

### ⚽ Aktivitäten & Sport

- Sport: ⚽ 🏀 🏈 ⚾ 🥎
- Spiele: 🎮 🎯 🎲 🎰 🎳
- Kunst: 🎨 🎭 🎪 🎬 🎤

### 🚗 Reisen & Orte

- Fahrzeuge: 🚗 🚕 🚙 🚌 🚎
- Gebäude: 🏠 🏡 🏢 🏣 🏤
- Geografie: 🏔 ⛰️ 🏕 🏖 🏜

### 💡 Objekte

- Tech: 💻 ⌨ 🖥 🖨 🖱
- Werkzeuge: 🔨 ⛏️ 🛠 ⚒️ 🔧
- Büro: 📝 ✏ ✏️ 🖊 🖋

### 🔣 Symbole

- Mathe: ➕ ➖ ✖ ➗ 🟰
- Pfeile: ⬆ ⬇ ⬅ ➡ ↔️
- Formen: ◼️ ◻️ 🔲 🔳 ⬛

### 🏁 Flaggen

- Länderflaggen: 🇬🇧 🇩🇪 🇫🇷 🇪🇸 🇮🇹
- Regionalflaggen: 🏴‍☠️ (erfordert ZWJ-Unterstützung)
- Spezialflaggen: 🏳 🏴 🏳️‍🌈

## Komplexe Emoji-Sequenzen

### Zero-Width Joiner (ZWJ) Sequenzen

Test zusammengesetzter Emojis:

- **Familie**: 👨‍👩‍👧‍👦 (erfordert ZWJ-Unterstützung)
- **Berufe**: 👨‍⚕️ 👩‍🏫 👨‍🌾
- **Kombinationen**: 🏴‍☠️ 🏳️‍🌈

### Hautton-Modifikatoren

Fitzpatrick-Skala-Unterstützung:

- Typ 1-2 (hell): 👋🏻
- Typ 3 (mittelhell): 👋🏼
- Typ 4 (mittel): 👋🏽
- Typ 5 (mitteldunkel): 👋🏾
- Typ 6 (dunkel): 👋🏿

### Flaggensequenzen

Regionale Indikatorsymbole:

- 🇬 + 🇧 = 🇬🇧 (UK-Flagge)
- 🇩 + 🇪 = 🇩🇪 (Deutsche Flagge)

## Schriftabdeckung

Mehrsprachige Textunterstützung über 100+ Sprachen:

### Lateinbasierte Schriften

- Westeuropäisch: Englisch, Deutsch, Französisch, Spanisch
- Osteuropäisch: Polnisch, Tschechisch, Ungarisch
- Sonderzeichen: Ā Ē Ī Ō Ū (Makrons)

### Kyrillisch

- Russisch: Привет мир
- Ukrainisch: Привіт світ
- Bulgarisch: Здравей свят

### Griechisch

- Neugriechisch: Γεια σου κόσμε
- Polytonisches Griechisch: ἀρχή (archaisch)

### Asiatische Schriften

- Chinesisch (Vereinfacht): 你好世界
- Japanisch: こんにちは世界 (Hiragana)
- Koreanisch: 안녕하세요 세계 (Hangul)

### Arabisch & RTL-Schriften

- Arabisch: مرحبا بالعالم (RTL)
- Hebräisch: שלום עולם (RTL)
- Persisch: سلام دنیا (RTL)

### Südasiatische Schriften

- Devanagari: नमस्ते दुनिया (Hindi)
- Tamil: வணக்கம் உலகம்
- Bengalisch: হ্যালো বিশ্ব

### Andere Schriften

- Thai: สวัสดีชาวโลก
- Amharisch: ሰላም ለዓለም
- Georgisch: გამარჯობა მსოფლიო

## Test-Methodik

### Visuelle Überprüfung

Alle Emojis und Schriften:

1. In PDF-Ausgabe gerendert
2. Visuell auf Korrektheit inspiziert
3. Auf korrekte Farbdarstellung geprüft (Emojis)
4. In Bildschirm- und Druckmodi verifiziert

### Schrift-Fallback-Kette

Das System testet Fallback-Verhalten:

```
Primär → Sekundär → System-Fallback
```

- Falls primäre Schrift eine Glyphe fehlt, versucht System sekundäre
- Finaler Fallback auf Systemschriften falls nötig
- Fehlende Glyphen durch □ (Ersetzungszeichen) angezeigt

### Bekannte Einschränkungen

1. **ZWJ-Sequenzen**: Komplexe Emojis können auf älteren Systemen als separate Glyphen dargestellt werden
2. **COLRv1-Unterstützung**: Erfordert modernes Font-Rendering (Cairo 1.18+, FreeType 2.13+)
3. **RTL-Layout**: Vereinfachte Handhabung; komplexer bidirektionaler Text benötigt möglicherweise Anpassung
4. **Seltene Schriften**: Einige Schriften erfordern zusätzliche Schriftinstallation

## Schriftkonfiguration

Siehe [`fonts-storage/fonts.conf`](../../fonts-storage/fonts.conf) für die vollständige Fontconfig-Konfiguration.

Wichtige Einstellungen:

- Emoji-Schrift-Prioritätsreihenfolge
- Schriftspezifische Schrift-Mappings
- Fallback-Ketten
- Hinting- und Antialiasing-Präferenzen

- YAML-Frontmatter (Metadaten je Dokument)
- Überschriften-Hierarchie (TOC / Bookmarks)
- Listen, Codeblöcke, Zitate
- Tabellen und Verweise
- Stabile Navigation (SUMMARY.md)

### Beispieltabelle

| Element | Zweck |
|---|---|
| Überschrift | TOC/Bookmarks |
| Tabelle | List-of-Tables |

### Beispiel-Codeblock

```
python -m gitbook_worker.tools.workflow_orchestrator --help
```
