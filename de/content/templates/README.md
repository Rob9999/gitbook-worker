---
title: Vorlagen
date: 2024-06-02
version: 1.1
doc_type: template
---

# Vorlagen

Dieses Verzeichnis enthält wiederverwendbare Vorlagen und Muster für die Dokumentation.

## Zweck

Vorlagen bieten:

- **Konsistenz**: Standardisierte Struktur über ähnliche Inhalte hinweg
- **Effizienz**: Schnelle Ausgangspunkte für neue Dokumente
- **Qualität**: Vorvalidierte Formatierung und Metadaten
- **Anleitung**: Beispiele für Best Practices

## Verfügbare Vorlagen

### Mehrsprachiger neutraler Text

Vorlage für Inhalte, die in allen Sprachversionen funktionieren müssen:

- Neutrale kulturelle Referenzen
- International anerkannte Beispiele
- Sprachunabhängige Codebeispiele
- Universelle Symbole und Notation

Siehe [multilingual-neutral-text.md](multilingual-neutral-text.md) für Details.

## Vorlagenstruktur

Jede Vorlage enthält:

```yaml
---
title: Vorlagenname
date: JJJJ-MM-TT
version: X.Y
doc_type: template
show_in_summary: false  # Normalerweise aus Haupt-TOC ausgeblendet
---
```

## Wie Vorlagen verwendet werden

1. **Kopieren** Sie die Vorlagendatei an Ihren Zielort
2. **Umbenennen** entsprechend Ihres Inhaltszwecks
3. **Aktualisieren** Sie Frontmatter (Titel, Datum, Version, doc_type)
4. **Ersetzen** Sie Vorlageninhalte durch Ihr Material
5. **Validieren** Sie Struktur und Formatierung

## Vorlagenkategorien

### Inhaltsvorlagen

- Kapitelstrukturen
- Beispielmuster
- Referenzdokumentations-Layouts

### Metadatenvorlagen

- Frontmatter-Konfigurationen
- Navigationsstrukturen
- Build-Konfigurationen

### Mehrsprachige Vorlagen

- Parallele Übersetzungs-Frameworks
- Sprachneutrale Inhaltsmuster
- Internationalisierungs-Richtlinien
