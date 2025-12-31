---
title: Examples
date: 2024-06-05
version: 1.0
doc_type: example
---

# Examples

This folder collects comprehensive emoji examples to validate color rendering and font coverage in generated PDFs.

## Emoji Categories

Examples are organized by Unicode categories:

- **[Smileys & People](emoji-smileys-and-people.md)**: Facial expressions, gestures, professional roles, and skin tone variants (U+1F600–U+1F64F, U+1F466–U+1F9D1)
  
- **[Nature & Food](emoji-nature-and-food.md)**: Animals, plants, weather symbols, and food items (U+1F330–U+1F37F, U+1F400–U+1F4FF)
  
- **[Activities & Travel](emoji-activities-and-travel.md)**: Sports, hobbies, transportation, and places (U+1F680–U+1F6FF, U+1F3A0–U+1F3FF)
  
- **[Objects, Symbols & Flags](emoji-objects-symbols-flags.md)**: Everyday objects, technical symbols, signs, and international flags (U+1F4A0–U+1F4FF, U+1F500–U+1F5FF, U+1F1E6–U+1F1FF)

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
