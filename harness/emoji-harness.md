<!-- License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) -->
# Emoji Rendering Harness

Dieses Harnisch-Dokument bündelt alle Prüfungen rund um das farbige Emoji-Rendering im ERDA-Buch. Es wird automatisiert aus den Markdowndateien erzeugt und dient als visuelle wie auch automatisierbare Referenz.

## Abschnitt A – Emoji-Inventar

Die folgende Tabelle listet sämtliche im Buch gefundenen Emojis, inklusive Codepoints, CLDR-Namen und Häufigkeiten.

{{EMOJI_INVENTORY_TABLE}}

## Abschnitt B – Satzmuster

Unterschiedliche Textkontexte zeigen, ob die Inline-Darstellung konsistent bleibt.

### Inline-Fließtext

{{EMOJI_SAMPLE_INLINE}}

### Überschrift

#### {{EMOJI_SAMPLE_HEADING}}

### Listen & Zitate

- {{EMOJI_SAMPLE_LIST}}
- {{EMOJI_SAMPLE_LIST_ALTERNATE}}

> {{EMOJI_SAMPLE_BLOCKQUOTE}}

`{{EMOJI_SAMPLE_CODE}}`

## Abschnitt C – Schrift-Matrix

Vergleich der Emoji-Einbettung bei den im Buch verwendeten Schriften.

| Schriftart | Beispiel |
| --- | --- |
| Serif (DejaVu) | <span style="font-family: 'DejaVu Serif', serif;">{{EMOJI_SAMPLE_MATRIX}}</span> |
| Sans (DejaVu) | <span style="font-family: 'DejaVu Sans', sans-serif;">{{EMOJI_SAMPLE_MATRIX}}</span> |
| Monospace (DejaVu Mono) | <span style="font-family: 'DejaVu Sans Mono', monospace;">{{EMOJI_SAMPLE_MATRIX}}</span> |

---

Die Ausgabe dient als Referenz für die PDF-Konvertierung und wird im CI als Artefakt abgelegt.
