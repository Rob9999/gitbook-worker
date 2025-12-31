---
version: 1.0.0
date: 2025-12-31
history:
  - 1.0.0: Initial draft (Doc-Type generator usage and fallbacks)
---

# Configure Doc-Types for SUMMARY generation

Diese Notiz fasst zusammen, wie das Doc-Type-Feature in `gitbook_style.py` und `document_types.py` arbeitet, wie man es aktiviert und welche Fallbacks greifen.

## Funktionsweise (Kurzfassung)
- Aktivierung: `use_document_types: true` im jeweiligen `publish.yml`.
- Reihenfolge: `document_type_config.section_order` bestimmt die Abschnittsreihenfolge in `SUMMARY.md`.
- Titel: `section_titles` (optional) überschreibt die Überschrift je Abschnitt; fehlt ein Eintrag, wird der Roh-Sections-Schlüssel verwendet (z. B. `appendices`).
- Sichtbarkeit: `show_in_summary` steuert pro Doc-Type, ob er gelistet wird (Default: true, falls nicht gesetzt).
- Nummerierung: `auto_number_chapters`, `auto_number_appendices`, `auto_number_parts` steuern automatische Zählungen.
- Kapitel-Anhang: `chapter_appendix_indent` + `chapter_appendix_prefix` steuern Einrückung und Präfix für Kapitel-Anhänge.

## Doc-Type-Erkennung
1) Frontmatter hat Vorrang: `doc_type: ...` (muss einem Eintrag in `DOC_TYPES` entsprechen).
2) Fallback-Heuristik: `_infer_doc_type` erkennt gängige Muster über Pfad/Dateiname (z. B. `index.md` → cover, `chapters/*` → chapter, `appendices/*` → appendix, Epilog-Ordner/-Namen → epilog, etc.).
3) Dokumente ohne erkannten Doc-Type werden ignoriert und erscheinen nicht in der generierten SUMMARY.

## Was passiert, wenn `section_titles` fehlt?
- Die Überschrift der Section wird aus dem Schlüssel in `section_order` übernommen (z. B. `glossary`, `index`).
- Reihenfolge und Auswahl bleiben unverändert; lediglich die Anzeige nutzt den Roh-Schlüssel.

## Was passiert bei fehlenden Doc-Types?
- Ein Abschnitt in `section_order` ohne passende Dokumente wird übersprungen.
- Um einen Abschnitt sichtbar zu machen, braucht es mindestens eine Datei mit passendem `doc_type` (oder eine Datei, die per Heuristik diesem Typ zugeordnet wird).

## Generierungsschritte
- CLI: `python -m gitbook_worker.tools.publishing.gitbook_style summary --root <lang-root> --document-manifest <lang>/publish.yml --summary-appendices-last`
- Der Generator versucht zuerst `generate_doc_type_summary` (Doc-Type-Modus). Fällt nur zurück auf den klassischen Baum-Generator, wenn `use_document_types` im Manifest nicht aktiv ist oder das Manifest nicht geladen werden kann.

## Konfigurations-Checkliste
- `publish.yml` enthält `use_document_types: true` und eine vollständige `section_order`.
- Für jede Section existiert mindestens eine Datei mit passendem `doc_type` (Frontmatter oder heuristisch ableitbar).
- Optional: `section_titles` und `section_titles_by_locale` pflegen, wenn freundliche Überschriften benötigt werden.
- `show_in_summary` setzen, falls einzelne Doc-Types ausgeblendet werden sollen (z. B. `template: false`).

## Typische Stolpersteine
- Frontmatter-Zeilen dürfen nicht zusammenkleben (`version: ...` und `doc_type: ...` brauchen eigene Zeilen).
- Wenn ein Doc-Type in `section_order` steht, aber kein Dokument ihn trägt, taucht die Section nicht auf.
- Beispiele/Templates erscheinen nur, wenn sie in `section_order` stehen **und** `show_in_summary` nicht auf false gesetzt ist.

## Referenzen
- Generator-Logik: `gitbook_worker/tools/publishing/document_types.py`
- CLI/Wrapper: `gitbook_worker/tools/publishing/gitbook_style.py` (Command `summary`)
