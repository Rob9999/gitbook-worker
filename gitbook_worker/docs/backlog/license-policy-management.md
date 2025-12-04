---
version: 0.1.0
date: 2025-12-04
history:
  - version: 0.1.0
    date: 2025-12-04
    description: Initial backlog for centralized license policy management
---

# License Policy Management - Centralization & Extension

## 1. Problem Statement

### Current State (IST-Zustand)

**License Policy ist fragmentiert:**

1. **fonts.yml** (gitbook_worker/defaults/fonts.yml):
   - ❌ **FEHLT:** Keine `allowed_licenses` / `forbidden_licenses` Sektion
   - ✅ **GUT:** Jeder Font hat explizite License-Angabe
   - ⚠️ **INKONSISTENT:** Keine zentrale Policy-Definition

2. **setup_docker_environment.py** (hardcoded):
   ```python
   ALLOWED_LICENSES = {
       "CC BY 4.0",
       "Creative Commons Attribution 4.0 International (CC BY 4.0)",
       "MIT",
       "SIL Open Font License 1.1",
       "Bitstream Vera License",
       "Bitstream Vera License + Public Domain",
   }
   
   FORBIDDEN_LICENSES = {
       "OFL",  # Wrong abbreviation
       "Apache", "Apache-2.0",
       "GPL", "AGPL", "LGPL",
       "UFL", "proprietary",
   }
   ```
   - ❌ **PROBLEM:** Hardcoded in Python-Code
   - ❌ **PROBLEM:** Nur für Docker-Setup nutzbar
   - ❌ **PROBLEM:** Änderungen erfordern Code-Änderung

3. **DOCKERFILE_STRATEGY.md** (Archiv-Dokumentation):
   - ✅ **DOKUMENTIERT:** Policy ist beschrieben
   - ❌ **OBSOLET:** Nur in Legacy-Dokumentation
   - ⚠️ **NICHT GENUTZT:** Keine Runtime-Verwendung

### Risiken

1. **Inkonsistenz:** Policy-Änderungen müssen an mehreren Stellen erfolgen
2. **Fehleranfälligkeit:** Vergessene Updates führen zu abweichenden Policies
3. **Keine Automatisierung:** Keine programmatische Validierung außerhalb Docker
4. **Asset-Coverage fehlt:** Nur Fonts, keine Bilder/Grafiken/Daten
5. **Keine AGENTS.md-Synchronisation:** Policy nicht mit AGENTS.md verlinkt

## 2. Zielsetzung

### Primärziele

1. **Single Source of Truth:** Eine zentrale `license-policy.yml` für alle Asset-Typen
2. **Automatische Validierung:** Bei Build-Zeit ALLE Assets gegen Policy prüfen
3. **Erweiterbarkeit:** Nicht nur Fonts, auch Images, Data, Code-Snippets
4. **AGENTS.md-Konformität:** Policy muss mit AGENTS.md Sections 12-14 aligned sein
5. **Programmatische API:** `LicensePolicyValidator` für Tests und CI/CD

### Sekundärziele

- Attribution Generation: Automatische LICENSE-Dateien für Publikationen
- Upgrade-Path: Sanfte Migration ohne Breaking Changes
- Documentation: Klare Richtlinien für Beitragende
- Tooling: CLI-Tools zur License-Überprüfung

## 3. Lösungsansatz

### 3.1 Zentrale Policy-Datei: `license-policy.yml`

**Speicherort:** `gitbook_worker/defaults/license-policy.yml`

**Struktur:**
```yaml
version: 1.0.0

# =============================================================================
# License Policy - Rechtliche Grundlage für alle Assets
# =============================================================================
# 
# Diese Policy definiert, welche Lizenzen für Assets in ERDA-Projekten
# verwendet werden dürfen. Sie basiert auf:
# - AGENTS.md Sections 12-14 (Font Management & License Compliance)
# - Open Source Best Practices
# - Attribution-Anforderungen
#
# CRITICAL: Jede Änderung dieser Policy muss rechtlich geprüft werden!
#

policy:
  # Asset-Typen die validiert werden
  asset_types:
    - fonts
    - images
    - data
    - code_snippets
    - audio
    - video
  
  # Erlaubte Lizenzen (Whitelist)
  allowed_licenses:
    fonts:
      - "CC BY 4.0"
      - "Creative Commons Attribution 4.0 International (CC BY 4.0)"
      - "MIT"
      - "SIL Open Font License 1.1"
      - "OFL 1.1"  # Correct abbreviation for SIL OFL
      - "Bitstream Vera License"
      - "Bitstream Vera License + Public Domain"
      - "Public Domain"
    
    images:
      - "CC BY 4.0"
      - "CC BY-SA 4.0"
      - "Creative Commons Attribution 4.0 International (CC BY 4.0)"
      - "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)"
      - "MIT"
      - "Public Domain"
      - "CC0 1.0 Universal"
    
    data:
      - "CC BY 4.0"
      - "CC BY-SA 4.0"
      - "MIT"
      - "ODbL 1.0"  # Open Database License
      - "Public Domain"
      - "CC0 1.0 Universal"
    
    code_snippets:
      - "MIT"
      - "Apache 2.0"  # For code, Apache is OK
      - "BSD-3-Clause"
      - "BSD-2-Clause"
      - "Public Domain"
      - "CC0 1.0 Universal"
    
    audio:
      - "CC BY 4.0"
      - "CC BY-SA 4.0"
      - "MIT"
      - "Public Domain"
      - "CC0 1.0 Universal"
    
    video:
      - "CC BY 4.0"
      - "CC BY-SA 4.0"
      - "MIT"
      - "Public Domain"
      - "CC0 1.0 Universal"
  
  # Verbotene Lizenzen (Blacklist)
  forbidden_licenses:
    fonts:
      - "OFL"  # Wrong abbreviation (should be "OFL 1.1" or "SIL Open Font License 1.1")
      - "Apache"  # Ambiguous, use "Apache 2.0" if needed
      - "GPL"
      - "GPL-2.0"
      - "GPL-3.0"
      - "AGPL"
      - "AGPL-3.0"
      - "LGPL"
      - "LGPL-2.1"
      - "LGPL-3.0"
      - "UFL"  # Ubuntu Font License (restrictive)
      - "proprietary"
      - "All Rights Reserved"
    
    images:
      - "GPL"
      - "GPL-2.0"
      - "GPL-3.0"
      - "AGPL"
      - "LGPL"
      - "proprietary"
      - "All Rights Reserved"
      - "CC BY-NC"  # Non-Commercial not allowed
      - "CC BY-ND"  # No-Derivatives not allowed
    
    data:
      - "GPL"
      - "AGPL"
      - "LGPL"
      - "proprietary"
      - "All Rights Reserved"
    
    code_snippets:
      - "GPL"  # For snippets in documentation, GPL is problematic
      - "AGPL"
      - "LGPL"
      - "proprietary"
      - "All Rights Reserved"
    
    audio:
      - "GPL"
      - "AGPL"
      - "proprietary"
      - "All Rights Reserved"
      - "CC BY-NC"
      - "CC BY-ND"
    
    video:
      - "GPL"
      - "AGPL"
      - "proprietary"
      - "All Rights Reserved"
      - "CC BY-NC"
      - "CC BY-ND"

# Attribution Requirements
attribution:
  # Automatische Attribution-Generierung aktivieren?
  auto_generate: true
  
  # Wo wird Attribution gespeichert?
  output_files:
    - "publish/ATTRIBUTION.md"
    - "publish/LICENSES.txt"
  
  # Template für Attribution-Einträge
  template: |
    {asset_type}: {name}
    License: {license}
    License URL: {license_url}
    Source: {source_url}
    Author: {author}
    Version: {version}

# Validation Settings
validation:
  # Bei Build-Zeit validieren?
  enforce_on_build: true
  
  # Was passiert bei License-Violation?
  violation_action: "fail"  # "fail" | "warn" | "ignore"
  
  # Wo liegen Asset-Manifeste?
  asset_manifests:
    fonts: "gitbook_worker/defaults/fonts.yml"
    images: "gitbook_worker/defaults/images.yml"  # Future
    data: "gitbook_worker/defaults/data.yml"      # Future

# Legal Notes
legal:
  responsibility: |
    Diese Policy stellt keine Rechtsberatung dar. Bei Unsicherheit bezüglich
    einer Lizenz konsultieren Sie einen Rechtsanwalt. Die ERDA-Projektleitung
    übernimmt keine Haftung für Lizenzverletzungen.
  
  last_legal_review: "2025-12-04"
  next_review_due: "2026-06-04"  # Halbjährlich prüfen
  
  contact: "legal@erda-project.org"
```

### 3.2 Migration: fonts.yml erweitern

**Option A: Inline Policy (Einfach, weniger flexibel)**
```yaml
version: 1.0.0

# License Policy Reference
license_policy:
  policy_file: "gitbook_worker/defaults/license-policy.yml"
  asset_type: "fonts"

fonts:
  # ... existing font entries ...
```

**Option B: Separate Policy (Flexibel, wiederverwendbar)** ⭐ EMPFOHLEN
```yaml
version: 1.0.0

# Fonts werden gegen zentrale license-policy.yml validiert
# Die Policy wird zur Build-Zeit automatisch geladen

fonts:
  # ... existing font entries ...
```

### 3.3 Programmatische API

**Neue Datei:** `gitbook_worker/tools/licensing/policy_validator.py`

```python
"""License Policy Validation API."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import yaml


@dataclass
class LicenseViolation:
    """Represents a license policy violation."""
    asset_type: str
    asset_name: str
    license: str
    reason: str
    severity: str  # "error" | "warning"


@dataclass
class PolicyValidationResult:
    """Result of policy validation."""
    passed: bool
    violations: List[LicenseViolation]
    checked_assets: int
    
    def summary(self) -> str:
        if self.passed:
            return f"✅ All {self.checked_assets} assets passed license validation"
        else:
            errors = [v for v in self.violations if v.severity == "error"]
            warnings = [v for v in self.violations if v.severity == "warning"]
            return (
                f"❌ License violations found:\n"
                f"  Errors: {len(errors)}\n"
                f"  Warnings: {len(warnings)}\n"
                f"  Total checked: {self.checked_assets}"
            )


class LicensePolicyValidator:
    """Validates assets against license policy."""
    
    def __init__(self, policy_path: Optional[Path] = None):
        if policy_path is None:
            # Default: Load from defaults/
            policy_path = Path(__file__).parent.parent.parent / "defaults" / "license-policy.yml"
        
        with open(policy_path, encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)
    
    def validate_font(self, font_config: dict) -> List[LicenseViolation]:
        """Validate a single font against policy."""
        violations = []
        
        license_str = font_config.get("license", "")
        name = font_config.get("name", "Unknown")
        
        # Check against allowed list
        allowed = self.policy["policy"]["allowed_licenses"]["fonts"]
        if license_str not in allowed:
            violations.append(LicenseViolation(
                asset_type="font",
                asset_name=name,
                license=license_str,
                reason=f"License '{license_str}' not in allowed list for fonts",
                severity="error"
            ))
        
        # Check against forbidden list
        forbidden = self.policy["policy"]["forbidden_licenses"]["fonts"]
        if license_str in forbidden:
            violations.append(LicenseViolation(
                asset_type="font",
                asset_name=name,
                license=license_str,
                reason=f"License '{license_str}' is explicitly forbidden for fonts",
                severity="error"
            ))
        
        return violations
    
    def validate_fonts_yml(self, fonts_yml_path: Path) -> PolicyValidationResult:
        """Validate entire fonts.yml against policy."""
        with open(fonts_yml_path, encoding="utf-8") as f:
            fonts_config = yaml.safe_load(f)
        
        all_violations = []
        checked = 0
        
        for font_key, font_data in fonts_config.get("fonts", {}).items():
            checked += 1
            violations = self.validate_font(font_data)
            all_violations.extend(violations)
        
        return PolicyValidationResult(
            passed=len(all_violations) == 0,
            violations=all_violations,
            checked_assets=checked
        )
    
    def validate_image(self, image_config: dict) -> List[LicenseViolation]:
        """Validate image against policy (future implementation)."""
        # TODO: Implement when images.yml exists
        pass
    
    def generate_attribution(self, fonts_yml_path: Path) -> str:
        """Generate attribution text for all fonts."""
        with open(fonts_yml_path, encoding="utf-8") as f:
            fonts_config = yaml.safe_load(f)
        
        template = self.policy["attribution"]["template"]
        attributions = []
        
        for font_key, font_data in fonts_config.get("fonts", {}).items():
            attribution = template.format(
                asset_type="Font",
                name=font_data.get("name", "Unknown"),
                license=font_data.get("license", "Unknown"),
                license_url=font_data.get("license_url", "N/A"),
                source_url=font_data.get("source_url", "N/A"),
                author=font_data.get("author", "Unknown"),
                version=font_data.get("version", "Unknown")
            )
            attributions.append(attribution)
        
        return "\n\n".join(attributions)


def validate_fonts_license_policy(fonts_yml_path: Path) -> PolicyValidationResult:
    """Convenience function to validate fonts.yml."""
    validator = LicensePolicyValidator()
    return validator.validate_fonts_yml(fonts_yml_path)
```

### 3.4 CLI-Tool

**Neue Datei:** `gitbook_worker/tools/licensing/license_validator_cli.py`

```python
"""CLI tool for license validation."""

import argparse
from pathlib import Path
from .policy_validator import LicensePolicyValidator


def main():
    parser = argparse.ArgumentParser(
        description="Validate assets against license policy"
    )
    parser.add_argument(
        "asset_file",
        type=Path,
        help="Path to asset manifest (fonts.yml, images.yml, etc.)"
    )
    parser.add_argument(
        "--policy",
        type=Path,
        help="Path to license-policy.yml (default: defaults/license-policy.yml)"
    )
    parser.add_argument(
        "--generate-attribution",
        action="store_true",
        help="Generate attribution file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for attribution file"
    )
    
    args = parser.parse_args()
    
    validator = LicensePolicyValidator(policy_path=args.policy)
    
    # Validate
    if str(args.asset_file).endswith("fonts.yml"):
        result = validator.validate_fonts_yml(args.asset_file)
    else:
        print(f"❌ Unsupported asset type: {args.asset_file}")
        return 1
    
    # Print result
    print(result.summary())
    
    if not result.passed:
        for violation in result.violations:
            print(f"  [{violation.severity.upper()}] {violation.asset_name}: {violation.reason}")
    
    # Generate attribution if requested
    if args.generate_attribution:
        attribution = validator.generate_attribution(args.asset_file)
        output_path = args.output or Path("ATTRIBUTION.md")
        output_path.write_text(attribution, encoding="utf-8")
        print(f"✅ Attribution written to {output_path}")
    
    return 0 if result.passed else 1


if __name__ == "__main__":
    exit(main())
```

**Usage:**
```bash
# Validate fonts
python -m gitbook_worker.tools.licensing.license_validator_cli \
    gitbook_worker/defaults/fonts.yml

# Generate attribution
python -m gitbook_worker.tools.licensing.license_validator_cli \
    gitbook_worker/defaults/fonts.yml \
    --generate-attribution \
    --output publish/ATTRIBUTION.md
```

## 4. Rechtliche Haltbarkeit

### 4.1 Ist eine assets-license-policy.yml rechtlich haltbar?

**✅ JA, aber mit Einschränkungen:**

#### Vorteile (Pro)
1. **Klarheit:** Explizite Policy schafft Transparenz
2. **Dokumentation:** Nachweis der Due Diligence
3. **Automatisierung:** Technische Durchsetzung verhindert Fehler
4. **Attribution:** Automatische Lizenz-Erfüllung
5. **Best Practice:** Entspricht Open-Source-Standards

#### Risiken (Con)
1. **Keine Rechtsberatung:** YAML-Datei ersetzt keinen Anwalt
2. **Policy ≠ Garantie:** Technische Validierung ist keine Rechtsgarantie
3. **Interpretation:** Lizenz-Texte können mehrdeutig sein
4. **Updates:** Lizenzen ändern sich (z.B. CC BY 4.0 → 5.0)
5. **Jurisdiktion:** Lizenz-Interpretation variiert nach Land

#### Empfehlungen
1. **Rechtliche Prüfung:** Policy von Anwalt reviewen lassen
2. **Regelmäßige Updates:** Halbjährlich Policy aktualisieren
3. **Disclaimer:** Klarstellen dass Policy keine Rechtsberatung ist
4. **Dokumentation:** Begründung für jede Policy-Entscheidung
5. **Versionierung:** Jede Policy-Änderung dokumentieren

### 4.2 Rechtliche Stabilität nach Asset-Typ

| Asset-Typ | Stabilität | Begründung |
|-----------|------------|------------|
| **Fonts** | ✅ Hoch | Etablierte Lizenzen (OFL, CC BY), klare Rechtslage |
| **Images** | ✅ Hoch | Creative Commons gut etabliert |
| **Data** | ⚠️ Mittel | ODbL weniger bekannt, EU-Datenschutz zu beachten |
| **Code Snippets** | ✅ Hoch | MIT/Apache/BSD sehr stabil |
| **Audio/Video** | ⚠️ Mittel | Zusätzliche Rechte (Performer, Sound Recording) |

### 4.3 Compliance mit AGENTS.md

**AGENTS.md Sections 12-14 Anforderungen:**
- ✅ "No Hardcoded Fonts" → License Policy ist konfigurierbar
- ✅ "License Compliance" → Automatische Validierung
- ✅ "Attribution Requirements" → Automatische Attribution-Generierung
- ✅ "Dynamic Docker Font Setup" → Policy wird zur Build-Zeit gelesen

**Neue Requirement für AGENTS.md:**
```markdown
## License Policy Management (Section 15)
16. **Centralized License Policy**: All asset licenses MUST be validated against
    `gitbook_worker/defaults/license-policy.yml`. This ensures:
    - **Consistency**: Same rules for fonts, images, data, code
    - **Auditability**: Central place for legal review
    - **Automation**: Technical enforcement at build time
17. **Attribution Generation**: Every published document MUST include attribution
    for all used assets. Use `license_validator_cli.py --generate-attribution`.
18. **Policy Versioning**: License policy MUST be versioned and reviewed 
    semi-annually (see `legal.next_review_due` in policy file).
```

## 5. Implementierungs-Plan

### Phase 1: Grundlagen (Woche 1)
**Ziel:** Zentrale Policy-Datei und Validator

- [ ] Erstelle `gitbook_worker/defaults/license-policy.yml`
- [ ] Implementiere `LicensePolicyValidator` class
- [ ] Schreibe Unit-Tests für Validator
- [ ] Dokumentiere Policy-Struktur

**Deliverables:**
- license-policy.yml (funktional)
- policy_validator.py (getestet)
- README für Policy-Management

### Phase 2: Integration (Woche 2)
**Ziel:** Docker und Publisher nutzen Policy

- [ ] Refactor `setup_docker_environment.py`:
  - Ersetze hardcoded `ALLOWED_LICENSES` durch Policy-Loader
  - Lese Policy aus license-policy.yml
- [ ] Update `publisher.py`:
  - Validiere Fonts gegen Policy vor PDF-Build
  - Generiere Fehler bei Violations
- [ ] Erstelle CLI-Tool `license_validator_cli.py`
- [ ] Update CI/CD: Validierung in GitHub Actions

**Deliverables:**
- setup_docker_environment.py ohne hardcoded Licenses
- publisher.py mit Policy-Validierung
- CI/CD mit automatischer License-Prüfung

### Phase 3: Attribution (Woche 3)
**Ziel:** Automatische Attribution-Generierung

- [ ] Implementiere `generate_attribution()` in Validator
- [ ] Erstelle Markdown-Template für Attribution
- [ ] Integration in Publisher:
  - Generiere ATTRIBUTION.md bei jedem Build
  - Füge Attribution in PDF-Frontmatter ein
- [ ] Update publish.yml: `attribution_generation: true`

**Deliverables:**
- Automatische ATTRIBUTION.md Generierung
- PDF mit eingebetteter Attribution

### Phase 4: Erweiterung (Woche 4)
**Ziel:** Unterstützung für andere Asset-Typen

- [ ] Erstelle `gitbook_worker/defaults/images.yml` (Konzept)
- [ ] Implementiere `validate_image()` in Validator
- [ ] Dokumentiere Best Practices für Image-Lizenzen
- [ ] Update AGENTS.md mit neuer Section 15

**Deliverables:**
- images.yml Template
- Erweiterte Validator-API
- Vollständige Dokumentation

## 6. Tests & Validierung

### 6.1 Unit Tests

**Datei:** `gitbook_worker/tests/test_license_policy_validator.py`

```python
import pytest
from pathlib import Path
from gitbook_worker.tools.licensing.policy_validator import (
    LicensePolicyValidator,
    LicenseViolation
)


def test_validator_loads_default_policy():
    """Test that validator loads default policy without errors."""
    validator = LicensePolicyValidator()
    assert "policy" in validator.policy
    assert "allowed_licenses" in validator.policy["policy"]


def test_validate_allowed_font():
    """Test validation passes for allowed license."""
    validator = LicensePolicyValidator()
    font_config = {
        "name": "Test Font",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/"
    }
    violations = validator.validate_font(font_config)
    assert len(violations) == 0


def test_validate_forbidden_font():
    """Test validation fails for forbidden license."""
    validator = LicensePolicyValidator()
    font_config = {
        "name": "Bad Font",
        "license": "GPL",
        "license_url": "https://www.gnu.org/licenses/gpl-3.0.html"
    }
    violations = validator.validate_font(font_config)
    assert len(violations) > 0
    assert violations[0].severity == "error"
    assert "GPL" in violations[0].reason


def test_validate_fonts_yml(tmp_path):
    """Test validation of entire fonts.yml file."""
    fonts_yml = tmp_path / "fonts.yml"
    fonts_yml.write_text("""
version: 1.0.0
fonts:
  GOOD_FONT:
    name: "Good Font"
    license: "MIT"
    license_url: "https://opensource.org/licenses/MIT"
  
  BAD_FONT:
    name: "Bad Font"
    license: "proprietary"
    license_url: "https://example.com/proprietary"
""", encoding="utf-8")
    
    validator = LicensePolicyValidator()
    result = validator.validate_fonts_yml(fonts_yml)
    
    assert not result.passed
    assert result.checked_assets == 2
    assert len(result.violations) >= 1
    assert any("proprietary" in v.license for v in result.violations)


def test_generate_attribution(tmp_path):
    """Test attribution generation."""
    fonts_yml = tmp_path / "fonts.yml"
    fonts_yml.write_text("""
version: 1.0.0
fonts:
  TEST:
    name: "Test Font"
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    source_url: "https://example.com/font"
    version: "1.0.0"
""", encoding="utf-8")
    
    validator = LicensePolicyValidator()
    attribution = validator.generate_attribution(fonts_yml)
    
    assert "Test Font" in attribution
    assert "CC BY 4.0" in attribution
    assert "https://creativecommons.org/licenses/by/4.0/" in attribution
```

### 6.2 Integration Tests

**Test in CI/CD:**
```yaml
# .github/workflows/license-validation.yml
name: License Validation

on: [push, pull_request]

jobs:
  validate-licenses:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Validate Font Licenses
        run: |
          python -m gitbook_worker.tools.licensing.license_validator_cli \
            gitbook_worker/defaults/fonts.yml
      
      - name: Generate Attribution
        run: |
          python -m gitbook_worker.tools.licensing.license_validator_cli \
            gitbook_worker/defaults/fonts.yml \
            --generate-attribution \
            --output ATTRIBUTION.md
      
      - name: Upload Attribution
        uses: actions/upload-artifact@v3
        with:
          name: attribution
          path: ATTRIBUTION.md
```

## 7. Acceptance Criteria

### Funktional
- ✅ Zentrale `license-policy.yml` existiert und ist versioniert
- ✅ `LicensePolicyValidator` kann fonts.yml validieren
- ✅ CLI-Tool kann Policy-Violations anzeigen
- ✅ Automatische Attribution-Generierung funktioniert
- ✅ Docker-Setup liest Policy aus YAML statt Hardcoding
- ✅ Publisher validiert Fonts gegen Policy vor Build

### Qualität
- ✅ Unit-Tests >= 90% Coverage für Validator
- ✅ Integration-Tests in CI/CD
- ✅ Dokumentation vollständig (API + Usage)
- ✅ AGENTS.md aktualisiert mit Section 15

### Rechtlich
- ✅ Policy von Rechtsexperten reviewt
- ✅ Disclaimer in license-policy.yml eingefügt
- ✅ Review-Datum für nächste Prüfung gesetzt
- ✅ Begründungen für alle Policy-Entscheidungen dokumentiert

## 8. Offene Fragen & Diskussionspunkte

### Technisch
1. **Policy-Versionierung:** Semantic Versioning für Policy-Änderungen?
2. **Backwards Compatibility:** Wie gehen wir mit Policy-Upgrades um?
3. **Override-Mechanismus:** Sollen Projekte Policy per `publish.yml` überschreiben können?
4. **Performance:** Policy-Validierung bei jedem Build oder nur im CI/CD?

### Rechtlich
1. **Lizenz-Aliase:** Wie gehen wir mit verschiedenen Schreibweisen um?
   - "CC BY 4.0" vs "Creative Commons Attribution 4.0 International (CC BY 4.0)"
2. **Jurisdiktion:** Muss Policy nach deutschem / EU-Recht angepasst werden?
3. **Dual-Licensing:** Wie validieren wir Assets mit mehreren Lizenzen?
4. **Copyright vs License:** Müssen wir Copyright-Inhaber validieren?

### Organisatorisch
1. **Wer ist verantwortlich** für Policy-Updates?
2. **Wie oft** sollte Policy rechtlich geprüft werden?
3. **Wer darf** Policy-Änderungen approven?
4. **Was passiert** bei Policy-Violations in Legacy-Content?

## 9. Risiken & Mitigations

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Falsche Lizenz-Interpretation | Mittel | Hoch | Rechtsexperten-Review halbjährlich |
| Policy zu restriktiv | Mittel | Mittel | Override-Mechanismus in publish.yml |
| Performance-Impact | Niedrig | Niedrig | Caching von Policy-Loads |
| Breaking Changes | Hoch | Mittel | Semver für Policy, Deprecation-Warnings |
| Unvollständige Coverage | Mittel | Mittel | Phased Rollout: Fonts → Images → Data |

## 10. Success Metrics

### Quantitativ
- **Automatisierung:** 100% der Assets automatisch validiert
- **Fehlerrate:** < 1% False Positives in Policy-Validation
- **Performance:** Policy-Validierung < 100ms
- **Coverage:** >= 90% Test-Coverage für Validator

### Qualitativ
- **Developer Experience:** Einfaches Hinzufügen neuer Assets
- **Rechtssicherheit:** Klare Dokumentation aller License-Entscheidungen
- **Wartbarkeit:** Policy-Änderungen ohne Code-Änderungen möglich
- **Transparency:** Attribution in allen Publikationen vorhanden

## 11. Referenzen & Ressourcen

### Interne Dokumente
- `AGENTS.md` Sections 12-14: Font Management & License Compliance
- `DOCKERFILE_STRATEGY.md`: Aktuelle License Policy (Archive)
- `setup_docker_environment.py`: Hardcoded Policy (wird ersetzt)

### Externe Standards
- [Creative Commons Licenses](https://creativecommons.org/licenses/)
- [SIL Open Font License](https://scripts.sil.org/OFL)
- [Open Source Initiative](https://opensource.org/licenses)
- [SPDX License List](https://spdx.org/licenses/)

### Legal Resources
- [EU Copyright Directive](https://ec.europa.eu/digital-single-market/en/modernisation-eu-copyright-rules)
- [GDPR Data Protection](https://gdpr.eu/) (für Data-Assets)
- [GitHub Licensing Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)

## 12. Next Steps nach Backlog-Review

**Nach Abstimmung:**

1. **Rechtliche Prüfung:** Policy-Entwurf von Anwalt reviewen lassen
2. **AGENTS.md Update:** Section 15 hinzufügen
3. **Phase 1 Implementation:** license-policy.yml + Validator erstellen
4. **Migration Setup:** setup_docker_environment.py refactoren
5. **Testing:** Unit + Integration Tests schreiben
6. **Documentation:** Usage-Guide für Beitragende

---

**Signed-off-by:** ERDA GitBook Worker Team  
**Version:** 0.1.0 (Draft for Review)  
**Status:** 🔍 AWAITING LEGAL & TECHNICAL REVIEW
