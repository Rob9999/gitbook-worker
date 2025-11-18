# Scenario 2: Multi-GitBook

Testet mehrere GitBook-Projekte in einem Repository.

## Struktur

```
scenario-2-multi-gitbook/
├── publish.yml           # Manifest mit 2 Dokumenten
├── project-a/            # Backend-fokussiertes GitBook
│   ├── book.json
│   └── content/
│       ├── README.md
│       ├── SUMMARY.md
│       ├── chapter-1-architecture.md
│       └── chapter-2-api.md
└── project-b/            # Frontend-fokussiertes GitBook
    ├── book.json
    └── content/
        ├── README.md
        ├── SUMMARY.md
        ├── chapter-1-components.md
        └── chapter-2-state.md
```

## Was wird getestet?

1. **Mehrere GitBooks**: Zwei separate Projekte mit eigenen `book.json`
2. **Separate Konfiguration**: Jedes Projekt hat eigenes `root: content/`
3. **Separate Inhalte**: Project A (Backend), Project B (Frontend)
4. **Parallele Verarbeitung**: Beide werden zu separaten PDFs gebaut
5. **publish.yml mit mehreren Einträgen**: Testet Array von Dokumenten

## Erwartetes Ergebnis

- ✅ Zwei PDFs: `test-project-a.pdf` und `test-project-b.pdf`
- ✅ Jedes PDF enthält nur Inhalte des jeweiligen Projekts
- ✅ Keine Vermischung der Inhalte
- ✅ Beide PDFs haben korrekten Titel aus `book.json`
- ✅ Exit Code 0

## Test-Abdeckung

- **Multi-GitBook**: ✅ Ja (2 Projekte)
- **Separate book.json**: ✅ Ja
- **Separate SUMMARY.md**: ✅ Ja
- **Code-Blöcke**: ✅ Python & TypeScript
- **Tabellen**: ✅ Ja
- **Mathematik**: ✅ Ja (LaTeX-Formeln)
- **Emojis**: ✅ Ja (✅, 🚀, ⚠️, etc.)
- **Sonderzeichen**: ✅ Ja (≥, ≈, etc.)
