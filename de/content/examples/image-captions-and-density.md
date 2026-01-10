---
title: Bild-Beispiele – Captions & Dichte
description: Testseite für viele kleine Abbildungen und Captions in kurzer Folge.
date: 2026-01-10
version: 1.0
doc_type: example
category: "image-test"
show_in_summary: true
history:
  - version: 1.0
---

# Bild-Beispiele – Captions & Dichte

Diese Testseite prüft das Verhalten bei mehreren Bildern in kurzer Folge. Besonders relevant für:

- **Seitenumbrüche**: Wie verhalt sich das Layout bei vielen Bildern?
- **Bildunterschriften**: Werden Captions korrekt positioniert?
- **Abstände**: Ausreichender Raum zwischen Bildern?
- **Nummerierung**: Fortlaufende Bildnummern in Abbildungsverzeichnissen?

## Galerie (SVG)

Mehrere gleichartige Bilder in Folge testen das Layout:

![Neutrale Formen – A](../.gitbook/assets/neutral-shapes.svg)

_Abbildung 1: Erste Instanz der Formendarstellung_

![Neutrale Formen – B](../.gitbook/assets/neutral-shapes.svg)

_Abbildung 2: Zweite Instanz zur Prüfung von Wiederholungen_

## Mischung (SVG + PNG)

Kombination verschiedener Bildformate in einem Abschnitt:

![Neutrales Raster](../.gitbook/assets/neutral-grid.svg)

_Abbildung 3: Vektorgrafik mit Rastermuster_

![ERDA Logo](../.gitbook/assets/ERDA_Logo_simple.png)

_Abbildung 4: Rastergrafik (PNG-Format)_

## Technische Aspekte

### Bildunterschriften

Bildunterschriften (Captions) sollten:

1. Das Bild eindeutig beschreiben
2. Kontext zum umgebenden Text herstellen
3. Bei Bedarf Quellenangaben enthalten
4. Konsistent nummeriert sein

### Layout-Herausforderungen

Bei der Platzierung mehrerer Bilder müssen folgende Aspekte berücksichtigt werden:

- **Widow/Orphan-Kontrolle**: Bildunterschriften nicht vom Bild trennen
- **Seitenumbruch**: Große Bilder nicht mitten teilen
- **Abstände**: Ausreichender Raum zwischen Elementen
- **Ausrichtung**: Konsistente Positionierung

### Barrierefreiheit

Für bessere Zugänglichkeit:

- Jedes Bild bekommt einen aussagekräftigen Alt-Text
- Bildunterschriften ergänzen visuell dargestellte Informationen
- Farbschemata berücksichtigen Farbfehlsichtigkeit
- Kontraste sind ausreichend hoch
