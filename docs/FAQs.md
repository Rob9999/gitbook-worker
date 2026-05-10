---
version: 1.2.0
date: 2026-05-10
history:
  - "1.2.0: 2026-05-10 — FAQ #6 fuer Checkbox-/Textsymbol-Fallbacks in PDFs ergaenzt"
  - "1.1.0: 2026-02-08 — FAQ #1 aktualisiert: Auto-Detect & gitbook_rename-Key implementiert (v2.3.0)"
  - "1.0.0: 2026-02-08 — Initial FAQ from customer flat-file scenario"
---

# Frequently Asked Questions (FAQ)

## Inhaltsverzeichnis

1. [FileNotFoundError nach GitBook-Rename](#1-filenotfounderror-nach-gitbook-rename)
2. [project.license fehlt im Manifest](#2-projectlicense-fehlt-im-manifest)
3. [Profil-Fallback auf `default` statt `local`](#3-profil-fallback-auf-default-statt-local)
4. [Manifest-Version-Warnung (neuer als getestete)](#4-manifest-version-warnung-neuer-als-getestete)
5. [Sonderzeichen in Dateinamen (m², &, @, Leerzeichen)](#5-sonderzeichen-in-dateinamen)
6. [Checkbox-Symbole erscheinen im PDF als Rechtecke](#6-checkbox-symbole-erscheinen-im-pdf-als-rechtecke)

---

## 1. FileNotFoundError nach GitBook-Rename

### Symptom

```
ERROR Build-Fehler: [Errno 2] No such file or directory: '...\Habitats\My Document.md'
```

Die Datei existiert auf der Platte, aber der Publisher findet sie nicht.

### Ursache

Die Publishing-Pipeline führt standardmäßig einen **GitBook-Rename-Schritt** aus
(`gitbook_style.py rename`), der Verzeichnis- und Dateinamen normalisiert:

- Großbuchstaben → Kleinbuchstaben (`Habitats/` → `habitats/`)
- Leerzeichen → Bindestriche (`My Document.md` → `my-document.md`)
- CamelCase → kebab-case (`MarsGummiHaus/` → `marsgummihaus/`)

Die Pfade in `publish.yml` werden **nicht** automatisch angepasst. Dadurch
zeigt `path: ./Habitats/My Document.md` ins Leere, weil die Datei jetzt
unter `./habitats/my-document.md` liegt.

### Lösung

**Option A (empfohlen ab v2.3.0):** `gitbook_rename: false` in `publish.yml` setzen:

```yaml
version: "0.1.1"
gitbook_rename: false          # ← Rename-Schritt explizit deaktivieren

project:
  license: "CC BY 4.0"

publish:
  - path: ./Habitats/My Document.md
    out: My Document.pdf
    source_type: file
```

> **Ab v2.3.0** erkennt die Pipeline automatisch, wenn **alle** Publish-Einträge
> `source_type: file` sind, und überspringt den Rename-Schritt von selbst
> (Auto-Detect). Der explizite Key `gitbook_rename: false` dient als
> zusätzliche Absicherung oder wenn gemischte Einträge vorliegen.

**Option B:** Pfade in `publish.yml` bereits in Kleinbuchstaben/kebab-case angeben:

```yaml
publish:
  - path: ./habitats/my-document.md    # schon normalisiert
    out: my-document.pdf
    source_type: file
```

**Option C:** Ordner von Anfang an in Kleinbuchstaben benennen:

```
repo/
├── habitats/          # nicht Habitats/
│   ├── document-a.md
│   └── document-b.md
└── publish.yml
```

### Hintergrund

Der GitBook-Rename ist für GitBook-kompatible Buchprojekte gedacht
(`source_type: folder` + `use_book_json: true`). Für flache
Einzeldatei-Szenarien (`source_type: file`) ist er in der Regel unnötig
und kann destruktiv wirken.

> **✅ Gelöst in v2.3.0:** Der Rename-Schritt wird automatisch übersprungen,
> wenn alle Publish-Einträge `source_type: file` sind (Auto-Detect).
> Zusätzlich kann `gitbook_rename: false` als Top-Level-Key in `publish.yml`
> gesetzt werden.

---

## 2. project.license fehlt im Manifest

### Symptom

```
CommandError: project.license fehlt im Manifest – bitte in publish.yml unter project.license setzen
```

### Ursache

`project.license` ist ein **Pflichtfeld**. Die Pipeline bricht beim
Publisher-Schritt ab, wenn es fehlt.

### Lösung

In `publish.yml` einen `project`-Block ergänzen:

```yaml
project:
  name: "Mein Projekt"
  license: "CC-BY-SA-4.0"    # Pflicht!
  authors:
    - "Autorenname"
```

---

## 3. Profil-Fallback auf `default` statt `local`

### Symptom

Man gibt `--profile local` an, aber im Log steht:

```
Starte Orchestrator-Profil 'default' mit Schritten: check_if_to_publish,
ensure_readme, update_citation, converter, engineering-document-formatter,
generate_attribution, publisher
```

Unerwartete Schritte wie `ensure_readme` erzeugen dutzende `README.md`-Dateien
in allen Unterverzeichnissen.

### Ursache

In der `publish.yml` fehlt das Profil `local`. Der Orchestrator fällt dann
auf das `default`-Profil zurück, das typischerweise alle Schritte enthält.

### Lösung

Ein `local`-Profil in `publish.yml` definieren:

```yaml
profiles:
  local:
    description: Lokale Ausführung ohne Docker.
    steps:
      - converter
      - publisher
```

Für reine Einzeldatei-Szenarien kann sogar `converter` entfallen:

```yaml
profiles:
  local:
    steps:
      - publisher
```

---

## 4. Manifest-Version-Warnung (neuer als getestete)

### Symptom

```
WARNING Manifest-Version 0.1.1 ist neuer als die getestete 0.1.0 – versuche fortzufahren.
```

### Ursache

Die installierte Version von gitbook-worker kennt nur Schema-Version `0.1.0`.
Die `publish.yml` deklariert `version: 0.1.1`.

### Lösung

gitbook-worker auf die neueste Version aktualisieren:

```bash
pip install --upgrade gitbook-worker
# oder
pip install gitbook_worker-2.2.1-py3-none-any.whl
```

Die Warnung ist **nicht blockierend** — der Publisher versucht fortzufahren.
Funktional gibt es zwischen 0.1.0 und 0.1.1 keine Breaking Changes.

---

## 5. Sonderzeichen in Dateinamen

### Unterstützte Zeichen

gitbook-worker unterstützt Sonderzeichen in Dateinamen, darunter:

- Unicode-Zeichen: `m²`, `ü`, `ö`, `ä`
- Satzzeichen: `&`, `@`, `!`
- Leerzeichen

**Beispiel:**

```yaml
publish:
  - path: "./Habitats/Das 1000 m² Mars Gummi-Glashaus v2.md"
    out: "Das 1000 m² Mars Gummi-Glashaus v2.pdf"
```

### Vorsicht bei GitBook-Rename

Der GitBook-Rename-Schritt normalisiert Dateinamen (Kleinbuchstaben,
Bindestriche statt Leerzeichen). Dateien mit Sonderzeichen werden
umbenannt, z. B.:

```
Das 1000 m² Mars Gummi-Glashaus v2.md
→ das-1000-m²-mars-gummi-glashaus-v2.md
```

Wenn `source_type: file` verwendet wird, empfiehlt sich `--no-gitbook-rename`
(siehe FAQ #1).

### Empfehlung für maximale Kompatibilität

Für Dateinamen, die über verschiedene Betriebssysteme und CI-Systeme
portabel sein sollen:

- ASCII-Kleinbuchstaben, Ziffern, Bindestriche
- Keine Leerzeichen, keine Unicode-Sonderzeichen
- Beispiel: `mars-rubber-glass-house-v2.md`

---

## 6. Checkbox-Symbole erscheinen im PDF als Rechtecke

### Symptom

Markdown-Tasklisten oder Textsymbole wie `☐`, `☑`, `☒`, `✓` oder `✔`
erscheinen im PDF als leere oder fremd wirkende Rechtecke.

### Ursache

Diese Zeichen sind Textsymbole, keine Farb-Emojis. Der Serif-Hauptfont deckt
einige davon nicht ab. Deshalb muss der PDF-Fallback eine Sans-Schrift
enthalten, die diese Symbole liefert.

### Lösung

Bei eigenen `publish.yml`-Overrides `DejaVu Sans:mode=harf` in die
Fallback-Kette aufnehmen, vor script-spezifischen ERDA-Fallbacks:

```yaml
pdf_options:
  main_font: DejaVu Serif
  sans_font: DejaVu Sans
  mono_font: DejaVu Sans Mono
  mainfont_fallback: Twemoji Mozilla:mode=harf; DejaVu Sans:mode=harf; ERDA CC-BY CJK:mode=harf
```

Der Publisher routet Checkbox-/Checkmark-Symbole zusaetzlich ueber
`text-symbols.lua` durch den konfigurierten Sans-Font. So bleiben
Markdown-Tasklisten und literal geschriebene Checkboxen im PDF sichtbar und im
Textlayer extrahierbar.
