---
title: Emoji-Beispiele – Smileys & Personen
description: Übersicht über klassische Gesichts- und Personen-Emojis zur Testabdeckung.
date: 2024-06-05
version: 1.0
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erste Sammlung für Gesichter, Gesten und Rollenprofile.
---

# Emoji-Beispiele – Smileys & Personen

Diese Seite gruppiert häufig genutzte Emoji-Sets nach Emotionen, Gesten und Rollenprofilen. Sie dient als Referenz, um Layouts, Schriftarten und Emoji-Fallbacks zu testen.

## Smileys & Emotionen

| Kategorie | Emoji | Unicode | Kurzbeschreibung |
| --- | --- | --- | --- |
| Fröhlich | 😀 😃 😄 😁 😆 😅 | U+1F600–U+1F606 | Standard-Smileys für positive Reaktionen |
| Liebevoll | 😊 🥰 😍 😘 😻 | U+1F60A · U+1F970 · U+1F60D · U+1F618 · U+1F63B | Herzliche Reaktionen und Tier-Varianten |
| Überraschung | 🤩 😮 😯 😲 🥳 | U+1F929 · U+1F62E · U+1F62F · U+1F632 · U+1F973 | Staunen und Party-Stimmung |
| Nachdenklich | 🤔 😐 😑 😶 🤨 | U+1F914 · U+1F610 · U+1F611 · U+1F636 · U+1F928 | Neutrale oder skeptische Gesichter |
| Stress | 😰 😱 😨 😢 😭 | U+1F630 · U+1F631 · U+1F628 · U+1F622 · U+1F62D | Stress, Sorge und Traurigkeit |
| Gesundheit | 🤒 🤕 🤧 😷 😴 | U+1F912 · U+1F915 · U+1F927 · U+1F637 · U+1F634 | Medizinische Emojis und Schlaf |

## Gesten & Hände

| Typ | Emoji | Unicode | Zweck |
| --- | --- | --- | --- |
| Zustimmung | 👍 👏 🤝 🙌 | U+1F44D · U+1F44F · U+1F91D · U+1F64C | Zustimmung und Kooperation |
| Ablehnung | 👎 🙅 🙅‍♂️ 🙅‍♀️ | U+1F44E · U+1F645 · ZWJ-Sequenzen | Verneinung und Abbruch |
| Hinweise | ☝️ ✍️ 👉 👈 👆 👇 | U+261D · U+270D · U+1F449 · U+1F448 · U+1F446 · U+1F447 | Zeigende Gesten |
| Kultur | 🤲 👐 🤘 🤙 🤟 | U+1F932 · U+1F450 · U+1F918 · U+1F919 · U+1F91F | Begrüßung und Musik-Gesten |
| Inklusiv | ✋ ✋🏻 ✋🏽 ✋🏿 | U+270B + Fitzpatrick Modifiers | Hauttöne zur Barrierefreiheit |

## Personen & Rollen

| Kategorie | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Alltag | 🙂 🧑‍🦰 🧑‍🦱 🧑‍🦳 | Standardgesicht und Haarvarianten | Gesichtszüge mit neutralen Farben |
| Beruf | 👩‍💻 👨‍🔧 🧑‍🏫 🧑‍🌾 | ZWJ-Sequenzen | Berufliche Darstellungen |
| Familie | 👨‍👩‍👧 👩‍👧‍👦 👨‍👨‍👧‍👦 | Familien-ZWJ | Diversität in Haushalten |
| Hilfsdienste | 👩‍🚒 👮‍♂️ 🧑‍🚀 🧑‍⚕️ | ZWJ-Sequenzen | Uniformen und Service |
| Diversität | 🧕 🧔‍♂️ 🧑‍🦽 🧑‍🦯 | U+1F93F etc. | Kultur- und Assistenzbeispiele |

## Hinweise für Tests

- Kombiniere diese Emoji-Zeilen mit Textblöcken in verschiedenen Schriftsystemen, um Wechselwirkungen mit Zeilenhöhen zu prüfen.
- Für farbige Glyphen empfiehlt sich das Einbinden der **Twemoji Color Font**; für monochrome Tests kann Twemoji in Graustufen gerendert werden.
- Ergänze weitere Emojis mit ZWJ- oder Hautton-Modifikatoren, wenn spezifische Workflows dies erfordern.
