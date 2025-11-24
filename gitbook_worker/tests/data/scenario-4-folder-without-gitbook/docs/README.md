# Documentation Overview

Dies ist ein Ordner ohne GitBook-Struktur (kein `book.json`, kein `SUMMARY.md`).

## Purpose

Dieses Szenario testet den **Fallback-Modus** des Publishers:

- Automatisches Sammeln aller `.md` Dateien
- Sortierung nach Dateinamen
- README.md wird priorisiert (wenn vorhanden)
- Keine explizite Reihenfolge definiert

## Expected Behavior

Der Publisher sollte:

1. ✅ Alle `.md` Dateien im Ordner finden
2. ✅ README.md an erste Stelle setzen
3. ✅ Andere Dateien alphabetisch sortieren
4. ✅ PDF ohne SUMMARY-Struktur generieren
5. ✅ Seitenumbrüche zwischen Dateien einfügen
