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
| Art & media | 🎨 🖌️ 🖼️ 🎬 🎞️ | U+1F3A8 · U+1F58C · U+1F5BC · U+1F3AC · U+1F39E | Creative domains |
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
