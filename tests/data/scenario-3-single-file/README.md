# Scenario 3: Single File Conversion

Testet die Konvertierung einer einzelnen Markdown-Datei zu PDF ohne GitBook-Struktur.

## Struktur

```
scenario-3-single-file/
├── publish.yml
└── complex-doc_with-special&chars@2024!.md
```

## Besondere Features dieser Datei

### 1. Dateiname mit Sonderzeichen
- Enthält: `_` (Unterstrich), `&` (Ampersand), `@` (At), `!` (Ausrufezeichen)
- Testet Filesystem-Kompatibilität und LaTeX-Escaping

### 2. Mehrsprachige Inhalte (8 Schriftsysteme)
- **CJK**: Chinesisch (中文), Japanisch (日本語), Koreanisch (한국어)
- **Kyrillisch**: Russisch (Русский)
- **Rechts-nach-Links**: Arabisch (العربية)
- **Andere**: Griechisch (Ελληνικά), Hindi (हिन्दी), Thai (ไทย)

### 3. Umfangreiche Tabellen-Tests

| Spaltenanzahl | Mit Überschrift | Ohne Überschrift | Zeilen |
|---------------|-----------------|------------------|--------|
| 1 | - | ✅ | 5 |
| 2 | ✅ | - | 8 |
| 5 | - | ✅ | 8 |
| 10 | ✅ | - | 8 |
| 25 | - | ✅ | 4 |
| 5 (lang) | ✅ | - | 50 |
| 100 | ✅ | - | 2 |

**Herausforderungen:**
- Breite Tabellen (100 Spalten) → automatische Skalierung
- Lange Tabellen (50+ Zeilen) → Seitenumbruch-Handling
- Gemischte Überschriften-Stile

### 4. LaTeX-Sonderzeichen
- Ampersand: & 
- Prozent: %
- Dollar: \$
- Unterstrich: \_
- Hash: \#
- Geschweifte Klammern: \{ \}
- Tilde: \~
- Caret: \^

### 5. Emojis
- Gesichter: 😀 😃 😄
- Objekte: 📱 💻 🎮
- Symbole: ✅ ❌ ⚠️
- Flaggen: 🇩🇪 🇪🇺 🇯🇵 🇨🇳

### 6. Mathematik
- Inline: $E = mc^2$
- Block: $$\int_0^\infty e^{-x^2} dx$$

### 7. Code mit Unicode
- Python mit chinesischen Kommentaren
- JavaScript mit japanischen/koreanischen Strings

## Erwartetes Ergebnis

- ✅ PDF erfolgreich generiert: `test-single-file.pdf`
- ✅ Alle Schriftsysteme korrekt dargestellt (Font-Fallback)
- ✅ Breite Tabellen automatisch skaliert oder rotiert
- ✅ Lange Tabellen über mehrere Seiten verteilt
- ✅ LaTeX-Sonderzeichen korrekt escaped
- ✅ Emojis mit Twemoji-Font gerendert
- ✅ Mathematische Formeln korrekt gesetzt
- ✅ Keine Kompilierungsfehler
- ✅ Exit Code 0

## Test-Abdeckung

- **Single File**: ✅ Ja (ohne GitBook-Struktur)
- **Dateiname mit Sonderzeichen**: ✅ Ja (&, \_, @, !)
- **Mehrsprachig**: ✅ 8 Schriftsysteme
- **Tabellen-Komplexität**: ✅ 1-100 Spalten, 5-50 Zeilen
- **LaTeX-Escaping**: ✅ Ja
- **Emojis**: ✅ Ja
- **Mathematik**: ✅ Ja
- **Unicode in Code**: ✅ Ja
