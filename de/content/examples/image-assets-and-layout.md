---
title: Bild-Beispiele – Assets & Layout
description: Neutrale Testbilder aus .gitbook/assets (Raster + SVG) für Rendering- und PDF-Regressionstests.
date: 2026-01-10
version: 1.0
doc_type: example
category: "image-test"
show_in_summary: true
history:
  - version: 1.0
---

# Bild-Beispiele – Assets & Layout

Diese Seite demonstriert die Integration verschiedener Bildformate in Markdown-Dokumente. Alle verwendeten Assets befinden sich im Verzeichnis `content/.gitbook/assets/` und sind rechtlich unkritisch.

## Bildformate im Vergleich

### Rasterbilder (PNG)

Rasterbilder eignen sich für:
- Fotos und komplexe Grafiken
- Bilder mit vielen Farbverläufen
- Screenshots und Bildschirmaufnahmen

**Nachteil**: Bei Vergrößerung kann es zu Qualitätsverlusten kommen.

<div><figure><img src="../.gitbook/assets/ERDA_Logo_simple.png" alt="ERDA Logo"><figcaption><p>ERDA Logo (PNG)</p></figcaption></figure></div>

### Vektorbilder (SVG)

Vektorbilder bieten:
- Beliebige Skalierbarkeit ohne Qualitätsverlust
- Kleine Dateigrößen bei einfachen Grafiken
- Scharfe Darstellung auf allen Bildschirmauflösungen

**Ideal für**: Diagramme, Icons, technische Zeichnungen

![Neutrales Raster (SVG)](../.gitbook/assets/neutral-grid.svg)

### Diagramme und Workflows

Strukturierte Darstellungen wie Flowcharts profitieren besonders von Vektorgrafiken:

![Neutraler Workflow (SVG)](../.gitbook/assets/neutral-flow.svg)

## Best Practices

### Bildgrößen

- **Web**: 72-96 DPI ausreichend
- **Druck**: Mindestens 300 DPI bei Rasterbildern
- **SVG**: Auflösungsunabhängig

### Dateiformate

| Format | Verwendung | Transparenz | Kompression |
|--------|------------|-------------|-------------|
| PNG | Screenshots, Logos | Ja | Verlustfrei |
| JPEG | Fotos | Nein | Verlustbehaftet |
| SVG | Diagramme, Icons | Ja | Vektorgrafik |
| WebP | Modern, Web | Ja | Beide Modi |

### Alt-Texte

Jedes Bild sollte einen beschreibenden Alt-Text haben:
- Verbessert Barrierefreiheit
- Hilft Suchmaschinen
- Wird angezeigt, wenn Bild nicht geladen werden kann
