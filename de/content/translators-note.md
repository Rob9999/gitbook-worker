---
title: Hinweis der Übersetzung
doc_type: translators-note
order: 6
---

# Hinweis der Übersetzung

Dieses Dokument demonstriert mehrsprachige Publishing-Fähigkeiten und Übersetzungs-Workflows.

## Übersetzungsprinzipien

Bei der Übersetzung technischer Dokumentation:

- **Terminologiekonsistenz**: Einheitliche Übersetzung technischer Begriffe beibehalten
- **Kulturelle Anpassung**: Beispiele und Metaphern an die Zielkultur anpassen
- **Formaterhaltung**: Struktur, Überschriften und Formatierung identisch halten
- **Technische Genauigkeit**: Alle Codebeispiele, Befehle und Referenzen überprüfen

## Sprachliche Überlegungen

### Deutsche Konventionen

Diese deutsche Version folgt den Rechtschreib- und Grammatikkonventionen:

- Rechtschreibung: Neue deutsche Rechtschreibung (2006 Reform)
- Interpunktion: Deutsche Anführungszeichen („“)
- Datumsformat: TT.MM.JJJJ
- Zahlenformatierung: Punkt für Tausender (1.000), Komma für Dezimalstellen (3,14)

### Unicode-Unterstützung

Das Dokument umfasst umfangreiche Unicode-Inhalte:

- **100+ Sprachen**: Abdeckung wichtiger Schriftsysteme
- **Emoji-Rendering**: Korrekte Darstellung von Flaggen, Symbolen und kombinierten Sequenzen
- **Rechts-nach-links-Text**: Unterstützung für Arabisch, Hebräisch und andere RTL-Schriften

## Übersetzungs-Workflow

Inhalte werden in parallelen Sprachverzeichnissen gepflegt:

```
de/     # Deutsch
en/     # Englisch (Britisch)
```

Jede Sprache enthält:

- Unabhängige SUMMARY.md (Navigationsstruktur)
- Sprachspezifische Metadaten (book.json)
- Lokalisierte Frontmatter und Terminologie
