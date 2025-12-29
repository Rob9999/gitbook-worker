---
title: Emoji-Beispiele – Aktivitäten & Reisen
description: Häufige Sport-, Freizeit- und Transport-Emojis für Funktions- und Renderingtests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Startversion für Aktivitäten- und Verkehrsgruppen.
---

# Emoji-Beispiele – Aktivitäten & Reisen

Diese Sammlung kombiniert Sport, Hobbys, Büro-Workflows und Transportmittel, damit Workflows mit kombinierten Emojis getestet werden können.

## Sport & Fitness

| Kategorie | Emoji | Unicode | Hinweis |
| --- | --- | --- | --- |
| Ausdauer | 🏃‍♀️ 🏃‍♂️ 🚴‍♀️ 🚴‍♂️ 🏊‍♀️ 🏊‍♂️ | Person + Variation Selector | Lauf-, Rad- und Schwimm-Events |
| Teamsport | ⚽ 🏀 🏐 🏈 ⚾ 🥎 | U+26BD · U+1F3C0 · U+1F3D0 · U+1F3C8 · U+26BE · U+1F94E | Ballspiele |
| Präzision | 🏓 🏸 🏑 🤺 🎯 | U+1F3D3 · U+1F3F8 · U+1F3D1 · U+1F93A · U+1F3AF | Schläger-, Fecht- und Zielübungen |
| Wintersport | ⛷️ 🏂 ⛸️ 🛷 🥌 | U+26F7 · U+1F3C2 · U+26F8 · U+1F6F7 · U+1F94C | Schnee- und Eisdisziplinen |
| Siege | 🏅 🥇 🥈 🥉 🏆 | U+1F3C5 · U+1F947 · U+1F948 · U+1F949 · U+1F3C6 | Auszeichnungen |

## Kultur & Freizeit

| Thema | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Musik | 🎧 🎤 🎸 🎻 🎹 🥁 | U+1F3A7 · U+1F3A4 · U+1F3B8 · U+1F3BB · U+1F3B9 · U+1F941 | Audio- und Instrumententests |
| Kunst & Medien | 🎨 🖌️ 🖼️ 🎬 🎞️ | U+1F3A8 · U+1F58C · U+1F5BC · U+1F3AC · U+1F39E | Kreativbereiche |
| Spiele | 🎮 ♟️ 🎲 🧩 🃏 | U+1F3AE · U+265F · U+1F3B2 · U+1F9E9 · U+1F0CF | Game- und Puzzlebeispiele |
| Lernen | 📚 🧪 🧬 🧠 📐 | U+1F4DA · U+1F9EA · U+1F9EC · U+1F9E0 · U+1F4D0 | Bildungs- und Labor-Inhalte |
| Büro | 💻 🖥️ 🖨️ 📠 📸 | U+1F4BB · U+1F5A5 · U+1F5A8 · U+1F4E0 · U+1F4F8 | Remote- und Studio-Workflows |

## Reisen & Infrastruktur

| Kategorie | Emoji | Unicode | Kontext |
| --- | --- | --- | --- |
| Landverkehr | 🚗 🚙 🚌 🚎 🚚 🚛 🚜 | U+1F697–U+1F69C | Straßenfahrzeuge |
| Bahn | 🚆 🚇 🚈 🚊 🚉 | U+1F686 · U+1F687 · U+1F688 · U+1F68A · U+1F689 | Bahntypen |
| Luftfahrt | ✈️ 🛫 🛬 🚁 🛩️ | U+2708 · U+1F6EB · U+1F6EC · U+1F681 · U+1F6E9 | Flugbewegungen |
| Wasser | ⛴️ 🚢 🛳️ 🚤 🛶 | U+26F4 · U+1F6A2 · U+1F6F3 · U+1F6A4 · U+1F6F6 | Schiffe & Freizeitboote |
| Infrastruktur | 🛣️ 🛤️ 🛫 🧭 🗺️ | U+1F6E3 · U+1F6E4 · U+1F6EB · U+1F9ED · U+1F5FA | Navigation |

## Hinweise für Tests

- Transport-Emojis verursachen oft höhere Zeilenhöhen; verwende daher Tabellen mit fixer Höhe, wenn Layouttests reproduzierbar sein sollen.
- Nutze Mehrspalten-Layouts, damit die Twemoji-Color-Font bei dicht gepackten Abschnitten richtig anti-aliased wird.
- Kombiniere Sport- und Reiseabschnitte, um Interaktionen zwischen Personen-ZWJ-Sequenzen und Piktogrammen zu überprüfen.
