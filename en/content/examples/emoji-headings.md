---
title: "🧪 Emoji in headings – Header samples"
description: "Regression test page for emojis in headings (bookmarks/ToC) and in the front matter title."
date: 2026-01-08
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2026-01-08
    changes: New test page for emojis in headings.
---

# 🧪 Emoji in headings – Header samples

This page is a focused regression test for emojis in headings.
It checks that:

- Emojis in H1/H2/H3 do not trigger LaTeX/hyperref errors.
- PDF bookmarks/outline remain stable (PDF strings).
- ZWJ sequences and Variation Selector (VS16) are handled correctly.

## 😀 Standard emoji in H2

Example text with an emoji in the heading.

## 🧑‍💻 ZWJ sequence in H2 (person + laptop)

Example text with a ZWJ sequence.

## ⚙️ VS16 in H2 (gear with variation selector)

Example text with a variation selector.

### 🇺🇸 Flag in H3 (regional indicator sequence)

Example text with a flag emoji.

### ✋🏽 Skin tone modifier in H3

Example text with a Fitzpatrick modifier.
