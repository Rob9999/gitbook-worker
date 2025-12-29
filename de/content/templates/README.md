---
title: Vorlagen
date: 2024-06-02
version: 1.1
---

# Vorlagen

Dieser Ordner enthält wiederverwendbare Textvorlagen für mehrsprachige, neutrale Dokumentation.

## Verfügbare Vorlagen

### [Mehrsprachige Neutrale Texte](multilingual-neutral-text.md)

Eine strukturierte Vorlage für internationale Dokumentation mit:
- **Neutraler Formulierung**: Keine kultur-, marken- oder personenspezifischen Begriffe
- **Mehrsprachigkeit**: Beispieltexte in 10+ Hauptsprachen (DE, EN, FR, ES, ZH, JA, AR, HI, RU, PT)
- **Konsistenter Aufbau**: Kontextbeschreibung → Sprachspezifische Absätze → Tabellen

**Verwendungszwecke**:
- Template für globale Dokumentationsprojekte
- Testmaterial für Unicode-Abdeckung und Font-Rendering
- Demonstrationsobjekt für mehrsprachige PDF-Generierung

## Struktur der Vorlagen

Jede Vorlage folgt diesem Schema:

```markdown
---
title: Vorlagentitel
date: YYYY-MM-DD
version: X.Y
---

# Kontext
Kurze Beschreibung des Szenarios.

## Sprache (ISO-Code)
Neutraler Absatz ohne kulturspezifische Referenzen.
```

## Best Practices

**Bei Verwendung der Vorlagen**:
- ✅ Verwende kurze, prägnante Sätze
- ✅ Vermeide idiomatische Ausdrücke
- ✅ Nutze ISO-Sprachcodes (de-DE, en-US, fr-FR, etc.)
- ✅ Dokumentiere Anpassungen im Versionsverlauf
- ❌ Keine personenbezogenen Daten
- ❌ Keine Markennamen ohne Notwendigkeit
- ❌ Keine kulturspezifischen Metaphern

## Erweiterung

Neue Vorlagen sollten:
1. YAML-Frontmatter mit `title`, `date`, `version` haben
2. Mindestens 3 Sprachen abdecken (DE, EN, +1)
3. Im Versionsverlauf dokumentiert sein
4. Neutrale, wiederverwendbare Textbausteine enthalten

---

*Dieser Ordner wird bei Bedarf erweitert. Vorschläge für neue Vorlagen sind willkommen.*
