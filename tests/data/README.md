# Test Data

Sample markdown and CSV files used for integration and converter tests.

## Publishing Test Scenarios

Dieses Verzeichnis enthält isolierte Testdaten für verschiedene Publishing-Szenarien.

### `scenario-1-single-gitbook/`
**Single GitBook mit book.json**

Testet:
- Korrekte Auswertung von `book.json` (insbesondere `root: content/`)
- Einlesen von `SUMMARY.md` aus dem korrekten `root`-Verzeichnis
- Kombination mehrerer Markdown-Dateien gemäß SUMMARY
- LaTeX-Sonderzeichen im Titel und Content (& % $ # _ { } \)
- Emoji-Rendering (Standard und Flaggen)
- CJK-Font-Fallback

Dateien:
- `book.json` - GitBook-Konfiguration mit `root: content/`
- `publish.yml` - Publisher-Manifest mit `use_book_json: true`
- `content/SUMMARY.md` - Inhaltsverzeichnis
- `content/README.md` - Einführung
- `content/chapter-*.md` - Kapitel mit verschiedenen Markdown-Features

Erwartetes Ergebnis:
- ✅ Erfolgreicher PDF-Build
- ✅ Nur Dateien aus `content/` werden einbezogen
- ✅ Keine YAML-Parse-Fehler
- ✅ Keine LaTeX-Fehler bei Sonderzeichen

---

### `scenario-2-multi-gitbook/`
**Mehrere GitBooks in einem Repository**

Testet:
- Zwei separate GitBook-Projekte (project-a, project-b)
- Jedes Projekt mit eigener `book.json` und `content/`
- Array von Dokumenten in `publish.yml`
- Separate PDF-Generierung pro Projekt
- Keine Vermischung der Inhalte

Dateien:
- `publish.yml` - Manifest mit 2 Dokumenten
- `project-a/book.json` + `content/` - Backend-fokussiertes GitBook
- `project-b/book.json` + `content/` - Frontend-fokussiertes GitBook

Erwartetes Ergebnis:
- ✅ Zwei separate PDFs (`test-project-a.pdf`, `test-project-b.pdf`)
- ✅ Jedes PDF enthält nur eigene Inhalte
- ✅ Korrekte Titel aus jeweiliger `book.json`
- ✅ Exit Code 0

---

### `scenario-3-single-file/`
**Einzelne Markdown-Datei ohne GitBook-Struktur**

Testet:
- Single-File-Konvertierung (kein GitBook, kein Ordner)
- Dateiname mit Sonderzeichen (&, \_, @, !)
- 8 verschiedene Schriftsysteme (CJK, Kyrillisch, Arabisch, Griechisch, Hindi, Thai)
- Extreme Tabellen-Tests (1 bis 100 Spalten, 5 bis 50 Zeilen)
- Tabellen mit und ohne Überschriften
- LaTeX-Sonderzeichen, Emojis, Mathematik
- Code mit Unicode-Kommentaren

Dateien:
- `publish.yml` - Manifest für single file
- `complex-doc_with-special&chars@2024!.md` - Komplexe Test-Datei

Erwartetes Ergebnis:
- ✅ PDF erfolgreich generiert
- ✅ Alle Schriftsysteme korrekt dargestellt
- ✅ Breite Tabellen automatisch skaliert
- ✅ Lange Tabellen über mehrere Seiten
- ✅ Exit Code 0

---

### `scenario-4-folder-without-gitbook/`
**Ordner ohne book.json (Fallback-Modus)**

Testet:
- Ordner ohne `book.json` und ohne `SUMMARY.md`
- Automatisches Sammeln aller `.md` Dateien
- README.md Priorisierung (erste Datei)
- Alphabetische Sortierung der anderen Dateien
- Mehrsprachige Inhalte (5 Sprachen)
- API-Dokumentation mit REST/WebSocket
- Fortgeschrittene Themen (Microservices, Security, Monitoring)

Dateien:
- `publish.yml` - Manifest für Ordner
- `docs/README.md` - Wird zuerst eingefügt
- `docs/01-getting-started.md` - Getting Started Guide
- `docs/02-api-reference.md` - API Documentation
- `docs/03-advanced-topics.md` - Advanced Topics

Erwartetes Ergebnis:
- ✅ PDF erfolgreich generiert
- ✅ README.md an erster Stelle
- ✅ Dateien alphabetisch sortiert (01, 02, 03)
- ✅ Seitenumbrüche zwischen Dateien
- ✅ Exit Code 0
