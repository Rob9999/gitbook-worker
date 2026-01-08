---
title: "🧪 Emoji im Header – Überschriften"
description: "Testseite für Emojis in Überschriften (Bookmarks/ToC) und im Frontmatter-Titel."
date: 2026-01-08
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2026-01-08
    changes: Neue Testseite für Emojis in Überschriften.
---

# 🧪 Emoji im Header – Überschriften

Diese Seite ist ein gezielter Regressionstest für Emojis in Überschriften.
Dabei wird geprüft, dass:

- Emojis in H1/H2/H3 nicht zu LaTeX-/hyperref-Fehlern führen.
- Bookmarks/Outline im PDF stabil bleiben (PDF-Strings).
- ZWJ-Sequenzen und Variation Selector (VS16) korrekt verarbeitet werden.

## 😀 Standard-Emoji im H2

Beispieltext mit Emoji in der Überschrift.

## 🧑‍💻 ZWJ-Sequenz im H2 (Person + Laptop)

Beispieltext mit ZWJ-Sequenz.

## ⚙️ VS16 im H2 (Gear mit Variation Selector)

Beispieltext mit Variation Selector.

### 🇩🇪 Flagge im H3 (Regional Indicator Sequenz)

Beispieltext mit Flaggen-Emoji.

### ✋🏽 Hauttöne im H3 (Modifier)

Beispieltext mit Fitzpatrick-Modifier.
