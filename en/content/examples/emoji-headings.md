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

This page tests the correct display of emojis in headings at different levels. Particularly relevant is the encoding in PDF bookmarks and the table of contents.

## 🎯 Test scenarios

Emojis in headings place special demands on document processing:

- **PDF bookmarks**: Correct Unicode encoding in PDF table of contents
- **TOC generation**: Table of contents with emoji characters
- **Font fallbacks**: Switching between text and emoji fonts
- **Hierarchy**: Emojis at all heading levels (H1-H6)

## 📋 Emoji test

### Sample set

This page places emojis in headings to test bookmarks/TOC and PDF strings.

#### 🧪 Heading with emoji

Inline: ✅ ⚠️ ℹ️ 🔒 🔑 ♻️

#### 🧩 ZWJ sequences (complex)

👩‍💻 👨‍💻 🧑‍🚀 👨‍👩‍👧‍👦

#### 🏁 Flags in text

🇩🇪 🇪🇺 🇬🇧 🇺🇸 🇺🇳

#### 🔢 Keycaps & variants

0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟 #️⃣ *️⃣
