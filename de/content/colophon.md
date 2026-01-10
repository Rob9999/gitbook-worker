---
title: Kolophon
date: 2025-12-29
version: 1.0
doc_type: colophon
position: "back"
include_technical_details: true
---

# Kolophon

Technische Details zur Produktion dieses Dokuments.

## Produktionsinformationen

### Erstellung

- **Erstellt am**: 2024-06-01
- **Letzte Aktualisierung**: 2025-12-29
- **Version**: 1.0.0
- **Build-System**: Python 3.8+ mit automatisierter Pipeline

### Quellformat

- **Primärformat**: Markdown mit YAML-Frontmatter
- **Versionskontrolle**: Git
- **Repository-Struktur**: Mehrsprachige parallele Verzeichnisse
- **Build-Tool**: Workflow Orchestrator (Python)

## Typografie

### Schriftarten

**Haupttext:**

- DejaVu Serif (Fließtext)
- DejaVu Sans (Überschriften)
- DejaVu Sans Mono (Code)

**Emojis:**

- Twemoji Mozilla (COLRv1) – Primär
- Twitter Color Emoji – Fallback

### Satz

- **Engine**: XeLaTeX / LuaLaTeX
- **Zwischenformat**: LaTeX via Pandoc
- **Seitenformat**: A4 (210 × 297 mm)
- **Textbreite**: Optimiert für Lesbarkeit
- **Schriftgröße**: 11pt Körper, skalierte Überschriften

## Technischer Stack

### Werkzeuge

**Konvertierung:**

- Pandoc 2.x – Markdown zu LaTeX
- XeLaTeX/LuaLaTeX – LaTeX zu PDF

**Build-System:**

- Python 3.8+
- PyYAML – Metadaten-Parsing
- GitPython – Repository-Integration
- Jinja2 – Template-Verarbeitung

**Bildverarbeitung:**

- svglib – SVG-Handhabung
- PIL/Pillow – Rastergrafikverarbeitung

### Plattform

- **Entwicklung**: Windows / Linux / macOS
- **CI/CD**: GitHub Actions (optional)
- **Container**: Docker-Unterstützung für reproduzierbare Builds

## Unicode-Unterstützung

### Schriftsysteme

- **Lateinisch**: Voll unterstützt (Diakritika, Erweiterungen)
- **Kyrillisch**: Russisch, Ukrainisch, Bulgarisch
- **Griechisch**: Modern und polytonisch
- **Arabisch**: Mit RTL-Unterstützung
- **CJK**: Chinesisch, Japanisch, Koreanisch
- **Indische Schriften**: Devanagari, Tamil, Bengali
- **100+ weitere**: Siehe Anhang B

### Emojis

- **Unicode-Version**: Emoji 13.0+
- **Kategorien**: Alle 8 Hauptkategorien abgedeckt
- **Hauttöne**: Fitzpatrick-Skala (Typ 1-6)
- **ZWJ-Sequenzen**: Unterstützt wo verfügbar
- **Flaggen**: Regionale Indikatorsymbole

## Qualitätssicherung

### Tests

- **Syntax-Validierung**: Markdown-Linting
- **Link-Überprüfung**: Interne und externe Links
- **PDF-Generierung**: Automatisierte Build-Tests
- **Font-Abdeckung**: Unicode-Rendering-Tests

### Review

- **Technische Prüfung**: Code-Beispiele und Befehle
- **Inhaltliche Prüfung**: Klarheit und Genauigkeit
- **Formatierung**: Konsistenz über Abschnitte
- **Barrierefreiheit**: Screenreader-Kompatibilität

## Lizenzen

Siehe separate Lizenzdateien:

- [LICENSE-CODE](../../LICENSE-CODE) – Software und Skripte
- [LICENSE-FONTS](../../LICENSE-FONTS) – Schriftlizenzen
- [LICENSE](../../LICENSE) – Inhalt und Dokumentation

## Kontakt

Für Fragen oder Feedback:

- **Repository**: gitbook-worker
- **Issue-Tracker**: GitHub Issues
- **Dokumentation**: `docs/` Verzeichnis

---

*Produziert mit Open-Source-Werkzeugen und frei verfügbaren Schriftarten.*
