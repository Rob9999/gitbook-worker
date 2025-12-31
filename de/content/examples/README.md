---
title: Beispiele
date: 2024-06-05
version: 1.0
doc_type: example
---

# Beispiele

Dieser Ordner sammelt umfassende Emoji-Beispiele zur Validierung der Farbdarstellung und Font-Abdeckung in generierten PDFs.

## Emoji-Kategorien

Die Beispiele sind nach Unicode-Kategorien organisiert:

- **[Smileys & Personen](emoji-smileys-and-people.md)**: Gesichtsausdrücke, Gesten, Berufsrollen und Hautfarb-Varianten (U+1F600–U+1F64F, U+1F466–U+1F9D1)
  
- **[Natur & Essen](emoji-nature-and-food.md)**: Tiere, Pflanzen, Wettersymbole und Lebensmittel (U+1F330–U+1F37F, U+1F400–U+1F4FF)
  
- **[Aktivitäten & Reisen](emoji-activities-and-travel.md)**: Sport, Hobbys, Verkehrsmittel und Orte (U+1F680–U+1F6FF, U+1F3A0–U+1F3FF)
  
- **[Objekte, Symbole & Flaggen](emoji-objects-symbols-flags.md)**: Alltags-Objekte, technische Symbole, Zeichen und internationale Flaggen (U+1F4A0–U+1F4FF, U+1F500–U+1F5FF, U+1F1E6–U+1F1FF)

## Testabdeckung

Diese Beispiele validieren:
- ✅ **Farbdarstellung**: Twemoji Mozilla COLR/CPAL Format
- ✅ **Unicode-Vollständigkeit**: Alle gängigen Emoji-Ranges
- ✅ **Modifikatoren**: Hautfarben, Geschlechts-Varianten, ZWJ-Sequenzen
- ✅ **Layout-Stabilität**: Emoji in Fließtext, Tabellen und Listen

## Verwendung

**Zweck**: 
- Automatisierte Rendering-Tests für PDF-Generierung
- Visuelle Qualitätskontrolle für Emoji-Farben
- Referenzdokumentation für Font-Stack-Konfiguration

**Technische Details**:
- Font: Twemoji Mozilla v0.7.0 (COLR/CPAL)
- Format: LuaTeX + Pandoc Lua-Filter
- Fallback: DejaVu Sans für nicht-Emoji-Zeichen

---

*Letzte Aktualisierung: Version 1.0 (2024-06-05) – Vollständige Emoji 13.1 Abdeckung*
