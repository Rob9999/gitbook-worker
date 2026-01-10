---
title: Appendix B – Emoji & font coverage
description: Evidence of suitable fonts for all scripts and coloured emojis used in the sample content.
date: 2024-06-05
version: 1.0
doc_type: appendix
appendix_id: "B"
category: "technical"
history:
  - version: 1.0
    date: 2024-06-05
    changes: Initial version with font matrix and testing notes.
---

# Appendix B – Emoji & font coverage

This appendix documents font coverage for the diverse Unicode content used throughout this document, including emoji rendering and multilingual text support.

## Font stack

The document uses a carefully configured font stack:

### Primary text fonts

**DejaVu Serif / DejaVu Sans**

- **Coverage**: Latin, Cyrillic, Greek, basic IPA
- **Purpose**: Main body text and headings
- **Licence**: Free (Bitstream Vera derivative)
- **Unicode blocks**: ∼3,000 glyphs covering common scripts

### Emoji fonts

**Twemoji Mozilla (COLRv1)**

- **Coverage**: Full Emoji 13.0+ support
- **Format**: COLRv1 (colour font format)
- **Purpose**: Primary emoji rendering
- **Licence**: CC BY 4.0
- **Rendering**: Native colour in modern systems

**Twitter Color Emoji (Fallback)**

- **Coverage**: Emoji 12.0
- **Format**: CBDT/CBLC (bitmap colour)
- **Purpose**: Fallback for older systems
- **Licence**: CC BY 4.0 / MIT

## Emoji categories tested

Comprehensive testing across all Unicode emoji categories:

### 😀 People & Emotions

- Faces: 😀 😃 😄 😁 😅
- Hands: 👋 🤚 🖐 ✋ 🖖
- People: 👶 👧 🧒 👦 👨
- Skin tones: 👋🏻 👋🏼 👋🏽 👋🏾 👋🏿

### 🐕 Animals & Nature

- Mammals: 🐕 🐈 🐎 🐄 🐖
- Birds: 🐓 🐔 🐤 🐣 🐥
- Plants: 🌲 🌳 🌴 🌵 🌾
- Weather: ☀️ ⛅ ☁️ ⛈️ 🌧️

### 🍕 Food & Drink

- Prepared food: 🍕 🍔 🍟 🌭 🥪
- Fruit: 🍎 🍊 🍋 🍌 🍉
- Drinks: ☕ 🍵 🥤 🍺 🍷

### ⚽ Activities & Sports

- Sports: ⚽ 🏀 🏈 ⚾ 🥎
- Games: 🎮 🎯 🎲 🎰 🎳
- Arts: 🎨 🎭 🎪 🎬 🎤

### 🚗 Travel & Places

- Vehicles: 🚗 🚕 🚙 🚌 🚎
- Buildings: 🏠 🏡 🏢 🏣 🏤
- Geography: 🏔 ⛰️ 🏕 🏖 🏜

### 💡 Objects

- Tech: 💻 ⌨ 🖥 🖨 🖱
- Tools: 🔨 ⛏️ 🛠 ⚒️ 🔧
- Office: 📝 ✏ ✏️ 🖊 🖋

### 🔣 Symbols

- Math: ➕ ➖ ✖ ➗ 🟰
- Arrows: ⬆ ⬇ ⬅ ➡ ↔️
- Shapes: ◼️ ◻️ 🔲 🔳 ⬛

### 🏁 Flags

- Country flags: 🇬🇧 🇩🇪 🇫🇷 🇪🇸 🇮🇹
- Regional flags: 🏴‍☠️ (requires ZWJ support)
- Special flags: 🏳 🏴 🏳️‍🌈

## Complex emoji sequences

### Zero-Width Joiner (ZWJ) sequences

Testing compound emoji:

- **Family**: 👨‍👩‍👧‍👦 (requires ZWJ support)
- **Professions**: 👨‍⚕️ 👩‍🏫 👨‍🌾
- **Combinations**: 🏴‍☠️ 🏳️‍🌈

### Skin tone modifiers

Fitzpatrick scale support:

- Type 1-2 (light): 👋🏻
- Type 3 (medium-light): 👋🏼
- Type 4 (medium): 👋🏽
- Type 5 (medium-dark): 👋🏾
- Type 6 (dark): 👋🏿

### Flag sequences

Regional indicator symbols:

- 🇬 + 🇧 = 🇬🇧 (UK flag)
- 🇩 + 🇪 = 🇩🇪 (German flag)

## Script coverage

Multilingual text support across 100+ languages:

### Latin-based scripts

- Western European: English, German, French, Spanish
- Eastern European: Polish, Czech, Hungarian
- Special characters: Ā Ē Ī Ō Ū (macrons)

### Cyrillic

- Russian: Привет мир
- Ukrainian: Привіт світ
- Bulgarian: Здравей свят

### Greek

- Modern Greek: Γεια σου κόσμε
- Polytonic Greek: ἀρχή (archaic)

### Asian scripts

- Chinese (Simplified): 你好世界
- Japanese: こんにちは世界 (Hiragana)
- Korean: 안녕하세요 세계 (Hangul)

### Arabic & RTL scripts

- Arabic: مرحبا بالعالم (RTL)
- Hebrew: שלום עולם (RTL)
- Persian: سلام دنیا (RTL)

### South Asian scripts

- Devanagari: नमस्ते दुनिया (Hindi)
- Tamil: வணக்கம் உலகம்
- Bengali: হ্যালো বিশ্ব

### Other scripts

- Thai: สวัสดีชาวโลก
- Amharic: ሰላም ልዑል
- Georgian: გამარჯობა მსოფლიო

## Testing methodology

### Visual verification

All emoji and scripts:

1. Rendered in PDF output
2. Visually inspected for correctness
3. Checked for proper colour rendering (emoji)
4. Verified in both screen and print modes

### Font fallback chain

The system tests fallback behaviour:

```
Primary → Secondary → System fallback
```

- If primary font lacks a glyph, system tries secondary
- Final fallback to system fonts if needed
- Missing glyphs indicated by □ (replacement character)

### Known limitations

1. **ZWJ sequences**: Complex emoji may render as separate glyphs on older systems
2. **COLRv1 support**: Requires modern font rendering (Cairo 1.18+, FreeType 2.13+)
3. **RTL layout**: Simplified handling; complex bidirectional text may need adjustment
4. **Rare scripts**: Some scripts require additional font installation

## Font configuration

See [`fonts-storage/fonts.conf`](../../fonts-storage/fonts.conf) for the complete fontconfig configuration.

Key settings:

- Emoji font priority ordering
- Script-specific font mappings
- Fallback chains
- Hinting and antialiasing preferences- YAML frontmatter (document metadata)
- Heading hierarchy (TOC / PDF bookmarks)
- Lists, code blocks, blockquotes
- Tables and references
- Stable navigation (SUMMARY.md)

### Example table

| Item | Purpose |
|---|---|
| Heading | TOC/bookmarks |
| Table | list of tables |

### Example code block

```
python -m gitbook_worker.tools.workflow_orchestrator --help
```
