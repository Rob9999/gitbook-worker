# Customer Example: Flat Per-Document PDF

Dieses Beispiel zeigt, wie einzelne Markdown-Dateien jeweils ein eigenes PDF erzeugen —
**ohne** GitBook-Struktur (`book.json`, `SUMMARY.md`).

## Struktur

```
customer-flat/
├── .vscode/
│   └── launch.json          ← Debug-Konfigurationen
├── content.yaml              ← Content-Registry für den Orchestrator
├── publish.yml               ← Manifest: 2 Dateien → 2 PDFs
├── Habitats/
│   ├── the-best-marsian-housing.md
│   └── the-more-best-marsian-housing.md
└── publish/                  ← Ausgabe (wird automatisch angelegt)
    ├── the-best-marsian-housing.pdf
    └── the-more-best-marsian-housing.pdf
```

## Ausführung

### Variante 1: Via content.yaml (empfohlen)

```bash
python -m gitbook_worker.tools.workflow_orchestrator run \
    --root . \
    --content-config customer-flat/content.yaml \
    --lang customer-flat \
    --profile local
```

### Variante 2: Manifest direkt

```bash
python -m gitbook_worker.tools.workflow_orchestrator run \
    --root . \
    --manifest customer-flat/publish.yml \
    --profile local
```

### Variante 3: VS Code Debugger

Öffne die Run-Ansicht (Ctrl+Shift+D) und wähle:
- **Build All Habitats PDFs (local)** — via content.yaml
- **Build All Habitats PDFs (manifest direct)** — via publish.yml

## Schlüsselprinzip

Jeder `publish`-Eintrag mit `source_type: file` erzeugt **ein** PDF aus **einer** Datei.
Der `path` ist relativ zur `publish.yml` — der Ordnername (`Habitats/`, `docs/`, o.ä.) ist frei wählbar.

## Anpassung

Neue Dokumente hinzufügen: Einfach einen weiteren Eintrag in `publish.yml` ergänzen:

```yaml
  - path: ./Habitats/mein-neues-dokument.md
    out: mein-neues-dokument.pdf
    out_dir: ./publish
    build: true
    source_type: file
```
