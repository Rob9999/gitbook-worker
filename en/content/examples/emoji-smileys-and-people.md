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
