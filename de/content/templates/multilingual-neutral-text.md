---
title: Vorlage für mehrsprachige neutrale Texte
date: 2024-06-02
version: 1.1
doc_type: template
show_in_summary: false
---

# Vorlage für mehrsprachige neutrale Texte

Diese Vorlage bietet Richtlinien zur Erstellung von Inhalten, die für alle Sprachversionen geeignet sind.

## Prinzipien

Mehrsprachig neutrale Inhalte:

- **Kulturelle Neutralität**: Vermeiden kulturspezifischer Referenzen, Redewendungen oder Beispiele
- **Universelle Konzepte**: International anerkannte Ideen und Terminologie verwenden
- **Technischer Fokus**: Technische Genauigkeit über kulturellen Kontext betonen
- **Symbolpräferenz**: Symbole, Diagramme und Code gegenüber Prosa bevorzugen, wo möglich

## Sprachliche Überlegungen

### Vermeiden

❌ **Kulturspezifische Beispiele:**

```markdown
Wie die Zubereitung eines traditionellen Sonntagsbratens...
So amerikanisch wie Apfelkuchen...
```

❌ **Regionale Redewendungen:**

```markdown
Es regnet Bindfäden
Der Beweis liegt im Pudding
```

❌ **Länderspezifische Referenzen:**

```markdown
Wie von der deutschen DSGVO gefordert...
Ähnlich dem US-amerikanischen ZIP-Code-System...
```

### Bevorzugen

✅ **Universelle Beispiele:**

```markdown
Wie die Zubereitung einer Mahlzeit...
Ein weithin anerkanntes Muster...
```

✅ **Klare, wörtliche Sprache:**

```markdown
Starker Niederschlag
Beweise demonstrieren, dass...
```

✅ **Internationale Standards:**

```markdown
Wie von ISO 8601 gefordert...
Gemäß RFC 3339 Datumsformat...
```

## Inhaltsmuster

### Technische Dokumentation

Technische Inhalte sind natürlicherweise neutraler:

```markdown
## Installation

1. Paket herunterladen
2. In ein Verzeichnis entpacken
3. Installer ausführen
4. Installation mit `command --version` verifizieren
```

### Codebeispiele

Code überwindet Sprachbarrieren:

```python
# Universelle technische Konzepte
def calculate_total(items):
    return sum(item.price for item in items)
```

### Mathematische Notation

Mathematik ist international:

```markdown
Der Satz des Pythagoras: $a^2 + b^2 = c^2$
```

### Visuelle Elemente

Diagramme und Symbole funktionieren sprachübergreifend:

- Flussdiagramme
- Sequenzdiagramme
- Icons und Symbole (Unicode)
- Tabellen und Matrizen

## Metadatenstruktur

Für mehrsprachige Dokumente:

```yaml
---
title: Ihr Titel
date: JJJJ-MM-TT
version: X.Y
doc_type: chapter  # oder passender Typ
language_neutral: true  # Flag für neutrale Inhalte
translation_notes: "Fokus auf technische Genauigkeit"
---
```

## Test-Checkliste

Vor Veröffentlichung mehrsprachiger Inhalte:

- [ ] Keine kulturspezifischen Referenzen
- [ ] Keine Redewendungen oder umgangssprachlichen Ausdrücke
- [ ] Technische Begriffe ordnungsgemäß definiert
- [ ] Codebeispiele sind universal
- [ ] Zahlen und Daten verwenden ISO-Formate
- [ ] Währungssymbole vermieden (generische "Einheiten" verwenden)
- [ ] Zeitzonen bei Bedarf spezifiziert
- [ ] Messungen verwenden metrische (SI) Einheiten

## Übersetzungs-Workflow

Beim Übersetzen neutraler Inhalte:

1. **Struktur bewahren**: Überschriften und Formatierung identisch halten
2. **Technische Genauigkeit**: Technische Begriffe in Zielsprache verifizieren
3. **Wörtliche Übersetzung**: Kreative Interpretation vermeiden
4. **Code unverändert**: Niemals Code-Variablennamen oder Befehle übersetzen
5. **Metadaten-Sync**: Versions- und Datumsmetadaten konsistent halten
