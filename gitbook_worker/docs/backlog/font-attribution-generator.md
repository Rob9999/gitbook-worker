---
title: Font Attribution & License Files Generator
description: Automated generation of ATTRIBUTION.md and LICENSE files from fonts.yml
date: 2024-12-02
version: 1.0.0
status: backlog
priority: medium
estimate: 6-8 hours
related:
  - font-storage-dynamic-generation.md
  - AGENTS.md (sections 12-14)
  - gitbook_worker/defaults/fonts.yml
history:
  - version: 1.0.0
    date: 2024-12-02
    changes: Initial backlog document for font attribution automation
---

# Font Attribution & License Files Generator

## Überblick

**Problem:** Attribution und License-Dateien werden manuell gepflegt und können mit fonts.yml inkonsistent werden.

**Lösung:** Generator liest fonts.yml und erstellt automatisch:
1. `ATTRIBUTION.md` mit vollständiger Font-Tabelle
2. Individuell `LICENSE-*` Dateien für jede Font-Lizenz
3. Copy-Operation in manifest-definierte `out_dir` Verzeichnisse

**Prinzip:** fonts.yml ist Single Source of Truth → Attribution und Licenses werden generiert, nicht manuell gepflegt.

## Motivation & Business Value

### Warum automatisieren?

1. **License Compliance (kritisch)**
   - AGENTS.md verlangt: "Jederzeit muss der Publizierer in der Lage sein den Attributions Pflichten und Lizenzpflichten nachzukommen"
   - Manuelle Pflege führt zu Inkonsistenzen zwischen fonts.yml und ATTRIBUTION.md
   - Fehler bei License-Attribution können rechtliche Folgen haben

2. **DRY Principle**
   - Font-Metadaten (Name, Version, License, URLs) existieren bereits in fonts.yml
   - Duplikation in ATTRIBUTION.md und LICENSE-FONTS ist fehleranfällig

3. **Workflow-Integration**
   - Nach jedem `azd up` oder PDF-Build sollten Attribution-Dateien im out_dir liegen
   - Publisher kann direkt aus fonts.yml generieren → keine separaten Update-Schritte

4. **Versionierung & Nachvollziehbarkeit**
   - Generator kann Git-Hash/Timestamp hinzufügen
   - Automatische Erkennung neuer/geänderter Fonts
   - Change Log für Attribution-Updates

### Success Metrics

- ✅ Keine manuellen Edits in ATTRIBUTION.md nötig (außer zusätzlichen Assets)
- ✅ LICENSE-* Dateien werden automatisch aus license_url heruntergeladen oder aus Vorlagen generiert
- ✅ `azd up` oder `orchestrator run` kopiert Attribution automatisch ins publish/
- ✅ 100% Konsistenz zwischen fonts.yml und generierten Files
- ✅ CI/CD-Check warnt bei fehlenden License-Feldern in fonts.yml

## Requirements

### Functional Requirements

1. **ATTRIBUTION.md Generator**
   - Input: fonts.yml (alle fonts.* Einträge)
   - Output: Markdown-Tabelle mit Spalten:
     * Asset Name
     * Version
     * License (kurz: "CC BY 4.0", "MIT", "Bitstream Vera + PD")
     * Source URL (mit Link)
     * Usage Note (aus fonts.yml)
   - Template: Bestehende ATTRIBUTION.md als Vorlage (Header, Footer, Pflegehinweise erhalten)
   - Sortierung: Alphabetisch nach Asset Name oder nach Kategorie (EMOJI, CJK, SERIF, SANS, MONO)

2. **LICENSE File Generator**
   - Pro Font-Lizenz: Separate LICENSE-<IDENTIFIER> Datei
   - Beispiele:
     * LICENSE-CC-BY-4.0 (Twitter Color Emoji, ERDA fonts)
     * LICENSE-BITSTREAM-VERA (DejaVu)
     * LICENSE-MIT (falls MIT-lizenzierte Fonts hinzukommen)
   - Inhalt: Vollständiger Lizenztext (entweder aus license_url fetchen oder aus lokalem Template)
   - Deduplizierung: Wenn mehrere Fonts dieselbe Lizenz haben → eine LICENSE-Datei, mehrfach referenziert

3. **Manifest Integration (publish.yml)**
   - Neue Option in publish.yml:
     ```yaml
     publish:
       - path: ./
         out_dir: ./publish
         generate_attribution: true  # Neu: Attribution & LICENSE ins out_dir
     ```
   - Generator kopiert/schreibt Dateien nach:
     * `{out_dir}/ATTRIBUTION.md`
     * `{out_dir}/LICENSE-CC-BY-4.0`
     * `{out_dir}/LICENSE-BITSTREAM-VERA`
     * etc.

4. **CLI Command**
   ```bash
   python -m gitbook_worker.tools.fonts_cli generate-attribution \
     --manifest de/publish.yml \
     --out-dir de/publish \
     --fonts-config gitbook_worker/defaults/fonts.yml
   ```

5. **Orchestrator Integration**
   - Neuer Step in orchestrator.py: `generate_attribution`
   - Wird vor `publisher` ausgeführt (damit ATTRIBUTION.md im PDF referenziert werden kann)
   - Nur wenn `generate_attribution: true` in publish.yml

### Non-Functional Requirements

1. **Performance**
   - Generator < 2 Sekunden für 7 Fonts
   - LICENSE-URL-Fetch: Cache lokal, nur beim ersten Mal herunterladen

2. **Error Handling**
   - Warnung wenn font.license oder font.license_url fehlt
   - Fehler wenn license_url nicht erreichbar (mit Fallback auf lokales Template)
   - Validierung: Alle fonts.yml Fonts haben vollständige Metadaten

3. **Extensibility**
   - Template-System für ATTRIBUTION.md (Jinja2 oder Python f-strings)
   - LICENSE-Templates für gängige Lizenzen (CC-BY, MIT, OFL, Bitstream Vera)
   - Plugin-Architektur falls später nicht-Font-Assets hinzukommen

4. **Testing**
   - Unit Tests für Generator-Logik (fonts.yml → Markdown-Tabelle)
   - Integration Test: Orchestrator run generiert Attribution korrekt
   - Fixture: Test-fonts.yml mit Mock-Fonts

## Design

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      fonts.yml                               │
│  (Single Source of Truth für Font-Metadaten)                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│          FontAttributionGenerator                            │
│  ┌──────────────────────────────────────────────────┐       │
│  │ 1. load_fonts_config(fonts.yml)                  │       │
│  │ 2. generate_attribution_table()                  │       │
│  │ 3. fetch_license_texts()                         │       │
│  │ 4. render_attribution_md(template)               │       │
│  │ 5. write_license_files(out_dir)                  │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 Output Files                                 │
│  - {out_dir}/ATTRIBUTION.md                                 │
│  - {out_dir}/LICENSE-CC-BY-4.0                              │
│  - {out_dir}/LICENSE-BITSTREAM-VERA                         │
│  - {out_dir}/LICENSE-MIT                                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. FontAttributionGenerator Class

```python
# gitbook_worker/tools/fonts/attribution_generator.py

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import yaml
import requests
from jinja2 import Template

@dataclass
class FontAttribution:
    """Structured font attribution data from fonts.yml"""
    name: str
    version: str
    license: str
    license_url: str
    source_url: str | None
    copyright: str | None
    usage_note: str | None
    category: str  # EMOJI, CJK, SERIF, SANS, MONO

class FontAttributionGenerator:
    def __init__(self, fonts_config_path: Path, template_path: Path | None = None):
        self.fonts_config = self._load_fonts_config(fonts_config_path)
        self.template = self._load_template(template_path)
        self.license_cache: Dict[str, str] = {}  # URL -> License Text
    
    def _load_fonts_config(self, path: Path) -> Dict:
        """Load fonts.yml and extract all font entries"""
        with open(path) as f:
            config = yaml.safe_load(f)
        return config.get("fonts", {})
    
    def _load_template(self, path: Path | None) -> Template:
        """Load Jinja2 template for ATTRIBUTION.md"""
        if path and path.exists():
            with open(path) as f:
                return Template(f.read())
        # Fallback: Use default template
        return Template(DEFAULT_ATTRIBUTION_TEMPLATE)
    
    def generate_attributions(self) -> List[FontAttribution]:
        """Convert fonts.yml entries to FontAttribution objects"""
        attributions = []
        for category, font_data in self.fonts_config.items():
            attribution = FontAttribution(
                name=font_data["name"],
                version=font_data.get("version", "unknown"),
                license=font_data["license"],
                license_url=font_data["license_url"],
                source_url=font_data.get("source_url"),
                copyright=font_data.get("copyright"),
                usage_note=font_data.get("usage_note"),
                category=category
            )
            attributions.append(attribution)
        return attributions
    
    def fetch_license_text(self, license_url: str) -> str:
        """Fetch license text from URL or return cached version"""
        if license_url in self.license_cache:
            return self.license_cache[license_url]
        
        try:
            response = requests.get(license_url, timeout=10)
            response.raise_for_status()
            text = response.text
            self.license_cache[license_url] = text
            return text
        except requests.RequestException as e:
            # Fallback to local template if URL fails
            logger.warning(f"Failed to fetch license from {license_url}: {e}")
            return self._get_local_license_template(license_url)
    
    def _get_local_license_template(self, license_url: str) -> str:
        """Return local license template based on URL pattern"""
        if "creativecommons.org/licenses/by/4.0" in license_url:
            return LICENSE_TEMPLATE_CC_BY_4_0
        elif "dejavu-fonts.github.io/License.html" in license_url:
            return LICENSE_TEMPLATE_BITSTREAM_VERA
        elif "opensource.org/licenses/MIT" in license_url:
            return LICENSE_TEMPLATE_MIT
        else:
            raise ValueError(f"No local template for license: {license_url}")
    
    def generate_attribution_md(self, attributions: List[FontAttribution]) -> str:
        """Render ATTRIBUTION.md from template"""
        return self.template.render(fonts=attributions)
    
    def generate_license_files(self, attributions: List[FontAttribution]) -> Dict[str, str]:
        """Generate LICENSE-* files (filename -> content)"""
        license_files = {}
        seen_licenses = set()
        
        for attr in attributions:
            license_id = self._license_id_from_name(attr.license)
            if license_id in seen_licenses:
                continue  # Already generated this license file
            
            filename = f"LICENSE-{license_id}"
            license_text = self.fetch_license_text(attr.license_url)
            license_files[filename] = license_text
            seen_licenses.add(license_id)
        
        return license_files
    
    def _license_id_from_name(self, license_name: str) -> str:
        """Convert license name to filename-safe ID"""
        # "CC BY 4.0" -> "CC-BY-4.0"
        # "Bitstream Vera License + Public Domain" -> "BITSTREAM-VERA"
        if "CC BY" in license_name:
            return "CC-BY-4.0"
        elif "Bitstream Vera" in license_name:
            return "BITSTREAM-VERA"
        elif "MIT" in license_name:
            return "MIT"
        elif "OFL" in license_name:
            return "OFL"
        else:
            # Fallback: Sanitize license name
            return license_name.upper().replace(" ", "-").replace("+", "")
    
    def write_files(self, out_dir: Path):
        """Write ATTRIBUTION.md and LICENSE-* files to out_dir"""
        out_dir.mkdir(parents=True, exist_ok=True)
        
        attributions = self.generate_attributions()
        
        # Write ATTRIBUTION.md
        attribution_md = self.generate_attribution_md(attributions)
        (out_dir / "ATTRIBUTION.md").write_text(attribution_md, encoding="utf-8")
        logger.info(f"✓ Generated {out_dir}/ATTRIBUTION.md")
        
        # Write LICENSE-* files
        license_files = self.generate_license_files(attributions)
        for filename, content in license_files.items():
            (out_dir / filename).write_text(content, encoding="utf-8")
            logger.info(f"✓ Generated {out_dir}/{filename}")
```

#### 2. ATTRIBUTION.md Template (Jinja2)

```jinja2
{# gitbook_worker/tools/fonts/templates/attribution.md.j2 #}
<!-- License: CC BY-SA 4.0 (Text); MIT (Code); CC BY 4.0/MIT (Fonts) -->
# Medien- & Lizenz-Attribution

**Lizenzmatrix (Kurz):** Texte = **CC BY-SA 4.0** · Code = **MIT** · Fonts (eigene) = **CC BY 4.0 / MIT** · Emojis = **Twemoji (CC BY 4.0)**.
Details: siehe **Anhang J: Lizenz & Offenheit** sowie die LICENSE-Dateien.

## Überblick

| Kategorie | Asset | Version | Lizenz | Quelle | Verwendung |
| --- | --- | --- | --- | --- | --- |
{% for font in fonts | sort(attribute='category') -%}
| {{ font.category }} | {{ font.name }} | {{ font.version }} | {{ font.license }} | {% if font.source_url %}[{{ font.source_url }}]({{ font.source_url }}){% else %}Projekt-intern{% endif %} | {{ font.usage_note or 'Font für Textdarstellung' }} |
{% endfor %}

> **Hinweise:**
> - Alle Fonts sind explizit in `gitbook_worker/defaults/fonts.yml` konfiguriert
> - Keine hardcodierten Fallback-Fonts (garantiert License Compliance)
> - Diese Datei wurde automatisch aus fonts.yml generiert am {{ generation_timestamp }}

## Pflegehinweise

### ⚠️ Attribution-Hierarchie beachten

Diese Datei ist **automatisch generiert** aus `gitbook_worker/defaults/fonts.yml`.  
**Keine manuellen Edits** – Änderungen nur in fonts.yml vornehmen!

Bei Änderungen an Fonts:
1. **`fonts.yml`** aktualisieren (name, version, license, license_url, paths, etc.)
2. Generator ausführen: `python -m gitbook_worker.tools.fonts_cli generate-attribution`
3. Commit mit DCO: `git commit -s -m "feat: Update font XYZ to version A.B.C"`

Falls zusätzliche Assets (Bilder, Logos) hinzukommen:
- Manuell in Tabelle eintragen (unterhalb Font-Einträge)
- Oder fonts.yml erweitern um `assets:` Sektion (zukünftig)

**Hinweis:** Lizenz- und Quellenangaben müssen mit den tatsächlichen Dateien im Repo übereinstimmen.
```

#### 3. CLI Command Integration

```python
# gitbook_worker/tools/fonts_cli.py (extend existing)

@click.group()
def fonts_cli():
    """Font management utilities"""
    pass

@fonts_cli.command(name="generate-attribution")
@click.option("--fonts-config", type=click.Path(exists=True), 
              default="gitbook_worker/defaults/fonts.yml",
              help="Path to fonts.yml")
@click.option("--out-dir", type=click.Path(), required=True,
              help="Output directory for ATTRIBUTION.md and LICENSE files")
@click.option("--template", type=click.Path(exists=True), required=False,
              help="Custom Jinja2 template for ATTRIBUTION.md")
def generate_attribution_cmd(fonts_config: str, out_dir: str, template: str | None):
    """Generate ATTRIBUTION.md and LICENSE files from fonts.yml"""
    from gitbook_worker.tools.fonts.attribution_generator import FontAttributionGenerator
    
    generator = FontAttributionGenerator(
        fonts_config_path=Path(fonts_config),
        template_path=Path(template) if template else None
    )
    
    generator.write_files(out_dir=Path(out_dir))
    click.echo(f"✓ Attribution files written to {out_dir}")
```

#### 4. Orchestrator Integration

```python
# orchestrator.py (add new step)

def _step_generate_attribution(ctx: Context):
    """Generate ATTRIBUTION.md and LICENSE files from fonts.yml"""
    logger.info("Schritt 'generate_attribution' starten")
    
    manifest = ctx.manifest
    for entry in manifest.get("publish", []):
        if not entry.get("generate_attribution", False):
            logger.debug(f"Skipping attribution generation for {entry['path']}")
            continue
        
        out_dir = Path(entry["out_dir"])
        fonts_config = Path("gitbook_worker/defaults/fonts.yml")
        
        cmd = [
            sys.executable, "-m", "gitbook_worker.tools.fonts_cli",
            "generate-attribution",
            "--fonts-config", str(fonts_config),
            "--out-dir", str(out_dir)
        ]
        
        ctx.run_command(cmd)
        logger.info(f"✓ Attribution generated for {out_dir}")
```

### Templates & Fallbacks

#### LICENSE-CC-BY-4.0 Template

```python
LICENSE_TEMPLATE_CC_BY_4_0 = """
Creative Commons Attribution 4.0 International (CC BY 4.0)
===========================================================

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license,
  and indicate if changes were made.

This is a human-readable summary. See the full license at the URL above.
"""
```

#### LICENSE-BITSTREAM-VERA Template

```python
LICENSE_TEMPLATE_BITSTREAM_VERA = """
Bitstream Vera Fonts License
=============================

Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved.
DejaVu changes are in public domain.

Permission is hereby granted, free of charge, to any person obtaining a copy
of the fonts accompanying this license ("Fonts") and associated documentation
files (the "Font Software"), to reproduce and distribute the Font Software,
including without limitation the rights to use, copy, merge, publish,
distribute, and/or sell copies of the Font Software, and to permit persons
to whom the Font Software is furnished to do so, subject to the following
conditions:

The Fonts must be distributed entirely with this copyright and license notice.

The Font Software may not be sold separately.

THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF COPYRIGHT, PATENT,
TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL BITSTREAM OR THE GNOME FOUNDATION
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, INCLUDING ANY GENERAL,
SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF THE USE OR INABILITY TO
USE THE FONT SOFTWARE OR FROM OTHER DEALINGS IN THE FONT SOFTWARE.
"""
```

### Data Flow

```
User: azd up / orchestrator run
  │
  ├─> orchestrator.py: _step_generate_attribution()
  │     │
  │     ├─> fonts_cli.py: generate-attribution
  │     │     │
  │     │     ├─> FontAttributionGenerator.load_fonts_config(fonts.yml)
  │     │     ├─> FontAttributionGenerator.generate_attributions()
  │     │     ├─> FontAttributionGenerator.fetch_license_text() [cache]
  │     │     ├─> FontAttributionGenerator.generate_attribution_md(template)
  │     │     ├─> FontAttributionGenerator.generate_license_files()
  │     │     └─> Write to {out_dir}/
  │     │
  │     └─> Log: "✓ Attribution generated for de/publish"
  │
  └─> orchestrator.py: _step_publisher()
        └─> Publisher finds ATTRIBUTION.md in publish/ for PDF embedding
```

## Implementation Plan

### Phase 1: Core Generator (3-4 hours)

**Files to create:**
- `gitbook_worker/tools/fonts/attribution_generator.py` (Core logic)
- `gitbook_worker/tools/fonts/templates/attribution.md.j2` (Jinja2 template)
- `gitbook_worker/tools/fonts/templates/licenses.py` (License text constants)

**Tasks:**
1. Implement `FontAttributionGenerator` class
2. Implement `_load_fonts_config()` (parse fonts.yml)
3. Implement `generate_attributions()` (FontAttribution dataclass list)
4. Implement `generate_attribution_md()` (Jinja2 rendering)
5. Implement `generate_license_files()` (deduplicated LICENSE-* files)
6. Implement `write_files()` (write to out_dir)

**Tests:**
- Unit test: Parse fonts.yml → List[FontAttribution]
- Unit test: Render template with mock data
- Unit test: License deduplication (7 fonts → 2 LICENSE files)
- Unit test: License ID generation ("CC BY 4.0" → "LICENSE-CC-BY-4.0")

### Phase 2: CLI Integration (1 hour)

**Files to modify:**
- `gitbook_worker/tools/fonts_cli.py` (add `generate-attribution` command)

**Tasks:**
1. Add `@fonts_cli.command(name="generate-attribution")`
2. Parse CLI options: `--fonts-config`, `--out-dir`, `--template`
3. Invoke FontAttributionGenerator
4. Colorized output (click.echo mit click.style)

**Tests:**
- Integration test: CLI command generates files in temp dir
- Test: `--template` option uses custom template

### Phase 3: Orchestrator Integration (1 hour)

**Files to modify:**
- `gitbook_worker/tools/workflow_orchestrator/orchestrator.py`
- `de/publish.yml` (add `generate_attribution: true`)

**Tasks:**
1. Add `_step_generate_attribution()` handler
2. Parse `generate_attribution` from manifest
3. Call fonts_cli as subprocess
4. Update default profiles to include step (optional, or manual trigger)

**Tests:**
- Integration test: Orchestrator run with `generate_attribution: true`
- Verify ATTRIBUTION.md and LICENSE files appear in publish/

### Phase 4: Documentation & Templates (1-2 hours)

**Files to create/update:**
- `gitbook_worker/tools/fonts/templates/LICENSE-CC-BY-4.0.txt`
- `gitbook_worker/tools/fonts/templates/LICENSE-BITSTREAM-VERA.txt`
- `gitbook_worker/tools/fonts/templates/LICENSE-MIT.txt`
- `docs/fonts-attribution-generator.md` (User guide)
- Update `AGENTS.md` with generator usage

**Tasks:**
1. Create LICENSE template files
2. Document CLI usage
3. Document orchestrator integration
4. Update AGENTS.md: "Attribution-Dateien werden automatisch generiert"

### Phase 5: Testing & Validation (1 hour)

**Tests:**
- End-to-end test: Full orchestrator run generates correct files
- Validate ATTRIBUTION.md table has all fonts from fonts.yml
- Validate LICENSE-CC-BY-4.0 exists and has correct content
- CI/CD: Add check that ATTRIBUTION.md is up-to-date (fail if manual edit)

**Validation:**
```bash
# Manual test
python -m gitbook_worker.tools.fonts_cli generate-attribution \
  --out-dir de/publish

# Verify files
ls de/publish/ATTRIBUTION.md
ls de/publish/LICENSE-CC-BY-4.0
ls de/publish/LICENSE-BITSTREAM-VERA

# Check content
grep "Twitter Color Emoji" de/publish/ATTRIBUTION.md
grep "DejaVu" de/publish/ATTRIBUTION.md
```

## Success Criteria

- [ ] `fonts_cli generate-attribution` command works standalone
- [ ] ATTRIBUTION.md table matches all fonts in fonts.yml (7 fonts)
- [ ] LICENSE-CC-BY-4.0 and LICENSE-BITSTREAM-VERA files generated
- [ ] Orchestrator step writes files to publish/
- [ ] Template system allows custom ATTRIBUTION.md layouts
- [ ] License URL fetch with fallback to local templates
- [ ] CI/CD validates fonts.yml completeness (all required fields)
- [ ] Documentation complete (CLI, orchestrator, AGENTS.md)

## Future Enhancements (Out of Scope)

1. **Asset Attribution (non-fonts)**
   - Extend generator to handle images, logos, icons
   - Add `assets:` section to fonts.yml or separate assets.yml

2. **License Validation**
   - Check license URLs are reachable
   - Validate license text against SPDX identifiers
   - Warn if license_url returns 404

3. **Multi-Language Support**
   - Generate ATTRIBUTION.md in multiple languages
   - Template system with i18n (Jinja2 + gettext)

4. **PDF Embedding**
   - Automatically embed ATTRIBUTION.md as appendix in PDF
   - Link LICENSE files in PDF metadata

5. **Change Detection**
   - Track fonts.yml changes via Git
   - Auto-regenerate only if fonts.yml modified
   - Store generation hash in ATTRIBUTION.md comment

6. **VS Code Integration**
   - Task: "Generate Attribution"
   - Status bar: "Attribution up-to-date ✓" / "Attribution outdated ⚠"
   - Quick Fix: "Regenerate attribution files"

## Dependencies

**Python Packages:**
- `pyyaml` (already installed)
- `jinja2` (already installed for Ansible, or add to requirements.txt)
- `requests` (for fetching license URLs)

**Internal Dependencies:**
- `gitbook_worker.tools.fonts_cli` (extend existing)
- `gitbook_worker.defaults.fonts.yml` (data source)
- `orchestrator.py` (new step: generate_attribution)

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| License URL fetch fails | Generator crashes | Medium | Fallback to local LICENSE templates |
| fonts.yml missing fields | AttributeError | Low | Validation step before generation |
| Template rendering error | Broken ATTRIBUTION.md | Low | Unit tests with edge cases |
| Out-of-sync manual edits | Overwritten by generator | Medium | CI check: fail if ATTRIBUTION.md modified manually |
| Large LICENSE files (MB+) | Slow generator | Low | Cache downloaded licenses, max timeout 10s |

## Open Questions

1. **Template Location**
   - Q: Store templates in `gitbook_worker/tools/fonts/templates/` or `gitbook_worker/defaults/templates/`?
   - A: `gitbook_worker/tools/fonts/templates/` (co-located with generator)

2. **Orchestrator Step Placement**
   - Q: Run `generate_attribution` before or after `publisher`?
   - A: **Before publisher** (damit ATTRIBUTION.md im PDF verlinkt werden kann)

3. **Manifest Schema**
   - Q: Use `generate_attribution: true` oder separate `attribution_config:` section?
   - A: Start simple with boolean flag, extend later if needed

4. **License File Naming**
   - Q: `LICENSE-CC-BY-4.0` oder `LICENSE.CC-BY-4.0` oder `CC-BY-4.0.LICENSE`?
   - A: `LICENSE-CC-BY-4.0` (matches existing `LICENSE-FONTS` pattern)

5. **Generation Timestamp**
   - Q: Include generation timestamp in ATTRIBUTION.md?
   - A: **Yes** (helps identify outdated files, format: ISO 8601)

## Related Work

- **font-storage-dynamic-generation.md**: Generates FontBundleSpec from fonts.yml
  - Synergy: Both tools use fonts.yml as single source
  - Attribution generator reads final font metadata, storage generator manages downloads

- **AGENTS.md sections 12-14**: Font management & license compliance
  - Attribution generator enforces: "NO hardcoded fonts" → all in fonts.yml → all attributed

- **publish/ATTRIBUTION.md**: Current manual file
  - Will become **generated** file (template preserves structure)

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Core Generator | 3-4h | None |
| Phase 2: CLI Integration | 1h | Phase 1 |
| Phase 3: Orchestrator Integration | 1h | Phase 2 |
| Phase 4: Documentation & Templates | 1-2h | Phase 3 |
| Phase 5: Testing & Validation | 1h | Phase 4 |
| **Total** | **6-8 hours** | |

## Approval & Sign-Off

- [ ] Technical design reviewed
- [ ] License compliance verified (AGENTS.md conformance)
- [ ] Implementation plan approved
- [ ] Tests specified
- [ ] Documentation outline complete

---

**Next Steps:**
1. Review this backlog document
2. Approve design & implementation plan
3. Create GitHub issue/task
4. Implement Phase 1 (core generator)
5. Iterate through phases with tests
