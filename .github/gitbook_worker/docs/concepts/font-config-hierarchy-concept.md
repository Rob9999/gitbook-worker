---
version: 1.0.0
created: 2025-11-07
modified: 2025-11-10
status: concept
type: technical-concept
---

# Font Configuration Hierarchy Konzept

## Problem-Analyse

Aktuell haben wir **zwei verschiedene Konfigurationsmechanismen** für Fonts:

### 1. `fonts.yml` (defaults)
```yaml
fonts:
  CJK:
    name: "ERDA CC-BY CJK"
    paths:
      - ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf"
      - ".github/fonts/erda-ccby-cjk.ttf"
  SERIF:
    name: "DejaVu Serif"
    paths: []
```

**Zweck:** System-weite Standard-Konfiguration für alle Publishing-Jobs

### 2. `publish.yml` (manifest)
```yaml
fonts:
- name: ERDA CC-BY CJK
  path: .github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf

publish:
- path: ./
  pdf_options:
    main_font: DejaVu Serif
    sans_font: DejaVu Sans
    mono_font: DejaVu Sans Mono
    mainfont_fallback: Twemoji Mozilla:mode=harf; [.github/fonts/erda-ccby-cjk/...]:mode=harf
```

**Zweck:** Projekt-spezifische Font-Konfiguration für einzelne Publikationen

## Vorgeschlagene Lösung: Hierarchisches Merge-System

### Konzept: "Defaults + Overrides"

```
┌─────────────────────────────────────────────────────────────┐
│  Ebene 1: fonts.yml (System Defaults)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ CJK: ERDA CC-BY CJK (3 Fallback-Pfade)               │  │
│  │ SERIF: DejaVu Serif (System)                         │  │
│  │ SANS: DejaVu Sans (System)                           │  │
│  │ MONO: DejaVu Sans Mono (System)                      │  │
│  │ EMOJI: Twemoji Mozilla (System)                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ▼ MERGE ▼
┌─────────────────────────────────────────────────────────────┐
│  Ebene 2: publish.yml fonts (Projekt-Overrides)             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ fonts:                                                │  │
│  │ - name: ERDA CC-BY CJK                                │  │
│  │   path: .github/fonts/custom-location/font.ttf       │  │
│  │                                                       │  │
│  │ → ÜBERSCHREIBT CJK-Pfad aus fonts.yml                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ▼ MERGE ▼
┌─────────────────────────────────────────────────────────────┐
│  Ebene 3: publish.yml pdf_options (Output-Overrides)        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ pdf_options:                                          │  │
│  │   main_font: Custom Serif                             │  │
│  │   sans_font: Custom Sans                              │  │
│  │   mainfont_fallback: Custom:mode=harf; ...            │  │
│  │                                                       │  │
│  │ → ÜBERSCHREIBT Font-Namen für diese Publikation      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │ FINAL FONT CONFIG│
                 └─────────────────┘
```

## Implementierungs-Strategie

### Option 1: "Smart Merge" (EMPFOHLEN)

**Verhalten:**
1. Lade `fonts.yml` als Basis-Konfiguration
2. Parse `publish.yml` → Abschnitt `fonts:`
3. Merge Font-Pfade nach Font-Namen
4. Parse `pdf_options` → überschreibt finale Font-Namen

**Code-Logik:**

```python
def get_merged_font_config(manifest_path: Optional[str] = None) -> FontConfigLoader:
    """Get font configuration with manifest overrides applied."""
    
    # 1. Load system defaults from fonts.yml
    base_config = get_font_config()
    
    # 2. If no manifest, return defaults
    if not manifest_path:
        return base_config
    
    # 3. Parse manifest fonts section
    manifest_data = _load_yaml(manifest_path)
    manifest_fonts = manifest_data.get("fonts", [])
    
    # 4. Create merged config
    merged = FontConfigLoader(config_path=base_config._config_path)
    
    # 5. Apply manifest overrides
    for font_spec in _parse_font_specs(manifest_fonts, Path(manifest_path).parent):
        if font_spec.name:
            # Try to match by name (e.g., "ERDA CC-BY CJK" → "CJK")
            key = _match_font_key(font_spec.name, merged.get_all_font_keys())
            if key and font_spec.path:
                # Override paths with manifest-specified path
                merged._fonts[key] = FontConfig(
                    name=merged._fonts[key].name,
                    paths=[str(font_spec.path)],  # Single path from manifest
                    license=merged._fonts[key].license,
                    license_url=merged._fonts[key].license_url,
                    source_url=merged._fonts[key].source_url,
                )
    
    return merged

def _match_font_key(font_name: str, available_keys: List[str]) -> Optional[str]:
    """Match font display name to configuration key."""
    # "ERDA CC-BY CJK" → "CJK"
    # "DejaVu Serif" → "SERIF"
    mappings = {
        "ERDA CC-BY CJK": "CJK",
        "DejaVu Serif": "SERIF",
        "DejaVu Sans": "SANS",
        "DejaVu Sans Mono": "MONO",
        "Twemoji Mozilla": "EMOJI",
    }
    return mappings.get(font_name)
```

**Vorteile:**
- ✅ Rückwärtskompatibel mit bestehenden `publish.yml`
- ✅ Klare Hierarchie: fonts.yml < publish.yml fonts < pdf_options
- ✅ Ermöglicht projekt-spezifische Font-Pfad-Overrides
- ✅ Zentrale Lizenz-Metadaten bleiben in fonts.yml

**Nachteile:**
- ⚠️ Matching-Logik zwischen Font-Namen und Keys notwendig
- ⚠️ Komplexität steigt

---

### Option 2: "Deprecate publish.yml fonts" (Einfacher)

**Verhalten:**
1. `fonts:` Abschnitt in `publish.yml` wird als **deprecated** markiert
2. Nur `pdf_options` wird weiter unterstützt
3. Alle Font-Pfade müssen in `fonts.yml` definiert werden
4. `publish.yml` überschreibt nur finale Font-**Namen**, nicht Pfade

**Migration:**

**Vorher (publish.yml):**
```yaml
fonts:
- name: ERDA CC-BY CJK
  path: .github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf

pdf_options:
  main_font: DejaVu Serif
```

**Nachher:**

**fonts.yml:**
```yaml
fonts:
  CJK:
    paths:
      - ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf"
```

**publish.yml:**
```yaml
# fonts: section removed (moved to fonts.yml)

pdf_options:
  main_font: DejaVu Serif  # Kann weiterhin überschreiben
```

**Vorteile:**
- ✅ Einfachere Implementierung
- ✅ Klare Separation of Concerns
- ✅ Eine "Source of Truth" für Font-Pfade

**Nachteile:**
- ⚠️ Breaking Change (benötigt Migration)
- ⚠️ Weniger flexibel für projekt-spezifische Font-Pfade

---

### Option 3: "Dual-Source mit Präzedenz" (Hybrid)

**Verhalten:**
1. Font-Pfade können in **beiden** Dateien definiert werden
2. `publish.yml fonts:` hat **Präzedenz** über `fonts.yml`
3. Wenn Font nicht in `publish.yml`, Fallback zu `fonts.yml`

**Lookup-Reihenfolge:**

```python
def find_font_file(font_key: str, manifest_fonts: List[FontSpec]) -> Optional[str]:
    # 1. Try manifest-specified fonts first
    for spec in manifest_fonts:
        if _matches_font_key(spec.name, font_key):
            if spec.path and spec.path.exists():
                return str(spec.path)
    
    # 2. Fallback to fonts.yml
    config = get_font_config()
    return config.find_font_file(font_key)
```

**Vorteile:**
- ✅ Maximale Flexibilität
- ✅ Rückwärtskompatibel
- ✅ Ermöglicht Overrides ohne fonts.yml zu ändern

**Nachteile:**
- ⚠️ Zwei "Sources of Truth" können zu Verwirrung führen
- ⚠️ Schwieriger zu debuggen ("Wo kommt dieser Font her?")

---

## Empfehlung: **Option 1 (Smart Merge)**

### Warum?

1. **Rückwärtskompatibilität:** Bestehende `publish.yml` funktionieren weiter
2. **Flexibilität:** Projekt-spezifische Overrides möglich
3. **Best Practice:** System-Defaults + Projekt-Overrides ist gängiges Pattern
4. **Klare Hierarchie:** Jeder weiß, welche Config Präzedenz hat

### Umsetzungsplan

#### Phase 1: Merge-Mechanismus implementieren

```python
# In font_config.py

class FontConfigLoader:
    def merge_manifest_fonts(
        self, 
        manifest_fonts: List[FontSpec]
    ) -> "FontConfigLoader":
        """Create new loader with manifest overrides applied."""
        merged = FontConfigLoader(config_path=self._config_path)
        
        # Copy base fonts
        merged._fonts = self._fonts.copy()
        
        # Apply manifest overrides
        for spec in manifest_fonts:
            key = self._match_font_key(spec.name)
            if key and spec.path:
                merged._fonts[key] = FontConfig(
                    name=self._fonts[key].name,
                    paths=[str(spec.path)],
                    license=self._fonts[key].license,
                    license_url=self._fonts[key].license_url,
                    source_url=self._fonts[key].source_url,
                )
        
        return merged
    
    def _match_font_key(self, font_name: Optional[str]) -> Optional[str]:
        """Match display name to config key."""
        if not font_name:
            return None
        
        # Exact match first
        for key, font in self._fonts.items():
            if font.name == font_name:
                return key
        
        # Fuzzy match (case-insensitive partial)
        font_name_lower = font_name.lower()
        for key, font in self._fonts.items():
            if font_name_lower in font.name.lower():
                return key
        
        return None
```

#### Phase 2: Publisher Integration

```python
# In publisher.py, prepare_publishing()

# Load base config
font_config = get_font_config()

# If manifest provided, merge fonts
if manifest_path:
    manifest_data = _load_yaml(manifest_path)
    manifest_fonts = _parse_font_specs(
        manifest_data.get("fonts"), 
        Path(manifest_path).parent
    )
    font_config = font_config.merge_manifest_fonts(manifest_fonts)

# Register fonts from merged config
erda_font_locations = font_config.get_font_paths("CJK")
for font_path in erda_font_locations:
    if os.path.exists(font_path):
        _register_font(font_path)
        break
```

#### Phase 3: Dokumentation

1. Update `README.md` in defaults/ mit Merge-Verhalten
2. Update `FONT_REFACTORING_SUMMARY.md` mit Hierarchie-Erklärung
3. Migration Guide für User die `publish.yml fonts:` nutzen

---

## Alternativen für `pdf_options`

Der `pdf_options` Abschnitt sollte **unverändert bleiben**, da er:

1. **Output-spezifisch** ist (verschiedene PDFs können verschiedene Fonts nutzen)
2. **Pandoc-Variablen** überschreibt (nicht Font-Pfade)
3. **Bereits gut etabliert** ist in der Pipeline

**Beispiel finale Konfiguration:**

```yaml
# fonts.yml (System Defaults)
fonts:
  CJK:
    name: "ERDA CC-BY CJK"
    paths:
      - ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf"
      - ".github/fonts/erda-ccby-cjk.ttf"

# publish.yml (Projekt Override + Output Config)
fonts:
  - name: ERDA CC-BY CJK
    path: .github/fonts/custom-build/erda-cjk-patched.ttf  # Override!

publish:
  - path: ./
    pdf_options:
      main_font: DejaVu Serif              # Output: Font-Name
      mainfont_fallback: Twemoji...; ...   # Output: Fallback-Chain
```

**Resultat:**
- CJK-Font wird von `.github/fonts/custom-build/erda-cjk-patched.ttf` geladen (publish.yml Override)
- Andere Fonts kommen aus fonts.yml
- PDF verwendet "DejaVu Serif" als Hauptfont

---

## Zusammenfassung

| Aspekt | Empfehlung |
|--------|------------|
| **Mechanismus** | Smart Merge (Option 1) |
| **fonts.yml** | System-weite Defaults mit Lizenz-Metadaten |
| **publish.yml fonts:** | Projekt-spezifische Font-Pfad-Overrides (optional) |
| **publish.yml pdf_options:** | Output-spezifische Font-Namen-Overrides |
| **Präzedenz** | fonts.yml < publish.yml fonts < pdf_options |
| **Breaking Changes** | Keine (vollständig rückwärtskompatibel) |

**Next Steps:**
1. ✅ Implementiere `merge_manifest_fonts()` in `FontConfigLoader`
2. ✅ Integriere Merge-Logik in `publisher.py`
3. ✅ Schreibe Tests für Merge-Verhalten
4. ✅ Dokumentiere Hierarchie in README
5. ✅ Optional: Deprecation-Warning wenn `publish.yml fonts:` verwendet wird
