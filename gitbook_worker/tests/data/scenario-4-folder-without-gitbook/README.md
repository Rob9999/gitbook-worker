# Scenario 4: Folder Without GitBook

Testet einen Ordner ohne GitBook-Struktur (kein `book.json`, kein `SUMMARY.md`).

## Struktur

```
scenario-4-folder-without-gitbook/
├── publish.yml
└── docs/
    ├── README.md
    ├── 01-getting-started.md
    ├── 02-api-reference.md
    └── 03-advanced-topics.md
```

## Was wird getestet?

### 1. Fallback-Modus

Ohne `book.json` und `SUMMARY.md` muss der Publisher:

- ✅ Alle `.md` Dateien automatisch finden
- ✅ README.md an erste Stelle setzen
- ✅ Andere Dateien alphabetisch sortieren
- ✅ Seitenumbrüche zwischen Dateien einfügen

### 2. Datei-Reihenfolge

Erwartete Reihenfolge im PDF:

1. README.md (priorisiert)
2. 01-getting-started.md (alphabetisch)
3. 02-api-reference.md (alphabetisch)
4. 03-advanced-topics.md (alphabetisch)

### 3. Inhalts-Features

#### 01-getting-started.md
- Installation & Konfiguration
- Code-Blöcke (Bash, Config-Files)
- Mehrsprachige Texte (Deutsch, English, 日本語, 中文)
- Einfache Tabellen

#### 02-api-reference.md
- REST API Dokumentation
- JSON-Beispiele
- Query-Parameter-Tabelle
- Error-Codes mit Emojis (✅, ❌, 🔒, etc.)
- WebSocket Events
- Mathematische Formeln (Rate Limiting)
- Mehrsprachige API-Antworten

#### 03-advanced-topics.md
- Performance-Optimierung (Indexing, Caching, Load Balancing)
- Security Best Practices
- Microservices-Architektur (ASCII-Diagramme)
- Code mit Unicode-Kommentaren (Python, TypeScript)
- Monitoring & Observability
- Internationalisierung (5+ Sprachen)
- Deployment-Strategien
- Komplexe Tabellen
- Mathematische Formeln

## Test-Abdeckung

| Feature | Status | Details |
|---------|--------|---------|
| Folder ohne book.json | ✅ | Fallback-Modus |
| README.md Priorisierung | ✅ | Erste Datei |
| Alphabetische Sortierung | ✅ | 01-, 02-, 03- |
| Mehrsprachig | ✅ | 5 Sprachen |
| Code-Blöcke | ✅ | Bash, SQL, Python, TypeScript, JavaScript |
| Tabellen | ✅ | Klein bis mittelgroß |
| Emojis | ✅ | Gesichter, Symbole, Flaggen |
| Mathematik | ✅ | Inline & Block |
| ASCII-Diagramme | ✅ | Service-Architektur |

## Erwartetes Ergebnis

- ✅ PDF erfolgreich generiert: `test-folder-fallback.pdf`
- ✅ README.md ist erste Seite
- ✅ Dateien in korrekter Reihenfolge (01, 02, 03)
- ✅ Seitenumbrüche zwischen Dateien
- ✅ Alle Schriftsysteme korrekt dargestellt
- ✅ Code-Highlighting funktioniert
- ✅ Tabellen korrekt formatiert
- ✅ Emojis gerendert
- ✅ Mathematische Formeln gesetzt
- ✅ Exit Code 0

## Unterschied zu Scenario 1

| Feature | Scenario 1 | Scenario 4 |
|---------|------------|------------|
| book.json | ✅ Ja | ❌ Nein |
| SUMMARY.md | ✅ Ja | ❌ Nein |
| Datei-Reihenfolge | Explizit | Automatisch |
| root Property | content/ | docs/ (auto) |
| Use Case | Strukturierte Bücher | Ad-hoc Docs |
