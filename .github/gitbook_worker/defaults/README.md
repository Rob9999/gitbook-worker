# Font Configuration System

This directory contains the font configuration system for the ERDA publishing pipeline.

## Overview

The font configuration system eliminates hardcoded font paths from the codebase by centralizing all font-related configuration in `fonts.yml`, with support for project-specific overrides via `publish.yml`.

## Files

- **`fonts.yml`**: Central font configuration file (system defaults)
- **`font_config.py`** (in `../tools/publishing/`): Python module for loading font configurations

## Hierarchical Configuration (Smart Merge)

The system implements a **3-level hierarchy** where each level can override the previous:

```
┌─────────────────────────────────────────────────┐
│  Level 1: fonts.yml (System Defaults)          │
│  - Base configuration for all projects          │
│  - License metadata                             │
│  - Multiple fallback paths per font             │
└─────────────────────────────────────────────────┘
                    ↓ MERGE ↓
┌─────────────────────────────────────────────────┐
│  Level 2: publish.yml fonts: (Project Override) │
│  - Optional project-specific font paths         │
│  - Overrides fonts.yml paths                    │
│  - Preserves license metadata                   │
└─────────────────────────────────────────────────┘
                    ↓ MERGE ↓
┌─────────────────────────────────────────────────┐
│  Level 3: publish.yml pdf_options: (Output)     │
│  - Output-specific font names                   │
│  - Pandoc variable overrides                    │
│  - Per-publication customization                │
└─────────────────────────────────────────────────┘
```

### Example

**fonts.yml (System Default):**
```yaml
fonts:
  CJK:
    name: "ERDA CC-BY CJK"
    paths:
      - ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf"  # Primary
      - ".github/fonts/erda-ccby-cjk.ttf"                          # Fallback 1
      - ".github/gitbook_worker/tools/publishing/fonts/.../erda-ccby-cjk.ttf"  # Fallback 2
```

**publish.yml (Project Override):**
```yaml
fonts:
  - name: ERDA CC-BY CJK
    path: .github/fonts/custom-build/erda-cjk-patched.ttf  # Overrides all fallbacks!

publish:
  - path: ./
    pdf_options:
      main_font: DejaVu Serif                    # Output-specific font name
      mainfont_fallback: Twemoji...; [...]       # Pandoc fallback chain
```

**Result:**
- CJK font loaded from: `.github/fonts/custom-build/erda-cjk-patched.ttf` (publish.yml wins)
- License metadata preserved from fonts.yml
- PDF uses "DejaVu Serif" as main font (pdf_options wins)

## Configuration Structure

```yaml
fonts:
  <FONT_KEY>:
    name: "Font Display Name"
    license: "License Type"
    license_url: "https://..."
    source_url: "https://..." # Optional
    paths:
      - "path/to/font.ttf"    # Primary location
      - "fallback/path.ttf"   # Fallback location(s)
```

### Font Keys

- **`CJK`**: CJK (Chinese/Japanese/Korean) font
- **`SERIF`**: Serif font for body text
- **`SANS`**: Sans-serif font for headings
- **`MONO`**: Monospace font for code
- **`EMOJI`**: Emoji font

### Path Behavior

- **Empty paths (`[]`)**: Font is expected to be available system-wide (e.g., DejaVu fonts)
- **Multiple paths**: Searched in order; first existing file is used
- **Relative paths**: Resolved from repository root

## Usage

### In Python Code

```python
from tools.publishing.font_config import get_font_config

# Get font configuration loader
config = get_font_config()

# Get font name
font_name = config.get_font_name("CJK")  # "ERDA CC-BY CJK"

# Get font paths
paths = config.get_font_paths("CJK")  # List of possible paths

# Find first existing font file
font_file = config.find_font_file("CJK")  # Returns path or None

# Get default fonts for Pandoc
defaults = config.get_default_fonts()
# {'serif': 'DejaVu Serif', 'sans': 'DejaVu Sans', ...}
```

### Smart Merge with Manifest

```python
from tools.publishing.font_config import get_font_config

# Load base configuration
base = get_font_config()

# Apply publish.yml overrides
manifest_fonts = [
    {"name": "ERDA CC-BY CJK", "path": "/custom/font.ttf"}
]
merged = base.merge_manifest_fonts(manifest_fonts)

# Merged config has override applied
print(merged.get_font_paths("CJK"))
# ['/custom/font.ttf']

# Original config unchanged
print(base.get_font_paths("CJK"))
# ['.github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf', ...]
```

### Font Name Matching

```python
config = get_font_config()

# Match display name to key
key = config.match_font_key("ERDA CC-BY CJK")  # Returns: 'CJK'
key = config.match_font_key("DejaVu Serif")     # Returns: 'SERIF'

# Case-insensitive partial match
key = config.match_font_key("erda cc-by cjk")   # Returns: 'CJK'
```

### Adding a New Font

1. Add configuration to `fonts.yml`:

```yaml
fonts:
  CUSTOM:
    name: "My Custom Font"
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    source_url: "https://example.com/font"
    paths:
      - ".github/fonts/custom/custom-font.ttf"
```

2. Use in code:

```python
font_path = get_font_config().find_font_file("CUSTOM")
```

## License Compliance (AGENTS.md)

All fonts must comply with ERDA licensing requirements:

- ✅ **CC BY 4.0**: Twemoji, ERDA CC-BY CJK
- ✅ **CC BY-SA 4.0**: Compatible (not used for fonts)
- ✅ **MIT**: Compatible
- ✅ **DejaVu License**: Compatible (Bitstream Vera derivative)
- ❌ **OFL (Open Font License)**: NOT ALLOWED
- ❌ **Apache Font License**: NOT ALLOWED
- ❌ **GPL/UFL**: NOT ALLOWED
- ❌ **Proprietary**: NOT ALLOWED

**Every font entry MUST include:**
- `license`: License type
- `license_url`: Link to full license text

## Testing

Run font configuration tests:

```bash
pytest .github/gitbook_worker/tests/test_font_config.py -v
```

15 tests covering:
- Configuration loading
- Font path resolution
- Error handling
- Singleton pattern
- YAML validation

## Migration from Hardcoded Paths

### Before
```python
erda_font_locations = [
    ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf",
    ".github/gitbook_worker/tools/publishing/fonts/truetype/erdafont/erda-ccby-cjk.ttf",
]
```

### After
```python
font_config = get_font_config()
erda_font_locations = font_config.get_font_paths("CJK")
```

## Troubleshooting

### Font Not Found Warning

```
⚠ ERDA CJK Font nicht gefunden in: ['/path/to/font.ttf', ...]
```

**Solutions:**
1. Verify font file exists at one of the configured paths
2. Check file permissions
3. Add additional fallback paths to `fonts.yml`
4. Install font system-wide if `paths: []`

### YAML Parse Error

```
Exception: ...yaml.scanner.ScannerError...
```

**Solutions:**
1. Check YAML indentation (use 2 spaces, not tabs)
2. Ensure arrays use `[]` not `null` for empty values
3. Quote strings containing special characters
4. Validate YAML syntax with online validator

### Import Error

```
ModuleNotFoundError: No module named 'tools.publishing.font_config'
```

**Solutions:**
1. Ensure `sys.path` includes `.github/gitbook_worker`
2. Check file exists: `.github/gitbook_worker/tools/publishing/font_config.py`
3. Verify Python environment is activated

## See Also

- `../tools/publishing/font_config.py` - Font configuration module
- `../../tests/test_font_config.py` - Test suite
- `../../../ATTRIBUTION.md` - Font attribution and licensing
- `../../../AGENTS.md` - Licensing requirements
- `../../../docs/FONT_REFACTORING_SUMMARY.md` - Migration documentation
