---
geometry:
- paperwidth=210mm
- paperheight=297mm
- left=15mm
- right=15mm
- top=15mm
- bottom=15mm
header-includes:
- \usepackage{calc}
- \usepackage{enumitem}
- \setlistdepth{20}
- \usepackage{longtable}
- \usepackage{ltablex}
- \usepackage{booktabs}
- \usepackage{array}
- \keepXColumns
- \setlength\LTleft{0pt}
- \setlength\LTright{0pt}
---

<a id="md-readme"></a>
# Start page

This is your quick navigation:

- [Cover & overview](#md-index)
- [Preface](#md-preface) and [Content note](#md-placeholder)
- [Chapter 1 – Observable patterns](#md-chapters-chapter-01)
- [Chapter 2 – Comparative tables](#md-chapters-chapter-02)
- [Emoji example collections](#md-examples-readme)
- [Appendices & references](#md-appendices-readme)
- [Lists of tables, figures, abbreviations](#md-list-of-tables)

> Tip: Use this page as a hub when you want to jump directly to chapters or examples.



\newpage

---
title: Home
description: Overview for the neutral sample book
date: 2024-06-01
version: 1.0
doc_type: cover
authors:
  - ERDA Team
---
<a id="md-index"></a>

# Welcome to the neutral sample library

This landing page provides a quick overview of the sample book, intended as a neutral template for tests, layout checks and international text snippets. The chapters include tables, images, internal and external links, as well as structured appendices.

## Quick start
- [Preface](#md-preface)
- [Chapter 1 – Observable patterns](#md-chapters-chapter-01)
- [Chapter 2 – Comparative tables](#md-chapters-chapter-02)
- [Templates for multilingual text](#md-templates-multilingual-neutral-text)
- [Appendix A – Data sources](#md-appendices-appendix-a)
- [Emoji examples (Smileys & people)](#md-examples-emoji-smileys-and-people)
- [Emoji examples (Nature & food)](#md-examples-emoji-nature-and-food)
- [Emoji examples (Activities & travel)](#md-examples-emoji-activities-and-travel)
- [Emoji examples (Objects, symbols & flags)](#md-examples-emoji-objects-symbols-flags)
- [Appendix – Emoji & font coverage](#md-appendices-emoji-font-coverage)
- [Citations & further reading](#md-references)

## Visual preview
<a id="visual-preview"></a>
![Neutral shapes](.gitbook/assets/neutral-grid.pdf)

The illustration shows abstract shapes with no reference to real people or trademark-relevant themes. It can be reused as often as needed to test image components.

## External neutral links
- [United Nations Data](https://data.un.org/)
- [Smithsonian Open Access](https://www.si.edu/openaccess)
- [World Meteorological Organization](https://public.wmo.int/en)

All links point to publicly accessible, neutral information and are suitable for legally low-risk test cases.

> Tip: Use this landing page as a template by copying the sections listed here and adapting them for your own documentation.


\newpage

---
title: Dedication
doc_type: dedication
order: 5
---
<a id="md-dedication"></a>

# Dedication

We dedicate this book to everyone who shares knowledge generously.


\newpage

---
title: Preface
date: 2024-06-01
version: 1.0
doc_type: preface
---
<a id="md-preface"></a>

# Preface

This preface explains the purpose and structure of the sample book. All content is deliberately phrased in a neutral way so it can be used for usability tests, layout demos and localisation workflows.

- **Audience:** teams who want to test text, image or table components without using real customer data.
- **Structure:** each section contains at least one element commonly found in book production – for example figures, cross-references, citations or tables.
- **International scope:** the included template for multilingual text covers common major languages and can be extended.

Further guidance can be found in [Chapter 1](#md-chapters-chapter-01), while [Chapter 2](#md-chapters-chapter-02) provides concrete table layouts.


\newpage

---
title: Chapter 1 – Observable patterns
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 1
---
<a id="md-chapters-chapter-01"></a>

# Chapter 1 – Observable patterns

This chapter introduces a neutral description of structured observations. All examples are based on generic measurement points that can be easily transferred to new contexts.

## 1.1 Method steps
1. **Define the frame:** determine the purpose of the observation (e.g. temperature, usage behaviour or process duration).
2. **Choose measurement points:** define neutral parameters that do not contain personal data.
3. **Secure documentation:** record measurement results in tables and cite the source, e.g. public data catalogues.[^1]

## 1.2 Example description
- *Measurement area:* a fictitious test area with a moderate climate.
- *Instruments:* standardised sensors with a calibration certificate.
- *Evaluation:* averages over a four-week period.

The resulting data is presented later in the book – in particular in [Chapter 2](#md-chapters-chapter-02) – in table form. Detailed data is also provided in [Appendix A](#md-appendices-appendix-a).

## 1.3 Cross-references
| Section | Purpose | Link |
|-----------|-------|------|
| Preface | Context and objective | [Introduction](#md-preface) |
| Image template | Visual representation | [Home](#visual-preview) |
| Text templates | Multilingual snippets | [Templates](#md-templates-multilingual-neutral-text) |

[^1]: See [Citations & further reading](#md-references).


\newpage

---
title: Chapter 2 – Comparative tables
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 2
---
<a id="md-chapters-chapter-02"></a>

# Chapter 2 – Comparative tables

The following tables show how neutral datasets can be structured. All values are illustrative averages and can easily be replaced with real measurement series.

## 2.1 Overview table
| Measurement point | Week 1 | Week 2 | Week 3 | Week 4 |
|-----------|---------|---------|---------|---------|
| Mean temperature (°C) | 18.2 | 18.5 | 18.4 | 18.3 |
| Relative humidity (%) | 52 | 53 | 51 | 52 |
| Hours of daylight | 14 | 14 | 13 | 13 |

## 2.2 Format example for ratios
| Category | Share of total volume | Note |
|-----------|------------------------|-------|
| Measurements with direct sensor reference | 40% | Sensors calibrated to ISO 17025 |
| Derived reference values | 35% | Computed using moving averages |
| Context data | 25% | Sourced from public catalogues[^2] |

The tables can be exported as CSV or revisited in [Appendix A](#table-layout). Always link internal sections using relative paths so the book works offline.

## 2.3 Reference to figures
![Grid representation of measurement points](.gitbook/assets/neutral-grid.pdf)

The figure illustrates how measurement zones can be shown schematically without naming real locations.

To verify an embedded HTML inlay variant, the following figure can additionally be used:

![ERDA logo](.gitbook/assets/ERDA_Logo_simple.png){fig-alt="ERDA Logo"}

[^2]: Cf. the referenced open catalogues in [Citations & further reading](#md-references).


\newpage

---
doc_type: epilog
title: Epilogue
version: 1.0.0
---
<a id="md-epilogue"></a>

# Epilogue

Placeholder for the epilogue / afterword.


\newpage

---
title: Emoji examples – Activities & travel
description: Common sport, leisure and transport emojis for functional and rendering tests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Initial version for activity and transport groups.
---
<a id="md-examples-emoji-activities-and-travel"></a>

# Emoji examples – Activities & travel

This collection combines sport, hobbies, office workflows and transport so workflows with combined emojis can be tested.

## Sport & fitness

| Category | Emoji | Unicode | Notes |
| --- | --- | --- | --- |
| Endurance | 🏃‍♀️ 🏃‍♂️ 🚴‍♀️ 🚴‍♂️ 🏊‍♀️ 🏊‍♂️ | Person + Variation Selector | Running, cycling and swimming |
| Team sports | ⚽ 🏀 🏐 🏈 ⚾ 🥎 | U+26BD · U+1F3C0 · U+1F3D0 · U+1F3C8 · U+26BE · U+1F94E | Ball games |
| Precision | 🏓 🏸 🏑 🤺 🎯 | U+1F3D3 · U+1F3F8 · U+1F3D1 · U+1F93A · U+1F3AF | Racket sports, fencing and target practice |
| Winter sports | ⛷️ 🏂 ⛸️ 🛷 🥌 | U+26F7 · U+1F3C2 · U+26F8 · U+1F6F7 · U+1F94C | Snow and ice disciplines |
| Wins | 🏅 🥇 🥈 🥉 🏆 | U+1F3C5 · U+1F947 · U+1F948 · U+1F949 · U+1F3C6 | Awards |

## Culture & leisure

| Topic | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Music | 🎧 🎤 🎸 🎻 🎹 🥁 | U+1F3A7 · U+1F3A4 · U+1F3B8 · U+1F3BB · U+1F3B9 · U+1F941 | Audio and instrument tests |
| Art \& media | 🎨 🖌️ 🖼️ 🎬 🎞️ | U+1F3A8 · U+1F58C · U+1F5BC · U+1F3AC · U+1F39E | Creative domains |
| Games | 🎮 ♟️ 🎲 🧩 🃏 | U+1F3AE · U+265F · U+1F3B2 · U+1F9E9 · U+1F0CF | Game and puzzle examples |
| Learning | 📚 🧪 🧬 🧠 📐 | U+1F4DA · U+1F9EA · U+1F9EC · U+1F9E0 · U+1F4D0 | Education and lab content |
| Office | 💻 🖥️ 🖨️ 📠 📸 | U+1F4BB · U+1F5A5 · U+1F5A8 · U+1F4E0 · U+1F4F8 | Remote and studio workflows |

## Travel & infrastructure

| Category | Emoji | Unicode | Context |
| --- | --- | --- | --- |
| Road transport | 🚗 🚙 🚌 🚎 🚚 🚛 🚜 | U+1F697–U+1F69C | Road vehicles |
| Rail | 🚆 🚇 🚈 🚊 🚉 | U+1F686 · U+1F687 · U+1F688 · U+1F68A · U+1F689 | Train types |
| Aviation | ✈️ 🛫 🛬 🚁 🛩️ | U+2708 · U+1F6EB · U+1F6EC · U+1F681 · U+1F6E9 | Flight movements |
| Water | ⛴️ 🚢 🛳️ 🚤 🛶 | U+26F4 · U+1F6A2 · U+1F6F3 · U+1F6A4 · U+1F6F6 | Ships and leisure boats |
| Infrastructure | 🛣️ 🛤️ 🛫 🧭 🗺️ | U+1F6E3 · U+1F6E4 · U+1F6EB · U+1F9ED · U+1F5FA | Navigation |

## Testing notes

- Transport emojis often increase line height; use fixed-height tables if you want reproducible layout tests.
- Use multi-column layouts so the Twemoji colour font anti-aliases correctly in dense sections.
- Combine sports and travel sections to check interactions between person ZWJ sequences and pictograms.


\newpage

---
title: Emoji examples – Nature & food
description: Collection of common nature, animal and food emojis for layout tests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: First release for nature and nutrition groups.
---
<a id="md-examples-emoji-nature-and-food"></a>

# Emoji examples – Nature & food

This reference page covers plants, weather events, animals and food. Use the groups to check colour contrast and line wrapping with multi-colour glyphs.

## Weather & environment

| Topic | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Weather | ☀️ 🌤️ ⛅ 🌧️ ⛈️ 🌩️ 🌪️ | U+2600 · U+1F324–U+1F32A | Neutral meteorological symbols |
| Sky | 🌈 🌙 ⭐ 🌌 🌠 | U+1F308 · U+1F319 · U+2B50 · U+1F30C · U+1F320 | Light and night motifs |
| Earth | 🌍 🌎 🌏 🌐 🧭 | U+1F30D · U+1F30E · U+1F30F · U+1F310 · U+1F9ED | Global representations |
| Plants | 🌱 🌿 ☘️ 🍀 🌳 🌵 | U+1F331 · U+1F33F · U+2618 · U+1F340 · U+1F333 · U+1F335 | Vegetation types |
| Elements | 🔥 💧 🪨 🌀 🌫️ | U+1F525 · U+1F4A7 · U+1FAA8 · U+1F300 · U+1F32B | Basic elements and effects |

## Animals

| Category | Emoji | Unicode | Notes |
| --- | --- | --- | --- |
| Mammals | 🐶 🐱 🐭 🐹 🐰 🦊 🐻 | U+1F436–U+1F43B | Pets and woodland animals |
| Birds | 🐦 🦅 🐧 🦜 🦢 | U+1F426 · U+1F985 · U+1F427 · U+1F99C · U+1F9A2 | Flying and water birds |
| Reptiles \& amphibians | 🐢 🐍 🦎 🐸 | U+1F422 · U+1F40D · U+1F98E · U+1F438 | Terrariums and natural history motifs |
| Insects | 🐝 🐞 🦋 🐜 🦟 | U+1F41D · U+1F41E · U+1F98B · U+1F41C · U+1F99F | Pollination and biology |
| Marine life | 🐟 🐠 🐡 🐬 🐳 🐙 | U+1F41F · U+1F420 · U+1F421 · U+1F42C · U+1F433 · U+1F419 | Aquatic diversity |

## Food & drink

| Category | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Fruit | 🍎 🍊 🍌 🍇 🍓 🥝 🍍 | U+1F34E–U+1F34A · U+1F34C · U+1F347 · U+1F353 · U+1F34F · U+1F34D | Fruit with clear colours |
| Vegetables | 🥕 🥦 🧅 🧄 🌽 🥔 | U+1F955 · U+1F966 · U+1F9C5 · U+1F9C4 · U+1F33D · U+1F954 | Food variety |
| Staples | 🍞 🥐 🥨 🥯 🍚 🍝 | U+1F35E · U+1F950 · U+1F968 · U+1F96F · U+1F35A · U+1F35D | Grain and pasta dishes |
| Snacks | 🍿 🍪 🍩 🍰 🧁 🍫 | U+1F37F · U+1F36A · U+1F369 · U+1F370 · U+1F9C1 · U+1F36B | Sweet examples |
| Drinks | ☕ 🍵 🥤 🧃 🍺 🍷 🍶 | U+2615 · U+1F375 · U+1F964 · U+1F9C3 · U+1F37A · U+1F377 · U+1F376 | Hot and cold drinks |

## Testing notes

- Combine plant or animal sections with the multilingual text templates to test line breaks in other scripts.
- Use dark and light background colours to ensure emoji colour layers stack correctly when using the Twemoji colour font.
- Also test print output in greyscale to assess contrast.


\newpage

---
title: Emoji examples – Objects, symbols & flags
description: Reference lists for tools, technology, symbols and flags with full emoji coverage.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Newly created page for objects, symbols and flags.
---
<a id="md-examples-emoji-objects-symbols-flags"></a>

# Emoji examples – Objects, symbols & flags

This page covers everyday objects, symbols and international flags and acts as a supplement to the other emoji example collections.

## Tools & devices

| Category | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Workshop | 🛠️ 🔧 🔩 ⚙️ 🪛 | U+1F6E0 · U+1F527 · U+1F529 · U+2699 · U+1FA9B | Mechanical components |
| Laboratory | 🔬 🔭 ⚗️ 🧪 🧫 | U+1F52C · U+1F52D · U+2697 · U+1F9EA · U+1F9EB | Research and analysis |
| Communication | 📱 📲 📞 📡 🛰️ | U+1F4F1 · U+1F4F2 · U+1F4DE · U+1F4E1 · U+1F6F0 | Radio and satellite symbols |
| Household | 🧹 🧺 🧼 🪣 🪟 | U+1F9F9 · U+1F9FA · U+1F9FC · U+1FAA3 · U+1FA9F | Cleaning and household items |
| Energy | 💡 🔋 🔌 ♻️ 🔦 | U+1F4A1 · U+1F50B · U+1F50C · U+267B · U+1F526 | Power and sustainability icons |

## Symbols & signs

| Type | Emoji | Unicode | Meaning |
| --- | --- | --- | --- |
| Warning | ⚠️ 🚸 ⛔ 🚫 ❗ ❕ | U+26A0 · U+1F6B8 · U+26D4 · U+1F6AB · U+2757 · U+2755 | Safety symbols |
| Navigation | ⛳ 🎯 🧭 🧭 🗺️ | U+26F3 · U+1F3AF · U+1F9ED · (dup.) · U+1F5FA | Orientation (including intentional duplication for redundancy tests) |
| Time | ⏱️ ⏲️ ⏰ 🕰️ 🗓️ | U+23F1 · U+23F2 · U+23F0 · U+1F570 · U+1F5D3 | Timers and calendars |
| Shapes | ⬛ 🟦 ⬜ 🟥 🟨 🟩 🟧 | U+2B1B · U+1F7E6 · U+2B1C · U+1F7E5 · U+1F7E8 · U+1F7E9 · U+1F7E7 | Area/shape test |
| Religion | ☮️ ☯️ ✝️ ☪️ 🕉️ ✡️ | U+262E · U+262F · U+271D · U+262A · U+1F549 · U+2721 | Spiritual symbols |

## Flags

| Region | Emoji | Description |
| --- | --- | --- |
| Global | 🏳️ 🏴 🏁 🏳️‍🌈 🏳️‍⚧️ | Base symbols incl. Pride variants |
| Europe | 🇪🇺 🇩🇪 🇫🇷 🇪🇸 🇮🇹 🇵🇱 🇸🇪 | EU and country flags |
| Americas | 🇺🇳 🇺🇸 🇨🇦 🇧🇷 🇦🇷 🇨🇱 | United Nations and the Americas |
| Africa | 🇪🇬 🇳🇬 🇰🇪 🇿🇦 🇪🇹 | North, West, East and Southern Africa |
| Asia \& Oceania | 🇨🇳 🇯🇵 🇰🇷 🇮🇳 🇦🇺 🇳🇿 | Asia-Pacific states |

## Testing notes

- Flags are made from regional indicator symbols (RIS); ensure the chosen font combines the sequences correctly.
- Verify that tables with symbols and tools render via the **DejaVu** set or another licence-compliant serif/sans solution.
- For coloured emojis, the Twemoji colour font remains recommended. In PDF workflows, use `fonts.yml` as the reference so ZWJ sequences are embedded.


\newpage

---
title: Emoji examples – Smileys & people
description: Overview of classic face and person emojis for test coverage.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: First collection for faces, gestures and role profiles.
---
<a id="md-examples-emoji-smileys-and-people"></a>

# Emoji examples – Smileys & people

This page groups commonly used emoji sets by emotions, gestures and role profiles. It serves as a reference to test layouts, fonts and emoji fallbacks.

## Smileys & emotions

| Category | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Happy | 😀 😃 😄 😁 😆 😅 | U+1F600–U+1F606 | Standard smileys for positive reactions |
| Affectionate | 😊 🥰 😍 😘 😻 | U+1F60A · U+1F970 · U+1F60D · U+1F618 · U+1F63B | Warm reactions and animal variants |
| Surprise | 🤩 😮 😯 😲 🥳 | U+1F929 · U+1F62E · U+1F62F · U+1F632 · U+1F973 | Astonishment and party mood |
| Thoughtful | 🤔 😐 😑 😶 🤨 | U+1F914 · U+1F610 · U+1F611 · U+1F636 · U+1F928 | Neutral or sceptical faces |
| Stress | 😰 😱 😨 😢 😭 | U+1F630 · U+1F631 · U+1F628 · U+1F622 · U+1F62D | Stress, worry and sadness |
| Health | 🤒 🤕 🤧 😷 😴 | U+1F912 · U+1F915 · U+1F927 · U+1F637 · U+1F634 | Medical emojis and sleep |

## Gestures & hands

| Type | Emoji | Unicode | Purpose |
| --- | --- | --- | --- |
| Approval | 👍 👏 🤝 🙌 | U+1F44D · U+1F44F · U+1F91D · U+1F64C | Approval and co-operation |
| Refusal | 👎 🙅 🙅‍♂️ 🙅‍♀️ | U+1F44E · U+1F645 · ZWJ sequences | Negation and stopping |
| Pointers | ☝️ ✍️ 👉 👈 👆 👇 | U+261D · U+270D · U+1F449 · U+1F448 · U+1F446 · U+1F447 | Pointing gestures |
| Culture | 🤲 👐 🤘 🤙 🤟 | U+1F932 · U+1F450 · U+1F918 · U+1F919 · U+1F91F | Greetings and music gestures |
| Inclusive | ✋ ✋🏻 ✋🏽 ✋🏿 | U+270B + Fitzpatrick modifiers | Skin tones for accessibility |

## People & roles

| Category | Emoji | Unicode | Description |
| --- | --- | --- | --- |
| Everyday | 🙂 🧑‍🦰 🧑‍🦱 🧑‍🦳 | Standard face and hair variants | Facial features with neutral colours |
| Occupation | 👩‍💻 👨‍🔧 🧑‍🏫 🧑‍🌾 | ZWJ sequences | Professional depictions |
| Family | 👨‍👩‍👧 👩‍👧‍👦 👨‍👨‍👧‍👦 | Family ZWJ | Diversity in households |
| Emergency/services | 👩‍🚒 👮‍♂️ 🧑‍🚀 🧑‍⚕️ | ZWJ sequences | Uniforms and services |
| Diversity | 🧕 🧔‍♂️ 🧑‍🦽 🧑‍🦯 | U+1F93F etc. | Cultural and assistance examples |

## Testing notes

- Combine these emoji rows with text blocks in different scripts to check interactions with line heights.
- For coloured glyphs, embedding the **Twemoji Color Font** is recommended; for monochrome tests, Twemoji can be rendered in greyscale.
- Add additional emojis with ZWJ or skin tone modifiers if your workflows require it.


\newpage

---
title: Examples
date: 2024-06-05
version: 1.0
doc_type: example
---
<a id="md-examples-readme"></a>

# Examples

This folder collects comprehensive emoji examples to validate color rendering and font coverage in generated PDFs.

## Emoji Categories

Examples are organized by Unicode categories:

- **[Smileys & People](#md-examples-emoji-smileys-and-people)**: Facial expressions, gestures, professional roles, and skin tone variants (U+1F600–U+1F64F, U+1F466–U+1F9D1)
  
- **[Nature & Food](#md-examples-emoji-nature-and-food)**: Animals, plants, weather symbols, and food items (U+1F330–U+1F37F, U+1F400–U+1F4FF)
  
- **[Activities & Travel](#md-examples-emoji-activities-and-travel)**: Sports, hobbies, transportation, and places (U+1F680–U+1F6FF, U+1F3A0–U+1F3FF)
  
- **[Objects, Symbols & Flags](#md-examples-emoji-objects-symbols-flags)**: Everyday objects, technical symbols, signs, and international flags (U+1F4A0–U+1F4FF, U+1F500–U+1F5FF, U+1F1E6–U+1F1FF)

## Test Coverage

These examples validate:
- ✅ **Color rendering**: Twemoji Mozilla COLR/CPAL format
- ✅ **Unicode completeness**: All common emoji ranges
- ✅ **Modifiers**: Skin tones, gender variants, ZWJ sequences
- ✅ **Layout stability**: Emoji in flowing text, tables, and lists

## Usage

**Purpose**: 
- Automated rendering tests for PDF generation
- Visual quality control for emoji colors
- Reference documentation for font stack configuration

**Technical Details**:
- Font: Twemoji Mozilla v0.7.0 (COLR/CPAL)
- Format: LuaTeX + Pandoc Lua filters
- Fallback: DejaVu Sans for non-emoji characters

---

*Last updated: Version 1.0 (2024-06-05) – Full Emoji 13.1 coverage*


\newpage

---
title: Template for multilingual neutral text
date: 2024-06-02
version: 1.1
doc_type: template
show_in_summary: false
---
<a id="md-templates-multilingual-neutral-text"></a>

# Template for multilingual neutral text

The following structure shows how neutral text building blocks can be written in multiple languages. Use short sentences, avoid personal details, and avoid culture- or brand-specific terms.

## Basic structure
```
## Context
Short description of the scenario.

### Language (ISO code)
Neutral paragraph.
```

## Example: global weather observation
- **Context:** a team describes a calm day with moderate weather readings.

### German (de)
Ein moderater Morgen brachte gleichmäßige Temperaturen, wodurch Messgeräte ohne Anpassung betrieben werden konnten.

### English (en)
The observation team noted a calm day with stable readings, enabling straightforward comparisons over the week.

### French (fr)
L'équipe a enregistré une journée stable, ce qui facilite la comparaison avec les mesures précédentes.

### Spanish (es)
El equipo observó un día sereno con datos regulares que permiten revisar tendencias sin sesgos.

### Portuguese (pt)
A equipe registrou um período estável, adequado para validar calibragens e rotinas de manutenção.

### Italian (it)
Il gruppo ha descritto una giornata equilibrata, utile per mantenere le serie temporali coerenti.

### Dutch (nl)
Het team rapporteerde een rustige dag met meetwaarden die zonder correcties konden worden vastgelegd.

### Bulgarian (bg)
Екипът отбеляза спокоен ден с равномерни данни, което улеснява сравненията в рамките на седмицата.

### Croatian (hr)
Tim je zabilježio miran dan s ujednačenim vrijednostima koje pojednostavljuju usporedbe tijekom tjedna.

### Czech (cs)
Tým zaznamenal klidný den se stabilními hodnotami, takže týdenní porovnání probíhá bez úprav.

### Danish (da)
Holdet noterede en rolig dag med jævne målinger, hvilket gør det let at sammenligne ugens værdier.

### Estonian (et)
Meeskond kirjeldas rahulikku päeva ühtlaste näitudega, mis hõlbustab nädalate võrdlemist.

### Finnish (fi)
Tiimi mukaan päivä oli tasainen ja mittaukset pysyivät muuttumattomina, mikä tukee vertailevaa seurantaa.

### Greek (el)
Η ομάδα κατέγραψε ήρεμη ημέρα με σταθερές μετρήσεις που διευκολύνουν τις εβδομαδιαίες συγκρίσεις.

### Hungarian (hu)
A csapat nyugodt napot írt le, amelynek mérései stabilak maradtak, így könnyű a heti összevetés.

### Irish (ga)
Luaigh an fhoireann lá ciúin le léamha cobhsaí a éascaíonn comparáidí seachtainiúla.

### Latvian (lv)
Komanda aprakstīja mierīgu dienu ar vienmērīgiem rādījumiem, kas atvieglo salīdzināšanu nedēļas griezumā.

### Lithuanian (lt)
Komanda užfiksavo ramią dieną su stabiliais duomenimis, todėl savaitiniai palyginimai yra paprasti.

### Maltese (mt)
It-tim irreġistra ġurnata kwieta b'qari stabbli li jagħmlu aktar faċli li tqabbel id-dejta tal-ġimgħa.

### Polish (pl)
Zespół odnotował spokojny dzień ze stałymi odczytami, co ułatwia porównania tygodniowe.

### Romanian (ro)
Echipa a remarcat o zi calmă cu valori stabile, ușurând comparațiile din cursul săptămânii.

### Slovak (sk)
Tím opísal pokojný deň so stabilnými údajmi, ktoré pomáhajú pri porovnávaní v rámci týždňa.

### Slovenian (sl)
Ekipa je opisala miren dan z enakomernimi meritvami, kar olajša tedenske primerjave.

### Swedish (sv)
Teamet noterade en lugn dag med stabila värden som gör jämförelser under veckan enklare.

### Ukrainian (uk)
Команда спостерігала спокійний день зі стабільними показниками, що спрощує тижневі порівняння.

### Arabic (ar)
سجل الفريق يوماً هادئاً بقراءات مستقرة تسهّل مقارنة البيانات خلال الأسبوع.

### Chinese (zh)
观测团队记录了一个稳定的日子，数据平稳，有助于持续对比不同周的趋势。

### Japanese (ja)
観測チームは穏やかな一日を記録し、安定したデータが週次比較を容易にすると述べました。

### Korean (ko)
관측 팀은 측정값이 고르게 유지된 차분한 하루를 기록하여 주간 비교가 수월해졌다고 보고했습니다.

### Hindi (hi)
टीम ने एक शांत दिन दर्ज किया जहाँ मान स्थिर रहे और साप्ताहिक तुलना सरल हो गई।

### Indonesian (id)
Tim melaporkan hari tenang dengan bacaan stabil sehingga peninjauan mingguan dapat dilakukan tanpa penyesuaian.

### Filipino (fil)
Iniulat ng koponan ang isang mahinahong araw na may pantay na datos, kaya mas madali ang paghahambing ng lingguhan.

### Māori (mi)
I tuhi te rōpū tirotiro i tētahi rā mārie me ngā uara tōtika, he mea māmā ai te whakataurite ā-wiki.

### Samoan (sm)
Na fa'amau e le 'au se aso filemu ma faitauga toniga e faafaigofie ai su'esu'ega o vaiaso ta'itasi.

### Swahili (sw)
Timu ilieleza siku tulivu yenye takwimu thabiti zinazorahisisha kulinganisha kwa wiki.

### Amharic (am)
ቡድኑ በተመጣጣኝ መዝገቦች ያለ የተረጋጋ ቀን መመዝገቡን አግልፆ እርምጃዎችን ለአስተካክል ቀላል እንደሚያደርግ ገለጸ።

### Yoruba (yo)
Ẹgbẹ́ náà sọ pé ọjọ́ naa dakẹ́ nígbà tí àwọ́n ìwọn ṣetán bí wọ́n ṣe rí, kí iṣirò ọ̀sẹ̀ rọrùn.

### Hausa (ha)
Ƙungiyar ta lura da ranar natsuwa mai daidaitattun bayanai da ke sauƙaƙa kwatancen mako-mako.

### Inuktitut (iu)
ᐊᒥᓱᓂ ᐱᒋᐊᕐᔪᖅ ᐅᑭᐅᑎᖅ ᐃᒡᓗᓕᖅ ᑐᙵᓇᐅᑎᓪᓗᓂ ᐱᖃᓗᒍ ᐅᓇ ᐃᓄᖅᑐᐊᓕᕐᓂᖅ ᑐᓴᖅᑕᐅᔪᒥ.

### Turkish (tr)
Ekip, ölçümlerin dengede kaldığı sakin bir gün bildirerek haftalık karşılaştırmaların kolaylaştığını belirtti.

### Azerbaijani (az)
Komanda sabit göstəricilərlə sakit bir gün qeydə aldı və bu da həftəlik müqayisələri sadələşdirir.

### Kazakh (kk)
Топ тұрақты көрсеткіштер сақталған тыныш күнді сипаттап, апталық салыстыруды жеңілдететінін айтты.

This list can be extended as needed. Add notes on writing systems or reading direction where relevant (for example for Arabic or Hebrew).


\newpage

---
title: Templates
date: 2024-06-02
version: 1.1
doc_type: template
---
<a id="md-templates-readme"></a>

# Templates

This folder contains reusable text templates for multilingual, neutral documentation.

## Available Templates

### [Multilingual Neutral Text](#md-templates-multilingual-neutral-text)

A structured template for international documentation featuring:
- **Neutral phrasing**: No culture-, brand-, or person-specific terms
- **Multilingualism**: Example texts in 10+ major languages (DE, EN, FR, ES, ZH, JA, AR, HI, RU, PT)
- **Consistent structure**: Context description → Language-specific paragraphs → Tables

**Use Cases**:
- Template for global documentation projects
- Test material for Unicode coverage and font rendering
- Demonstration object for multilingual PDF generation

## Template Structure

Each template follows this schema:

```markdown
---
title: Template Title
date: YYYY-MM-DD
version: X.Y
---

# Context
Brief description of the scenario.

## Language (ISO Code)
Neutral paragraph without culture-specific references.
```

## Best Practices

**When using templates**:
- ✅ Use short, concise sentences
- ✅ Avoid idiomatic expressions
- ✅ Use ISO language codes (de-DE, en-US, fr-FR, etc.)
- ✅ Document modifications in version history
- ❌ No personally identifiable information
- ❌ No brand names without necessity
- ❌ No culture-specific metaphors

## Extension

New templates should:
1. Have YAML front matter with `title`, `date`, `version`
2. Cover at least 3 languages (DE, EN, +1)
3. Be documented in version history
4. Contain neutral, reusable text blocks

---

*This folder is expanded as needed. Suggestions for new templates are welcome.*


\newpage

---
title: Translator's Note
doc_type: translators-note
order: 6
---
<a id="md-translators-note"></a>

# Translator's Note

This edition is based on the German version and was translated with the utmost care.


\newpage

---
title: List of Tables
date: 2025-12-29
version: 1.0
doc_type: list-of-tables
auto_generate: true
include_chapter_tables: true
numbering_style: "decimal"
---
<a id="md-list-of-tables"></a>

# List of Tables

> **Note**: This list of tables will be automatically generated from all chapter and appendix tables in future versions.

## Chapter Tables

- Table 1.1: Measurement Series Experimental Setup ............. (Ch. 1)
- Table 2.1: Comparison Values Layout A vs. B ................. (Ch. 2)
- Table 2.2: Statistical Evaluation ........................... (Ch. 2)

## Appendix Tables

- Table A.1: Public Climate Data Catalogs ..................... (App. A)
- Table A.2: Table Formats Overview ........................... (App. A)
- Table B.1: Font Matrix for Characters ....................... (App. B)
- Table B.2: Emoji Coverage by Category ....................... (App. B)

---

**Automatic Generation (v2.0.1+)**:
- All tables with captions will be automatically captured
- Numbering follows chapter affiliation
- Page numbers extracted from generated PDF


\newpage

---
title: List of Figures
date: 2025-12-29
version: 1.0
doc_type: list-of-figures
auto_generate: true
include_formats: [png, jpg, svg, pdf]
numbering_style: "decimal"
---
<a id="md-list-of-figures"></a>

# List of Figures

> **Note**: This list of figures will be automatically generated from all embedded images in future versions.

## Chapter Figures

- Fig. 1.1: Experimental Setup Overview ........................ (Ch. 1)
- Fig. 1.2: Measurement Curve Temperature Profile .............. (Ch. 1)
- Fig. 2.1: Diagram Comparative Analysis ....................... (Ch. 2)

## Appendix Figures

- Fig. A.1: Schematic Structure Data Catalog ................... (App. A)
- Fig. B.1: Font Coverage Matrix ............................... (App. B)

## Emoji Examples

- Fig. E.1: Smileys & People Overview .......................... (Ex.)
- Fig. E.2: Nature & Food Emoji Palette ........................ (Ex.)
- Fig. E.3: Activities & Travel Categories ..................... (Ex.)
- Fig. E.4: Objects, Symbols & Flags ........................... (Ex.)

---

**Automatic Generation (v2.0.1+)**:
- All images with alt-text or captions will be captured
- Numbering follows chapter affiliation
- Format detection: PNG, JPG, SVG, PDF
- Page numbers extracted from generated PDF


\newpage

---
title: List of Abbreviations
doc_type: list-of-abbreviations
order: 7
---
<a id="md-list-of-abbreviations"></a>

- API – Application Programming Interface
- CLI – Command Line Interface


\newpage

---
title: Appendix A – Data sources and table layout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---
<a id="md-appendices-appendix-a"></a>

# Appendix A – Data sources and table layout

## A.1 Data sources
1. Public climate data catalogues from regional weather services.
2. Neutral example values from internal sandbox systems.
3. International open-data repositories such as [UN Data](https://data.un.org/) or [World Bank Open Data](https://data.worldbank.org/).

## A.2 Table layout
<a id="table-layout"></a>
| Column | Data type | Description |
|--------|----------|-------------|
| `timestamp` | ISO-8601 | Timestamp of the measurement |
| `metric` | String | Measurement (temperature, humidity, etc.) |
| `value` | Decimal number | Measured value |
| `unit` | String | Associated unit |
| `notes` | Free text | Context or notes |

## A.3 Reuse
- The table can be imported directly into dataframes.
- Use relative links such as [Chapter 2](#md-chapters-chapter-02) for cross-references.
- Graphics can be found in the [`content/.github/assets`](../images/) directory.


\newpage

---
title: Appendix – Emoji & font coverage
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
<a id="md-appendices-emoji-font-coverage"></a>

# Appendix – Emoji & font coverage

This overview summarises the fonts that cover all writing systems used in the sample texts as well as all emoji sets. All fonts meet the licensing requirements from `AGENTS.md` and the `LICENSE-FONTS` file.

## Font matrix

| Category | Font | Licence | Source | Coverage |
| --- | --- | --- | --- | --- |
| Serif/Sans/Mono | DejaVu Serif · DejaVu Sans · DejaVu Sans Mono (v2.37) | Bitstream Vera License + public-domain additions | `gitbook_worker/defaults/fonts.yml` · `publish/ATTRIBUTION.md` | Latin, Greek, Cyrillic, plus technical symbols for tables and code |
| CJK \& additional BMP glyphs | ERDA CC-BY CJK | CC BY 4.0 **or** MIT | `.github/fonts/erda-ccby-cjk` · `LICENSE-FONTS` | Chinese, Japanese, Korean, plus additional Unicode blocks from the multilingual templates |
| Coloured emojis | Twemoji Color Font v15.1.0 | CC BY 4.0 | https://github.com/13rac1/twemoji-color-font/releases/tag/v15.1.0 · `publish/ATTRIBUTION.md` | All emoji categories including skin tones, ZWJ sequences and flags |

## Practical use

1. **Text sections** – The DejaVu family serves as the standard for body text (`SERIF`), UI elements (`SANS`) and code (`MONO`). This covers all European languages in `content/templates/multilingual-neutral-text.md`.
2. **CJK** – As soon as chapters or example pages use characters such as 日, 学 or 정보, the build system should embed the ERDA-CC-BY-CJK file from `.github/fonts/erda-ccby-cjk/true-type/`. This happens automatically via the `CJK` section in `gitbook_worker/defaults/fonts.yml`.
3. **Emoji colour** – The new emoji example pages use the Twemoji colour font. `gitbook_worker/defaults/fonts.yml` references the download URL so CI builds can fetch the TTF automatically.

## Testing notes

- Run `pytest -k emoji` to ensure the font scanning does not report unknown fonts.
- Check PDF exports with at least one page from each emoji category (smileys, nature, activities, objects) to test Twemoji alongside CJK text.
- Document any new fonts in `publish/ATTRIBUTION.md` and `LICENSE-FONTS` if additional writing systems are added.


\newpage

---
doc_type: legal-notice
title: Legal Notice
version: 1.0.0
---
<a id="md-legal-notice"></a>

# Legal Notice

Placeholder for imprint and legal notes.


\newpage

---
doc_type: glossary
title: Glossary
version: 1.0.0
---
<a id="md-glossary"></a>

# Glossary

Placeholder for terms and definitions.


\newpage

---
title: Citations & further reading
date: 2024-06-01
version: 1.0
doc_type: bibliography
citation_style: "APA"
---
<a id="md-references"></a>

# Citations & further reading

1. **United Nations Data Portal.** Accessed on 1 June 2024. https://data.un.org/
2. **World Bank Open Data.** Accessed on 1 June 2024. https://data.worldbank.org/
3. **World Meteorological Organization – Public Resources.** Accessed on 1 June 2024. https://public.wmo.int/en
4. **Smithsonian Open Access.** Accessed on 1 June 2024. https://www.si.edu/openaccess

References within the book use numbered footnotes to point consistently to this list.


\newpage

---
doc_type: index
title: Index
version: 1.0.0
---
<a id="md-book-index"></a>

# Index

Placeholder for the index.


\newpage

---
title: Acknowledgments & Attributions
date: 2025-12-29
version: 1.0
doc_type: attributions
include_font_licenses: true
include_contributors: true
categories:
  - fonts
  - libraries
  - contributors
---
<a id="md-attributions"></a>

# Acknowledgments & Attributions

This book was created with the support of many open-source projects and contributors. We thank everyone who makes their work available to the community.

---

## Fonts Used

### Twemoji Mozilla (v0.7.0)
**License**: CC BY 4.0  
**Copyright**: © Mozilla Foundation  
**Source**: https://github.com/mozilla/twemoji-colr  
**Usage**: Color emoji rendering (COLR/CPAL format)

### DejaVu Fonts (v2.37)
**License**: Bitstream Vera License (permissive, GPL-compatible)  
**Copyright**: © DejaVu Fonts Team  
**Source**: https://dejavu-fonts.github.io/  
**Usage**: 
- DejaVu Serif (body text)
- DejaVu Sans (headings, UI elements)
- DejaVu Sans Mono (code blocks)

### ERDA CC-BY CJK Font (v1.0)
**License**: CC BY 4.0  
**Copyright**: © ERDA Team  
**Usage**: Multilingual coverage (Latin, Cyrillic, Greek, CJK, Devanagari, Ethiopic)

---

## Software & Libraries

### LuaTeX (v1.18.0)
**License**: GPLv2+  
**Copyright**: © LuaTeX Development Team  
**Usage**: PDF typesetting engine with COLR font support

### Pandoc (v3.6)
**License**: GPLv2+  
**Copyright**: © John MacFarlane  
**Usage**: Markdown → LaTeX conversion

### Python (v3.12)
**License**: PSF License  
**Copyright**: © Python Software Foundation  
**Usage**: Build automation, font management, workflow orchestration

### GitBook Worker (v2.0.1)
**License**: MIT  
**Copyright**: © ERDA Team  
**Usage**: Multilingual publishing system

---

## Contributors

### Project Team
- **ERDA Team** – Concept, development, documentation
- **GitHub Copilot** – Architecture support, code review, documentation assistance

### Editorial
- Neutral content: ERDA Content Team
- Emoji test collections: ERDA Quality Assurance
- Multilingual templates: ERDA Localization Team

### Technical Illustrations
- Font coverage matrix: Automatically generated
- Emoji overviews: Unicode Consortium data

---

## Data Sources

The neutral sample data comes from publicly accessible sources:

1. **United Nations Data Portal** – https://data.un.org/
2. **World Bank Open Data** – https://data.worldbank.org/
3. **World Meteorological Organization** – https://public.wmo.int/
4. **Smithsonian Open Access** – https://www.si.edu/openaccess

---

## Community & Standards

Special thanks to:
- **Unicode Consortium** – Emoji standard and documentation
- **GitHub** – Hosting and collaboration tools
- **Open Source Community** – For the countless libraries and tools

---

**Status**: December 2025  
**Version**: 1.0  
**Updates**: This document is updated with each release


\newpage

---
doc_type: errata
title: Errata
version: 1.0.0
---
<a id="md-errata"></a>

# Errata

Placeholder for known issues and corrections.


\newpage

---
doc_type: release-notes
title: Release Notes
version: 1.0.0
---
<a id="md-release-notes"></a>

# Release Notes

Placeholder for release notes.


\newpage

---
title: Colophon
date: 2025-12-29
version: 1.0
doc_type: colophon
position: "back"
include_technical_details: true
---
<a id="md-colophon"></a>

# Colophon

**The ERDA Book – Multilingual Publishing Platform**

A neutral example book for tests, layout demos, and localization workflows.

---

## Publication Details

**Title**: The ERDA Book  
**Subtitle**: Neutral Example Library for Multilingual Publishing Tests  
**Edition**: 1st Edition, December 2025

**Publisher**: ERDA Team  
**Contact**: https://github.com/Rob9999/gitbook-worker

**ISBN**: –  
**eISBN (PDF)**: –

---

## License

**Text License**: CC BY-SA 4.0  
Creative Commons Attribution-ShareAlike 4.0 International  
https://creativecommons.org/licenses/by-sa/4.0/

**Meaning**:
- ✓ Reproduction and distribution permitted
- ✓ Adaptation and commercial use permitted
- ⚠ Attribution required
- ⚠ Distribution only under same license

**Code License**: MIT License  
https://opensource.org/licenses/MIT

---

## Technical Details

### Typesetting and Typography

**Typesetting Engine**: LuaTeX 1.18.0 (TeX Live 2024)  
**Conversion**: Pandoc 3.6  
**Build System**: GitBook Worker 2.0.1 (Python 3.12)

**Fonts**:
- **Body Text**: DejaVu Serif 2.37 (10pt)
- **Headings**: DejaVu Sans 2.37 (14-24pt)
- **Code**: DejaVu Sans Mono 2.37 (9pt)
- **Emojis**: Twemoji Mozilla 0.7.0 (COLR/CPAL)
- **Multilingual**: ERDA CC-BY CJK 1.0 (7000+ glyphs)

### Document Properties

**Page Size**: A4 (210 × 297 mm)  
**Margins**: 2.5cm (top/bottom), 2cm (left/right)  
**Line Height**: 1.4 (body text)  
**Columns**: Single column

**PDF Version**: PDF/A-1b (archiving)  
**Color Model**: RGB (screen-optimized)  
**Font Embedding**: Full (100%)

### Automation

**Workflow Orchestrator**: GitBook Worker Orchestrator  
**Font Management**: FontStorageBootstrapper (dynamic loading)  
**Content Conversion**: Markdown → LaTeX → PDF  
**Emoji Processing**: Unicode 15.1 with COLR rendering

**Git Repository**: https://github.com/Rob9999/gitbook-worker  
**Release Tag**: v2.0.1  
**Build Date**: {{ BUILD_DATE }}

---

## Print Details

**Printing**: –  
**Paper**: –  
**Binding**: –

**Note**: This digital version is optimized for screen use. A print version with CMYK color space and high resolution can be generated separately.

---

## Version and History

**Version 1.0** (December 2025)
- First complete edition
- Document-type system implemented
- Automatic index generation
- Multilingual support (DE, EN)

Full changelog:  
https://github.com/Rob9999/gitbook-worker/releases

---

## Contact and Feedback

**Issues**: https://github.com/Rob9999/gitbook-worker/issues  
**Discussions**: https://github.com/Rob9999/gitbook-worker/discussions  
**Contributions**: Pull requests welcome!

---

Typeset with LuaTeX and Pandoc • Developed in Germany • December 2025
