# Tests

Dieses Verzeichnis enthält automatisierte Tests für den GitBook Worker und die Publishing-Tools.

## Test-Struktur

### Unit & Integration Tests

- **emoji/** - Tests für Emoji-Verarbeitung und Rendering
- **workflow_orchestrator/** - Tests für den Workflow-Orchestrator  
- **test_a1_pdf.py** - Tests für A1-Papierformat-PDF-Generierung
- **test_appendix_layout_inspector.py** - Tests für Anhang-Layout-Inspektion
- **test_csv_converter.py** - Tests für CSV-zu-Markdown/Chart-Konvertierung
- **test_gitbook_style.py** - Tests für GitBook-Stil-Verarbeitung
- **test_markdown_combiner.py** - Tests für Markdown-Zusammenfügung
- **test_paper_info.py** - Tests für Papierformat-Informationen
- **test_pipeline.py** - Tests für die Publishing-Pipeline
- **test_preprocess_md.py** - Tests für Markdown-Vorverarbeitung
- **test_publisher.py** - Tests für den PDF-Publisher
- **test_set_publish_flag.py** - Tests für das Publish-Flag-System

### Slow/Integration Tests

Die folgenden Tests sind als `@pytest.mark.slow` markiert und werden standardmäßig **nicht** ausgeführt:

- **test_documents_publishing.py** - Vollständige Dokumenten-Publishing (275+ Dokumente)
- **test_exact_table_dimensions.py** - Exakte Tabellendimensionen-Tests (LaTeX)
- **test_pdf_integration.py** - End-to-End PDF-Generierungs-Tests
- **test_docker_container.py** - Docker-Container-Tests (Skip wenn INSIDE_DOCKER)

## Lokales Ausführen

### Alle schnellen Tests

```bash
cd .github/gitbook_worker/tests
pytest -q -m "not slow"
```

### Alle Tests (inkl. langsame)

```bash
cd .github/gitbook_worker/tests
pytest -q
```

### Spezifische Tests

```bash
pytest test_publisher.py -v
pytest emoji/ -v
pytest -k "pandoc" -v
```

## CI/CD

Die Tests werden in GitHub Actions über `.github/workflows/test.yml` ausgeführt:

- **unit-tests**: Schnelle Unit-Tests im Docker-Container (`-m 'not slow'`)
- **integration-tests**: Integration-Tests mit vollständiger Toolchain (Pandoc, LaTeX, etc.)
- **emoji-harness**: Emoji-Compliance-Tests  
- **qa**: Dokumentations-QA (Links, Quellen)

## Voraussetzungen

### Für Unit-Tests
- Python 3.11+
- pytest
- Abhängigkeiten aus `requirements.txt`

### Für Integration-Tests
- Pandoc 3.1.11+
- LuaLaTeX (TeX Live)
- wkhtmltopdf
- pdfinfo (poppler-utils)
- Fonts: DejaVu, OpenMoji, Twemoji

## Bekannte Probleme

1. **Font-Verfügbarkeit**: Einige Tests erwarten `ERDA CC-BY CJK`, akzeptieren aber `DejaVu Sans` als Fallback
2. **Windows-Encoding**: Tests können Encoding-Probleme bei Umlauten in LaTeX-Ausgaben haben
3. **Resource-Pfade**: PDF-Tests benötigen korrekte Pfade zu `.sty`-Dateien

## Test-Marker

- `@pytest.mark.slow` - Langsame Tests (PDF-Generierung, LaTeX-Kompilierung)
- `@pytest.mark.skipif` - Tests die von externer Software abhängen (Pandoc, LaTeX, Docker)

## Hinzufügen neuer Tests

1. Neue Test-Datei in `tests/` erstellen
2. Bei Bedarf `@pytest.mark.slow` hinzufügen
3. Fixtures aus `conftest.py` nutzen (`logger`, `output_dir`, `artifact_dir`)
4. Tests lokal und in CI ausführen lassen

## Test-Ergebnisse

Stand: November 2025
- **88 Tests** bestehen bei `-m 'not slow'`
- **7 Tests** als `slow` markiert (werden nur bei Bedarf ausgeführt)
- **1 Test** skipped (Docker-Container, nur in CI relevant)
