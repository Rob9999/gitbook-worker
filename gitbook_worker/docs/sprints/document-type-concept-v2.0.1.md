---
title: Document Type Concept for SUMMARY.md Generation
version: 2.0.1-alpha
date: 2025-12-29
status: proposal
history:
  - version: 2.0.1-alpha
    date: 2025-12-29
    changes: Initial concept for document type classification
  - version: 2.0.1-alpha+doc-catalog
    date: 2025-12-29
    changes: Added missing doc types (abbreviations, symbols, equations, listings, dedication, translator, legal, errata, changelog), part/subchapter handling, locale-aware section titles, per-doc ordering
---

# Document Type Concept for SUMMARY.md Generation

## Motivation

Aktuell wird SUMMARY.md ohne Berücksichtigung der semantischen Rolle eines Dokuments generiert. Dies führt zu:
- Vorwörter erscheinen mitten in der Kapitelstruktur
- Appendices sind nicht klar vom Haupttext getrennt
- Cover-Seiten fehlen eine dedizierte Behandlung
- Chapter-spezifische Anhänge sind nicht zuordenbar

**Lösung**: Document-Type Header in Markdown-Frontmatter + Flag in `publish.yml`

---

## Document Types

### 1. Core Structure Types

#### `part` - Buchteil / Part
**Zweck**: Mehrteilige Werke strukturieren (Teil I, II, ...)

**Position**: Vor den zugehörigen Kapiteln

**Properties**:
```yaml
---
doc_type: part
part_number: 1        # numerisch oder römisch
title: "Teil I – Grundlagen"
order: 90             # optionale Feinsortierung
---
```

**SUMMARY.md Output**:
```markdown
## Teil I – Grundlagen

* [Kapitel 1 – ...](chapters/ch-01.md)
```

#### `cover` - Cover Page / Startseite
**Zweck**: Buch-Cover mit Titel, Autor, Grafik, ggf. Video (Zukunft)

**Position**: Immer erste Seite, vor ToC

**Properties**:
```yaml
---
doc_type: cover
title: "Das ERDA Buch"
subtitle: "Mehrsprachige Publishing Platform"
cover_image: ./assets/cover.png
cover_video: ./assets/intro.mp4  # optional, future
authors:
  - ERDA Team
---
```

**SUMMARY.md Output**:
```markdown
# Das ERDA Buch

[Cover](index.md)
```

#### `dedication` - Widmung
**Zweck**: Widmung am Buchanfang

**Position**: Nach Cover, vor Preface

**Properties**:
```yaml
---
doc_type: dedication
title: "Für unsere Leserinnen"
order: 30
---
```

**SUMMARY.md Output**:
```markdown
* [Widmung](dedication.md)
```

#### `preface` - Vorwort / Prolog
**Zweck**: Einleitende Texte vor dem Hauptteil

**Position**: Nach Cover, vor Chapters

**Variants**:
- `preface` - Standard-Vorwort
- `foreword` - Geleitwort (von Dritter Person)
- `acknowledgments` - Danksagungen
- `introduction` - Einleitung

**Properties**:
```yaml
---
doc_type: preface
variant: foreword  # optional
title: "Vorwort"
author: "Dr. Jane Doe"  # optional, bei foreword
order: 40               # optionale Reihenfolge innerhalb der Preface-Gruppe
---
```

**SUMMARY.md Output**:
```markdown
## Vorwort

* [Vorwort](preface.md)
* [Geleitwort](foreword.md)
```

#### `translators-note` - Hinweis der Übersetzenden
**Zweck**: Sprachspezifische Hinweise, Terminologie-Erklärungen

**Position**: Nach Preface/Foreword oder vor den Kapiteln

**Properties**:
```yaml
---
doc_type: translators-note
title: "Hinweis der Übersetzenden"
order: 50
---
```

**SUMMARY.md Output**:
```markdown
* [Hinweis der Übersetzenden](translators-note.md)
```

#### `chapter` - Hauptkapitel
**Zweck**: Hauptinhalt des Buches

**Position**: Hauptteil, zwischen Preface und Epilog

**Properties**:
```yaml
---
doc_type: chapter
chapter_number: 1
title: "Beobachtbare Muster"
parent_chapter: 1       # optional für Unterkapitel 1.1, 1.2
order: 110              # optionale Feinsortierung
chapter_appendices:  # optional
  - chapters/chapter-01-appendix-a.md
  - chapters/chapter-01-appendix-b.md
---
```

**SUMMARY.md Output**:
```markdown
## Teil I: Hauptinhalt

* [Kapitel 1 – Beobachtbare Muster](chapters/chapter-01.md)
  * [Appendix 1.A – Methodenvergleich](chapters/chapter-01-appendix-a.md)
  * [Appendix 1.B – Rohdaten](chapters/chapter-01-appendix-b.md)
* [Kapitel 2 – Vergleichstabellen](chapters/chapter-02.md)
```

#### `epilog` - Epilog / Nachwort
**Zweck**: Abschließende Reflexion, Ausblick

**Position**: Nach Chapters, vor Appendices

**Properties**:
```yaml
---
doc_type: epilog
title: "Epilog – Ausblick"
---
```

**SUMMARY.md Output**:
```markdown
## Abschluss

* [Epilog – Ausblick](epilog.md)
```

#### `appendix` - Globaler Anhang
**Zweck**: Anhänge für das gesamte Buch

**Position**: Am Ende, nach Epilog

**Properties**:
```yaml
---
doc_type: appendix
appendix_id: "A"  # A, B, C, ...
title: "Datenquellen und Tabellenlayout"
category: "technical"  # optional: technical, legal, reference
---
```

**SUMMARY.md Output**:
```markdown
## Anhänge

* [Appendix A – Datenquellen](appendices/appendix-a.md)
* [Appendix B – Emoji-Abdeckung](appendices/appendix-b.md)
```

#### `chapter-appendix` - Kapitel-spezifischer Anhang
**Zweck**: Anhänge die nur ein Chapter betreffen

**Position**: Direkt nach dem zugehörigen Chapter

**Properties**:
```yaml
---
doc_type: chapter-appendix
chapter_ref: 1  # Bezug zu Chapter 1
appendix_id: "1.A"
title: "Methodenvergleich zu Kapitel 1"
---
```

**SUMMARY.md Output**: Siehe `chapter` oben (als Unterpunkt)

---

### 2. Front Matter Types (vor Hauptinhalt)

#### `list-of-tables` - Tabellenverzeichnis
**Zweck**: Verzeichnis aller Tabellen mit Seitenzahlen (wie in Ingenieurs-/wissenschaftlichen Büchern)

**Position**: Nach ToC, vor Chapters (typisch in wissenschaftlichen Publikationen)

**Properties**:
```yaml
---
doc_type: list-of-tables
title: "Tabellenverzeichnis"
auto_generate: true  # scan all chapters for tables
include_chapter_tables: true  # include tables from chapter-appendices
numbering_style: "decimal"  # decimal (1.1, 1.2), roman (I, II), alpha (A, B)
---
```

**SUMMARY.md Output**:
```markdown
## Verzeichnisse

* [Tabellenverzeichnis](list-of-tables.md)
```

**Auto-Generated Content Example**:
```markdown
# Tabellenverzeichnis

- Tabelle 1.1: Messreihen Versuchsaufbau A ........................... 12
- Tabelle 1.2: Vergleichswerte Konfiguration B ...................... 15
- Tabelle 2.1: Statistische Auswertung ............................... 23
- Tabelle A.1: Rohdaten Sensor 1-10 .................................. 45
```

#### `list-of-figures` - Abbildungsverzeichnis
**Zweck**: Verzeichnis aller Abbildungen/Grafiken mit Seitenzahlen

**Position**: Nach Tabellenverzeichnis (falls vorhanden), vor Chapters

**Properties**:
```yaml
---
doc_type: list-of-figures
title: "Abbildungsverzeichnis"
auto_generate: true  # scan all chapters for images
include_formats: [png, jpg, svg, pdf]  # which image formats to include
numbering_style: "decimal"  # decimal (1.1, 1.2), roman, alpha
---
```

**SUMMARY.md Output**:
```markdown
## Verzeichnisse

* [Tabellenverzeichnis](list-of-tables.md)
* [Abbildungsverzeichnis](list-of-figures.md)
```

**Auto-Generated Content Example**:
```markdown
# Abbildungsverzeichnis

- Abb. 1.1: Versuchsaufbau Übersicht ................................. 10
- Abb. 1.2: Messkurve Temperaturverlauf .............................. 14
- Abb. 2.1: Diagramm Vergleichsanalyse ............................... 20
- Abb. 3.1: Blockschaltbild System ................................... 28
```

#### `list-of-abbreviations` - Abkürzungsverzeichnis
**Zweck**: Abkürzungen, Akronyme und Bedeutungen

**Position**: Typisch nach Abbildungsverzeichnis

**Properties**:
```yaml
---
doc_type: list-of-abbreviations
title: "Abkürzungsverzeichnis"
auto_generate: true
include_symbols: false
order: 140
---
```

**SUMMARY.md Output**:
```markdown
* [Abkürzungsverzeichnis](list-of-abbreviations.md)
```

#### `list-of-symbols` - Symbolverzeichnis
**Zweck**: Mathematische/technische Symbole

**Position**: Nach Abkürzungen oder direkt nach Verzeichnissen

**Properties**:
```yaml
---
doc_type: list-of-symbols
title: "Symbolverzeichnis"
auto_generate: true
order: 150
---
```

**SUMMARY.md Output**:
```markdown
* [Symbolverzeichnis](list-of-symbols.md)
```

#### `list-of-equations` - Gleichungsverzeichnis
**Zweck**: Auflistung nummerierter Gleichungen

**Position**: Optional nach Symbolverzeichnis

**Properties**:
```yaml
---
doc_type: list-of-equations
title: "Gleichungsverzeichnis"
auto_generate: true
numbering_style: decimal
order: 160
---
```

#### `list-of-algorithms` - Algorithmusverzeichnis
**Zweck**: Nummerierte Algorithmen / Pseudocode

**Properties**:
```yaml
---
doc_type: list-of-algorithms
title: "Algorithmusverzeichnis"
auto_generate: true
order: 170
---
```

#### `list-of-listings` - Code-Listing-Verzeichnis
**Zweck**: Nummerierte Codebeispiele / Listings

**Properties**:
```yaml
---
doc_type: list-of-listings
title: "Listing-Verzeichnis"
auto_generate: true
include_languages: [py, js, ts, tex]
order: 180
---
```

---

### 3. Back Matter Types (nach Hauptinhalt)

#### `glossary` - Glossar
**Zweck**: Begriffsdefinitionen

**Position**: Vor oder nach Appendices

**Properties**:
```yaml
---
doc_type: glossary
title: "Glossar"
alphabetical: true  # auto-sort entries
---
```

**SUMMARY.md Output**:
```markdown
## Referenzen

* [Glossar](glossary.md)
```

#### `legal-notice` - Rechtliche Hinweise / Safety / Privacy
**Zweck**: Rechtliche Anforderungen, Sicherheitshinweise, Datenschutz

**Position**: Vor Bibliography oder im Referenzen-Block

**Properties**:
```yaml
---
doc_type: legal-notice
title: "Rechtliche Hinweise"
scope: [safety, privacy, compliance]
order: 410
---
```

#### `bibliography` - Literaturverzeichnis / Zitationen
**Zweck**: Quellenangaben, Referenzen

**Position**: Nach Appendices

**Properties**:
```yaml
---
doc_type: bibliography
title: "Zitationen & weiterführende Quellen"
citation_style: "APA"  # APA, MLA, Chicago, IEEE
---
```

**SUMMARY.md Output**:
```markdown
* [Zitationen & Quellen](references.md)
```

#### `index` - Stichwortverzeichnis
**Zweck**: Alphabetischer Index mit Seitenzahlen

**Position**: Nach Bibliography, vor Colophon

**Properties**:
```yaml
---
doc_type: index
title: "Stichwortverzeichnis"
auto_generate: true  # scan all chapters for keywords
---
```

**SUMMARY.md Output**:
```markdown
* [Stichwortverzeichnis](index-page.md)
```

#### `attributions` - Zuschreibungen / Danksagungen
**Zweck**: Danksagungen für verwendete Ressourcen, Lizenzen, Beitragende

**Position**: Nach Index, vor Colophon

**Properties**:
```yaml
---
doc_type: attributions
title: "Danksagungen & Zuschreibungen"
include_font_licenses: true  # auto-include from fonts.yml
include_contributors: true   # auto-include from git history
categories:
  - fonts
  - libraries
  - contributors
  - reviewers
---
```

**SUMMARY.md Output**:
```markdown
## Danksagungen

* [Danksagungen & Zuschreibungen](attributions.md)
```

**Content Example**:
```markdown
# Danksagungen & Zuschreibungen

## Verwendete Schriften

- **Twemoji Mozilla** (v0.7.0) - CC BY 4.0
  Copyright © Mozilla Foundation
  https://github.com/mozilla/twemoji-colr

- **DejaVu Fonts** - Bitstream Vera License
  Copyright © DejaVu Fonts Team

## Beitragende

- Dr. Jane Doe - Fachredaktion Kapitel 1-3
- John Smith - Technische Illustrationen
- ERDA Team - Konzeption & Umsetzung

## Software & Bibliotheken

- Pandoc - GPLv2+ - Document conversion
- LuaTeX - GPLv2 - Typesetting engine
- Python - PSF License - Automation
```

#### `colophon` - Kolophon / Impressum
**Zweck**: Verlagsangaben, Druckdaten, ISBN, Copyright, technische Details

**Position**: Letzte Seite (oder erste Rückseite bei Print)

**Properties**:
```yaml
---
doc_type: colophon
title: "Kolophon"
position: "back"  # back (letzte Seite) oder front (nach Cover)
include_technical_details: true  # Schriften, Software, Druckdaten
---
```

**SUMMARY.md Output**:
```markdown
## Impressum

* [Kolophon](colophon.md)
```

**Content Example**:
```markdown
# Kolophon

**Das ERDA Buch – Mehrsprachige Publishing Platform**

© 2025 ERDA Team
Alle Rechte vorbehalten.

**ISBN**: 978-3-12345-678-9 (Print)  
**eISBN**: 978-3-12345-679-6 (PDF)

**Lizenz**: CC BY-SA 4.0  
https://creativecommons.org/licenses/by-sa/4.0/

**Verlag**: ERDA Publishing  
**1. Auflage**: Dezember 2025

---

## Technische Details

**Satz**: LuaTeX 1.18.0  
**Schriften**: 
- Text: DejaVu Serif 2.37
- Code: DejaVu Sans Mono 2.37
- Emoji: Twemoji Mozilla 0.7.0

**Konvertierung**: Pandoc 3.6  
**Automatisierung**: Python 3.12, GitBook Worker 2.0.1

**Druck**: [Druckerei Name]  
**Papier**: 120g/m² Offset weiß  
**Bindung**: Klebebindung

---

Gesetzt und gedruckt in Deutschland.
```

#### `errata` - Errata / Fehlerkorrekturen
**Zweck**: Fehlerliste nach Veröffentlichung

**Position**: Am Ende des Back Matter, vor Colophon

**Properties**:
```yaml
---
doc_type: errata
title: "Errata"
version_scope: "v2.0.1"
order: 480
---
```

**SUMMARY.md Output**:
```markdown
* [Errata](errata.md)
```

#### `release-notes` / `changelog` - Versionshinweise
**Zweck**: Änderungen zwischen Releases

**Position**: Neben oder vor Errata

**Properties**:
```yaml
---
doc_type: release-notes
title: "Release Notes"
version: "2.0.1"
order: 470
---
```

**SUMMARY.md Output**:
```markdown
* [Release Notes](releases/v2.0.1.md)
```

---

### 4. Meta Document Types

#### `placeholder` - Platzhalter
**Zweck**: "Work in Progress", "Coming Soon"

**Position**: Wo benötigt

**Properties**:
```yaml
---
doc_type: placeholder
title: "Inhaltshinweis"
show_in_summary: false  # optional: hide from ToC
---
```

**SUMMARY.md Output**: Wird übersprungen oder grau dargestellt

#### `template` - Vorlagen
**Zweck**: Wiederverwendbare Templates

**Position**: Nicht in SUMMARY.md

**Properties**:
```yaml
---
doc_type: template
title: "Vorlage für mehrsprachige Texte"
show_in_summary: false
---
```

**SUMMARY.md Output**: Nicht enthalten (außer `show_in_summary: true`)

#### `example` - Beispieldokumente
**Zweck**: Test-Content, Demos, Examples

**Position**: Optional in SUMMARY.md

**Properties**:
```yaml
---
doc_type: example
category: "emoji-test"  # emoji-test, layout-demo, test-content
title: "Emoji-Beispiele – Smileys"
show_in_summary: true  # default: false
order: 900
---
```

**SUMMARY.md Output**:
```markdown
## Beispiele & Tests

* [examples](examples/README.md)
  * [Emoji – Smileys](examples/emoji-smileys.md)
```

---

## Configuration in `publish.yml`

### Flag: `use_document_types`

```yaml
publish:
- path: ./
  out_format: pdf
  out_dir: ./publish
  out: das-erda-buch.pdf
  source_type: folder
  source_format: markdown
  use_summary: true
  use_book_json: true
  
  # NEU: Document Type Support
  use_document_types: true  # default: false (backward-compatible)
  
  document_type_config:
    # Reihenfolge der Sections in SUMMARY.md
    section_order:
      - cover
      - dedication
      - preface
      - translators-note
      - list-of-tables
      - list-of-figures
      - list-of-abbreviations
      - list-of-symbols
      - list-of-equations
      - list-of-algorithms
      - list-of-listings
      - chapters
      - epilog
      - appendices
      - legal-notice
      - glossary
      - bibliography
      - index
      - attributions
      - errata
      - release-notes
      - colophon
    
    # Überschriften für Sections
    section_titles:
      preface: "Vorwort"
      dedication: "Widmung"
      translators-note: "Hinweis der Übersetzenden"
      list-of-tables: "Tabellenverzeichnis"
      list-of-figures: "Abbildungsverzeichnis"
      list-of-abbreviations: "Abkürzungsverzeichnis"
      list-of-symbols: "Symbolverzeichnis"
      list-of-equations: "Gleichungsverzeichnis"
      list-of-algorithms: "Algorithmusverzeichnis"
      list-of-listings: "Listing-Verzeichnis"
      chapters: "Teil I: Hauptinhalt"
      epilog: "Abschluss"
      appendices: "Anhänge"
      legal-notice: "Rechtliche Hinweise"
      glossary: "Referenzen"
      bibliography: "Literatur"
      index: "Register"
      attributions: "Danksagungen"
      errata: "Errata"
      release-notes: "Release Notes"
      colophon: "Impressum"

    # Sprach-/Profil-spezifische Überschriften
    section_titles_by_locale:
      en:
        dedication: "Dedication"
        translators-note: "Translator's Note"
        legal-notice: "Legal Notices"
        list-of-abbreviations: "List of Abbreviations"
        list-of-symbols: "List of Symbols"
        list-of-equations: "List of Equations"
        list-of-algorithms: "List of Algorithms"
        list-of-listings: "List of Listings"
    
    # Welche Types zeigen?
    show_in_summary:
      template: false
      placeholder: false
      example: true  # kann per doc überschrieben werden
      release-notes: true
      errata: true
      legal-notice: true
    
    # Auto-Nummerierung
    auto_number_chapters: true
    auto_number_appendices: true  # A, B, C, ...
    auto_number_parts: true       # Part I, II, ...
    
    # Chapter-Appendix Handling
    chapter_appendix_indent: true  # als Unterpunkt unter Chapter
    chapter_appendix_prefix: "Appendix {chapter}.{id}"

    # Per-Document Weighting (falls mehrere Preface/Notes/Legal)
    default_order_weight: 100
```

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. **Frontmatter Parser Enhancement**: `gitbook_worker/tools/content/frontmatter_parser.py`
   - Add `doc_type` field parsing
   - Add validation for known doc_types
  - Add `chapter_appendices`, `chapter_ref`, `appendix_id`, `part_number`, `parent_chapter`, `order` fields

2. **Document Type Registry**: `gitbook_worker/tools/content/document_types.py`
   ```python
   from enum import Enum
   
   class DocumentType(Enum):
       COVER = "cover"
       PREFACE = "preface"
       CHAPTER = "chapter"
       PART = "part"
       EPILOG = "epilog"
       APPENDIX = "appendix"
       CHAPTER_APPENDIX = "chapter-appendix"
       LIST_OF_TABLES = "list-of-tables"
       LIST_OF_FIGURES = "list-of-figures"
       LIST_OF_ABBREVIATIONS = "list-of-abbreviations"
       LIST_OF_SYMBOLS = "list-of-symbols"
       LIST_OF_EQUATIONS = "list-of-equations"
       LIST_OF_ALGORITHMS = "list-of-algorithms"
       LIST_OF_LISTINGS = "list-of-listings"
       GLOSSARY = "glossary"
       LEGAL_NOTICE = "legal-notice"
       BIBLIOGRAPHY = "bibliography"
       INDEX = "index"
       ATTRIBUTIONS = "attributions"
       ERRATA = "errata"
       RELEASE_NOTES = "release-notes"
       COLOPHON = "colophon"
       PLACEHOLDER = "placeholder"
       TEMPLATE = "template"
       EXAMPLE = "example"
       DEDICATION = "dedication"
       TRANSLATORS_NOTE = "translators-note"
   ```

3. **Config Schema Update**: `gitbook_worker/defaults/publish_schema.yml`
   - Add `use_document_types` flag
  - Add `document_type_config` schema inkl. `section_titles_by_locale`, new doc_types, `default_order_weight`

### Phase 2: SUMMARY.md Generator
1. **Collector**: `gitbook_worker/tools/content/document_collector.py`
   - Scan all markdown files
   - Parse frontmatter
   - Group by `doc_type`
   - Sort by `chapter_number`, `appendix_id`

2. **Summary Builder**: `gitbook_worker/tools/content/summary_builder.py`
   - Read `document_type_config` from `publish.yml`
   - Apply `section_order`
   - Generate sections with titles
   - Handle `chapter_appendices` linking
  - Apply `show_in_summary` filters
  - Apply per-doc `order` to stabilisieren (preface-Varianten, mehrere Legal Notices)
  - Support `part` grouping und nested chapters (`parent_chapter`)

3. **Backward Compatibility**:
   - If `use_document_types: false` → use old SUMMARY.md logic
   - If `doc_type` missing in file → infer from path (chapters/, appendices/)

### Phase 3: Validation & Testing
1. **Validation Rules**:
   - `chapter_appendix` must have valid `chapter_ref`
   - `appendix_id` must be unique
   - `chapter_number` must be sequential
  - `part_number` must be sequential (if used)
  - `order` must be numeric if provided
  - `cover` can only exist once
  - Only one `legal-notice` per scope unless `order` disambiguates
  - Only one `release-notes` pro Version

2. **Tests**:
   - `test_document_type_parser.py`
   - `test_summary_generation_with_types.py`
   - `test_chapter_appendix_linking.py`

### Phase 4: Documentation
1. Update `docs/multilingual-content-guide.md`
2. Create `docs/document-types-guide.md`
3. Add examples to `de/content/` and `en/content/`

---

## Examples

### Example 1: Simple Book Structure
```
content/
├── index.md              # doc_type: cover
├── preface.md            # doc_type: preface
├── chapters/
│   ├── chapter-01.md     # doc_type: chapter, chapter_number: 1
│   └── chapter-02.md     # doc_type: chapter, chapter_number: 2
├── epilog.md             # doc_type: epilog
└── references.md         # doc_type: bibliography
```

**Generated SUMMARY.md**:
```markdown
# Das ERDA Buch

[Cover](index.md)

## Vorwort

* [Vorwort](preface.md)

## Verzeichnisse

* [Tabellenverzeichnis](list-of-tables.md)
* [Abbildungsverzeichnis](list-of-figures.md)

## Teil I: Hauptinhalt

* [Kapitel 1 – Patterns](chapters/chapter-01.md)
* [Kapitel 2 – Tables](chapters/chapter-02.md)

## Abschluss

* [Epilog](epilog.md)

## Anhänge

* [Appendix A – Datenquellen](appendices/appendix-a.md)
* [Appendix B – Emoji-Abdeckung](appendices/appendix-b.md)

## Referenzen

* [Glossar](glossary.md)

## Literatur

* [Referenzen](references.md)

## Register

* [Stichwortverzeichnis](index-page.md)

## Danksagungen

* [Danksagungen & Zuschreibungen](attributions.md)

## Impressum

* [Kolophon](colophon.md)
```

### Example 2: Complex Book with Chapter-Appendices
```
content/
├── index.md              # doc_type: cover
├── chapters/
│   ├── chapter-01.md     # doc_type: chapter
│   │                     # chapter_appendices: [chapter-01-app-a.md]
│   ├── chapter-01-app-a.md  # doc_type: chapter-appendix
│   │                         # chapter_ref: 1, appendix_id: "1.A"
│   └── chapter-02.md     # doc_type: chapter
├── appendices/
│   ├── appendix-a.md     # doc_type: appendix, appendix_id: "A"
│   └── appendix-b.md     # doc_type: appendix, appendix_id: "B"
└── glossary.md           # doc_type: glossary
```

**Generated SUMMARY.md**:
```markdown
# Das ERDA Buch

[Cover](index.md)

## Teil I: Hauptinhalt

* [Kapitel 1 – Patterns](chapters/chapter-01.md)
  * [Appendix 1.A – Methodenvergleich](chapters/chapter-01-app-a.md)
* [Kapitel 2 – Tables](chapters/chapter-02.md)

## Anhänge

* [Appendix A – Datenquellen](appendices/appendix-a.md)
* [Appendix B – Emoji-Abdeckung](appendices/appendix-b.md)

## Referenzen

* [Glossar](glossary.md)
```

---

## Backward Compatibility

### Fallback-Logik bei fehlendem `doc_type`
1. **Path-basierte Inferenz**:
   - `content/index.md` → `cover`
   - `content/preface.md` → `preface`
   - `content/chapters/chapter-*.md` → `chapter`
   - `content/appendices/appendix-*.md` → `appendix`
   - `content/references.md` → `bibliography`

2. **Filename Pattern Matching**:
   - `*-appendix-*.md` in chapters/ → `chapter-appendix`
   - `glossary.md` → `glossary`
   - `epilog.md` / `epilogue.md` → `epilog`

3. **Default Behavior**:
   - Wenn `use_document_types: false` → ignore all doc_type headers
   - Wenn `use_document_types: true` + kein doc_type → use inference
   - Wenn kein Match → warning + behandle als `chapter`

---

## Open Questions & Future Extensions

### Q1: Multi-Part Books?
**Question**: Wie behandeln wir mehrteilige Bücher (Part I, Part II)?

**Proposal**:
```yaml
---
doc_type: chapter
part: 1  # Part I
chapter_number: 1
title: "Kapitel 1 – Patterns"
---
```

**SUMMARY.md**:
```markdown
## Teil I: Grundlagen

* [Kapitel 1](chapters/ch-01.md)

## Teil II: Fortgeschritten

* [Kapitel 3](chapters/ch-03.md)
```

### Q2: Nested Chapters?
**Question**: Sub-Chapters (1.1, 1.2 als eigenständige Files)?

**Proposal**:
```yaml
---
doc_type: chapter
chapter_number: 1.1
parent_chapter: 1
title: "Methodische Schritte"
---
```

### Q3: Multiple Bibliography Sections?
**Question**: Separate Bibliographien pro Chapter?

**Proposal**:
```yaml
---
doc_type: bibliography
scope: chapter
chapter_ref: 1
title: "Quellen zu Kapitel 1"
---
```

### Q4: Cover Video Support?
**Question**: Wie binden wir Videos ein (nur Web-PDF)?

**Proposal**:
```yaml
---
doc_type: cover
cover_video:
  url: ./assets/intro.mp4
  poster: ./assets/poster.png
  format: mp4
  platforms: [web]  # not in print PDF
---
```

---

## Migration Path (v2.0.0 → v2.0.1)

### Step 1: Opt-in Flag
- Add `use_document_types: false` to existing `publish.yml` (default)
- No breaking changes for existing users

### Step 2: Example Content
- Update `de/content/` with doc_type headers
- Update `en/content/` with doc_type headers
- Keep both versions working (with/without types)

### Step 3: Documentation
- Add migration guide in `docs/`
- Show before/after SUMMARY.md examples
- Explain benefits (structure, clarity, automation)

### Step 4: Testing
- Full test suite for both modes
- Validation tests for all doc_types
- Edge case tests (missing fields, invalid refs)

---

## Benefits

### For Authors
✅ **Semantic Clarity**: Doc type macht Rolle des Dokuments explizit
✅ **Automatic Ordering**: Keine manuelle SUMMARY.md Pflege
✅ **Chapter-Appendices**: Natürliche Zuordnung zu Chapters
✅ **Validation**: Früherkennung von Strukturfehlern

### For Readers
✅ **Better Navigation**: Klare Sections (Vorwort, Hauptteil, Anhänge)
✅ **Logical Flow**: Cover → Preface → Chapters → Epilog → Appendices
✅ **Consistent Structure**: Gleiche Struktur über alle Sprachen

### For Platform
✅ **Automation**: SUMMARY.md auto-generated from frontmatter
✅ **Extensibility**: Neue doc_types einfach hinzufügbar
✅ **Validation**: Strukturelle Konsistenz prüfbar
✅ **Multi-Language**: Section titles pro Sprache konfigurierbar

---

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation**: Opt-in flag (`use_document_types: false` default)

### Risk 2: Learning Curve
**Mitigation**: Comprehensive docs + examples + migration guide

### Risk 3: Complex Config
**Mitigation**: Sensible defaults, minimal required config

### Risk 4: Inference Errors
**Mitigation**: Clear warnings + validation messages

---

## Decision: Go / No-Go?

✅ **GO** - Vorteile überwiegen deutlich
- Backward-compatible durch Opt-in
- Löst echtes Problem (manuelle SUMMARY.md Pflege)
- Skaliert für große Bücher
- Foundation für zukünftige Features (Parts, nested chapters)

**Next Steps**:
1. Review dieses Konzept
2. Implementation Phase 1 (Core Infrastructure)
3. Prototyp mit DE content
4. Testing & Refinement
5. Documentation
6. v2.0.1 Release

---

**Status**: ✅ Proposal Ready for Review
**Version**: 2.0.1-alpha
**Date**: 2025-12-29
