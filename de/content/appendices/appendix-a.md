---
title: Appendix A – Datenquellen und Tabellenlayout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---

# Appendix A – Datenquellen und Tabellenlayout

Dieser Anhang dokumentiert die Datenquellen und strukturellen Konventionen, die in Tabellen im gesamten Dokument verwendet werden.

## Tabellen-Design-Prinzipien

### Lesbarkeit

Tabellen sind gestaltet für:

- **Schnelles Scannen**: Klare Überschriften und konsistente Ausrichtung
- **Datenvergleich**: Parallele Struktur für einfachen Vergleich
- **Referenznutzung**: Vollständige Informationen ohne externen Kontext

### Konsistenz

Alle Tabellen folgen:

- Konsistente Spaltenanordnung
- Einheitliche Überschriftenformatierung
- Standard-Ausrichtungsregeln (links für Text, rechts für Zahlen)
- Beschreibende Bildunterschriften

## Tabellentypen

### Vergleichstabellen

Struktur zum Vergleichen von Optionen:

| Merkmal | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Leistung | Hoch | Mittel | Niedrig |
| Komplexität | Niedrig | Mittel | Hoch |
| Kosten | Niedrig | Mittel | Hoch |

### Referenztabellen

Datenabfrage-Format:

| Schlüssel | Wert | Beschreibung |
|-----|-------|-------------|
| Begriff 1 | Definition | Ausführliche Erklärung |
| Begriff 2 | Definition | Ausführliche Erklärung |

### Mehrstufige Tabellen

Hierarchische Informationen:

| Kategorie | Unterkategorie | Details |
|----------|----------------|----------|
| Typ A | Variante 1 | Spezifikationen |
| | Variante 2 | Spezifikationen |
| Typ B | Variante 1 | Spezifikationen |

## Datenquellen

### Primärquellen

Tabellen werden zusammengestellt aus:

- Offiziellen Dokumentationen und Spezifikationen
- Veröffentlichten Standards (ISO, RFC usw.)
- Peer-reviewter Forschung wo anwendbar
- Herstellerdokumentationen und Release Notes

### Datenverifizierung

Alle tabellierten Daten:

1. Mit Primärquellen abgeglichen
2. Auf aktuelle Genauigkeit überprüft
3. Datiert zur Angabe der Aktualität
4. Wo möglich mit Quelldokumentation verlinkt

### Aktualisierungsrichtlinie

Tabellen werden überprüft:

- Während Hauptversions-Updates
- Wenn sich zugrundeliegende Spezifikationen ändern
- Nach bedeutenden Technologie-Veröffentlichungen
- Sobald Korrekturen identifiziert werden

## Formatierungskonventionen

### Numerische Daten

- **Ganzzahlen**: Kein Dezimaltrennzeichen (1000, nicht 1.000)
- **Dezimalzahlen**: Komma als Dezimaltrennzeichen (3,14)
- **Prozentsätze**: Zahl gefolgt vom %-Symbol (85%)
- **Bereiche**: Halbgeviertstrich zwischen Werten (10–20)

### Textausrichtung

- **Linksbündig**: Text, Beschreibungen, Kategorienamen
- **Rechtsbündig**: Zahlen, Daten, Versionen
- **Zentriert**: Ja/Nein, Häkchen, Symbole

### Spezielle Symbole

- ✓ = Unterstützt/Ja
- ✗ = Nicht unterstützt/Nein
- — = Nicht zutreffend
- ≈ = Ungefähr
- ≥/≤ = Größer/kleiner oder gleich

## Bildunterschriften-Format

Tabellen-Bildunterschriften enthalten:

```markdown
Tabelle X.Y: Beschreibender Titel
```

Wobei:

- X = Kapitelnummer
- Y = Fortlaufende Tabellennummer innerhalb des Kapitels
- Titel beschreibt Inhalt prägnant

## Barrierefreiheit

### Screenreader

Tabellen verwenden:

- Korrekte Markdown-Tabellensyntax für korrektes HTML-Rendering
- Beschreibende Überschriften, die bei sequenziellem Lesen funktionieren
- Bildunterschriften, die Kontext unabhängig vom umgebenden Text bieten

### Drucklesbarkeit

Tabellen-Design berücksichtigt:

- Seitenbreitenbeschränkungen in PDF-Ausgabe
- Lesbarkeit in Standarddruckgrößen
- Klare Unterscheidung zwischen Kopf- und Datenzeilen

### Beispieltabelle

| Element | Zweck |
|---|---|
| Überschrift | TOC/Bookmarks |
| Tabelle | List-of-Tables |

### Beispiel-Codeblock

```
python -m gitbook_worker.tools.workflow_orchestrator --help
```
