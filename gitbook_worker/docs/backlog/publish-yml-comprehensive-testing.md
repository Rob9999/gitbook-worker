---
version: 0.2.0
date: 2025-12-04
history:
  - version: 0.2.0
    date: 2025-12-04
    description: |
      CRITICAL UPDATE: Added configuration-aware testing strategy.
      Tests MUST read expectations from fonts.yml instead of hardcoding font names.
      Added Section 3.0 "Test Configuration Strategy" with fixtures and anti-patterns.
      This ensures tests remain valid when users customize fonts.yml or publish.yml.
  - version: 0.1.0
    date: 2025-12-04
    description: Initial concept for comprehensive publish.yml testing and PDF content validation
---

# Comprehensive Testing for publish.yml Options and PDF Content Validation

## 1. Motivation & Problem Statement

### Current State
- **Partieller Test-Coverage**: Existierende Tests decken nur Teilbereiche der `publish.yml` Konfiguration ab:
  - `test_smart_publish_target.py`: Tests für `pdf_options` parsing (emoji_color, emoji_bxcoloremoji, paper_format, geometry)
  - `test_publisher.py`: Unit tests für `_parse_pdf_options()`, `_decide_bxcoloremoji()`
  - `test_pdf_integration.py`: End-to-end tests mit realer Pandoc-Pipeline
  - `test_documents_publishing.py`: Tests für Manifest-basierte Veröffentlichung

- **Fehlende Validierung**: Kein automatisierter Test prüft, ob das generierte PDF die konfigurierten Vorgaben tatsächlich umsetzt:
  - ✗ Sind Emojis wirklich farbig? (aktuelles Problem: schwarz-weiß trotz `emoji_color: true`)
  - ✗ Wurde die richtige Font verwendet?
  - ✗ Entsprechen Seitengrößen den `paper_format` Vorgaben?
  - ✗ Wurden Fallback-Fonts korrekt geladen?

- **Keine Combined-Markdown Validierung**: Das vorverarbeitete Markdown, welches an Pandoc übergeben wird, wird nicht systematisch getestet:
  - ✗ Wurden alle Dateien kombiniert?
  - ✗ Wurden LaTeX-Sonderzeichen korrekt escaped?
  - ✗ Sind Emoji-Spans korrekt formatiert?
  - ✗ Sind Asset-Pfade korrekt aufgelöst?

### Regression-Risiko
Aktuelle Situation zeigt: Änderungen an Publisher-Code oder Lua-Filtern können unbemerkt kritische Funktionen brechen. Das aktuelle Emoji-Problem ist ein Beispiel dafür.

## 2. Zielsetzung

### Primärziele
1. **100% Coverage aller `publish.yml` Schalter** durch automatisierte Tests
2. **PDF Content Validation API**: Programmierbare Schnittstelle zur Prüfung von PDF-Eigenschaften
3. **Combined Markdown Validation**: Automatisierte Prüfung des vorverarbeiteten Markdown-Inhalts
4. **Regression Prevention**: Früherkennung von Breaking Changes durch Integration Tests

### Sekundärziele
- Dokumentation des erwarteten Verhaltens jedes Schalters
- Performance-Benchmarks für verschiedene Konfigurationen
- Debugging-Tools für PDF-Analyse

## 3. Technischer Ansatz

### 3.0 Test Configuration Strategy (CRITICAL)

#### Problem: Tests dürfen keine hardcoded Font-Annahmen haben
**User Case:**
```
Anwender lädt gitbook_worker herunter
→ Ändert gitbook_worker/defaults/fonts.yml
→ Ändert eigene publish.yml
→ Führt pytest aus
→ ❌ Tests schlagen fehl mit "Twemoji Mozilla not found"
```

**Root Cause:** Tests prüfen auf spezifische Fonts statt auf konfigurierte Fonts.

#### Lösung: Configuration-Aware Testing

**Prinzip:** Tests MÜSSEN Erwartungen dynamisch aus aktueller Konfiguration ableiten.

**Implementation:**

##### 1. Test Fixtures für Font Configuration
```python
# gitbook_worker/tests/conftest.py

import pytest
from pathlib import Path
from gitbook_worker.tools.publishing.font_config import FontConfigLoader


@pytest.fixture(scope="session")
def default_font_config() -> FontConfigLoader:
    """Load default fonts.yml configuration for tests.
    
    Uses the actual defaults/fonts.yml from the codebase.
    Tests validate against THIS configuration, not hardcoded values.
    """
    return FontConfigLoader()


@pytest.fixture
def test_font_config(tmp_path) -> FontConfigLoader:
    """Create isolated font configuration for unit tests.
    
    Returns a temporary fonts.yml that tests can modify without
    affecting other tests or the system configuration.
    """
    test_fonts_yml = tmp_path / "fonts.yml"
    test_fonts_yml.write_text("""
version: 1.0.0
fonts:
  TEST_SERIF:
    name: "DejaVu Serif"
    paths:
      - "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    license: "Bitstream Vera License"
    license_url: "https://dejavu-fonts.github.io/License.html"
    version: "2.37"
  
  TEST_EMOJI:
    name: "Twemoji Mozilla"
    paths:
      - "/usr/share/fonts/truetype/twitter-color-emoji/TwitterColorEmoji-SVGinOT.ttf"
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    version: "15.1.0"
""", encoding="utf-8")
    return FontConfigLoader(config_path=test_fonts_yml)


@pytest.fixture
def expected_emoji_font(default_font_config: FontConfigLoader) -> str:
    """Get the configured emoji font name from fonts.yml.
    
    Tests should use THIS fixture instead of hardcoding "Twemoji Mozilla".
    If user changes fonts.yml to use a different emoji font, tests adapt automatically.
    """
    # Look for emoji font in configuration
    emoji_config = default_font_config.get_font("EMOJI")
    if emoji_config:
        return emoji_config.name
    
    # Fallback: check other keys that might contain emoji fonts
    for key in default_font_config.list_fonts():
        font = default_font_config.get_font(key)
        if font and "emoji" in font.name.lower():
            return font.name
    
    pytest.skip("No emoji font configured in fonts.yml")


@pytest.fixture
def expected_main_fonts(default_font_config: FontConfigLoader) -> dict:
    """Get configured main fonts (serif, sans, mono).
    
    Returns dict with expected font names based on current configuration.
    """
    defaults = default_font_config.get_default_fonts()
    return {
        "serif": defaults.get("serif", "DejaVu Serif"),
        "sans": defaults.get("sans", "DejaVu Sans"),
        "mono": defaults.get("mono", "DejaVu Sans Mono"),
    }


@pytest.fixture
def test_publish_config(tmp_path, expected_emoji_font, expected_main_fonts) -> dict:
    """Generate test publish.yml configuration using current fonts.yml.
    
    This ensures test configurations are always valid according to
    the current font setup.
    """
    return {
        "pdf_options": {
            "emoji_color": True,
            "emoji_bxcoloremoji": False,
            "main_font": expected_main_fonts["serif"],
            "sans_font": expected_main_fonts["sans"],
            "mono_font": expected_main_fonts["mono"],
            "mainfont_fallback": f"{expected_emoji_font}:mode=harf",
            "paper_format": "a4",
        }
    }
```

##### 2. Configuration-Aware Assertions
```python
# Instead of WRONG:
def test_emoji_color_wrong(tmp_path):
    pdf = generate_pdf(...)
    fonts = extract_fonts(pdf)
    assert "Twemoji Mozilla" in fonts  # ❌ BREAKS if user changes fonts.yml

# Do RIGHT:
def test_emoji_color_correct(tmp_path, expected_emoji_font):
    pdf = generate_pdf(...)
    fonts = extract_fonts(pdf)
    assert expected_emoji_font in fonts  # ✅ ADAPTS to configuration
```

##### 3. Test-Specific Font Configurations
```python
def test_with_custom_fonts(tmp_path, test_font_config):
    """Test can define its own font configuration."""
    # test_font_config is isolated, won't affect other tests
    assert test_font_config.get_font("TEST_EMOJI").name == "DejaVu Sans"
```

#### Benefits
1. ✅ **User-friendly:** Tests pass after user changes fonts.yml
2. ✅ **Maintainable:** No hardcoded font names scattered in tests
3. ✅ **Flexible:** Easy to test alternative font configurations
4. ✅ **Realistic:** Tests validate actual runtime behavior
5. ✅ **Isolated:** Unit tests can use synthetic configs without side effects

### 3.1 PDF Content Validation Library

#### Option A: PyPDF2 / pypdf (Empfohlen)
**Vorteile:**
- Pure Python, keine externen Abhängigkeiten
- Breite Community-Unterstützung
- Kann Fonts, Metadaten, Seitengrößen extrahieren
- Bereits in vielen Python-Projekten etabliert

**Nachteile:**
- Keine direkte Emoji-Farb-Erkennung
- Begrenzte Rendering-Analyse

**Installation:**
```bash
pip install pypdf
```

**API Beispiel:**
```python
from pypdf import PdfReader

def get_pdf_metadata(pdf_path: Path) -> dict:
    reader = PdfReader(pdf_path)
    return {
        "num_pages": len(reader.pages),
        "page_sizes": [(p.mediabox.width, p.mediabox.height) for p in reader.pages],
        "fonts": extract_fonts(reader),
        "metadata": reader.metadata,
    }
```

#### Option B: pdfplumber (Alternative)
**Vorteile:**
- Höheres Abstraktionslevel
- Bessere Text-Extraktion
- Tabellen-Analyse möglich

**Nachteile:**
- Schwergewichtiger (benötigt pdfminer.six)
- Langsamer als pypdf

#### Option C: External Tools (pdfinfo, pdffonts)
**Vorteile:**
- Bereits in Tests verwendet (`test_a1_pdf.py`)
- Sehr zuverlässig

**Nachteile:**
- Plattformabhängig
- Erfordert Parsing von Textausgaben
- Keine programmatische API

**Empfehlung:** **Hybrid-Ansatz** - pypdf für Python API + pdfinfo/pdffonts als Fallback/Validierung

### 3.2 Combined Markdown Validation

#### Zugriffspunkt
Der Combined Markdown Content wird bereits in `publisher.py` generiert:
```python
def build_pdf(..., keep_combined: bool = False):
    # Line ~2640: Combined markdown wird erstellt
    combined_md = publish_path / f"{base_name}.md"
```

Bei `keep_combined: true` wird die Datei im `publish/` Ordner behalten.

#### Validierungs-API
```python
@dataclass
class CombinedMarkdownValidation:
    has_frontmatter: bool
    num_chapters: int
    emoji_spans: List[str]  # Alle gefundenen Emoji-Spans
    latex_escaping_correct: bool
    asset_links_resolved: bool
    warnings: List[str]
    errors: List[str]

def validate_combined_markdown(md_path: Path, config: dict) -> CombinedMarkdownValidation:
    """Validate preprocessed combined markdown against configuration."""
    pass
```

### 3.3 Test-Architektur

#### Layer 1: Unit Tests (Publisher-Funktionen)
**Bestehende Tests erweitern:**
- `test_publisher.py`: Alle `_parse_pdf_options()` Zweige abdecken
- `test_smart_publish_target.py`: Alle `pdf_options` Kombinationen testen

**Neue Tests:**
```python
def test_parse_pdf_options_all_fields():
    """Test all possible pdf_options fields."""
    parsed = publisher._parse_pdf_options({
        "emoji_color": True,
        "emoji_bxcoloremoji": False,
        "main_font": "DejaVu Serif",
        "sans_font": "DejaVu Sans",
        "mono_font": "DejaVu Sans Mono",
        "mainfont_fallback": "Twemoji Mozilla:mode=harf",
        "paper_format": "a4",
        "geometry": "margin=2cm",
        "toc_depth": 3,
        # ... alle Felder ...
    })
    # Assertions für jeden Wert
```

#### Layer 2: Integration Tests (Pandoc-Pipeline)
**Erweitern: `test_pdf_integration.py`**

```python
@pytest.mark.integration
def test_pdf_respects_emoji_color_setting(tmp_path):
    """Verify PDF actually contains colored emojis when emoji_color=true."""
    md_content = "# Test\n\nHello 😀 World 🌍"
    
    # Generate PDF with emoji_color=true
    pdf_path = generate_pdf(md_content, emoji_color=True)
    
    # Validate PDF content
    validation = validate_pdf_fonts(pdf_path)
    assert "Twemoji Mozilla" in validation.fonts_used
    assert validation.harfbuzz_renderer_active
    
@pytest.mark.integration  
def test_pdf_respects_paper_format(tmp_path):
    """Verify PDF page size matches paper_format setting."""
    sizes_to_test = ["a4", "a3", "letter"]
    for paper_format in sizes_to_test:
        pdf_path = generate_pdf("# Test", paper_format=paper_format)
        metadata = get_pdf_metadata(pdf_path)
        expected = PAPER_SIZES[paper_format.upper()]
        assert_page_size_matches(metadata.page_sizes[0], expected)
```

#### Layer 3: End-to-End Tests (Full Orchestrator)
**Erweitern: `test_full_orchestrator_pipeline.py`**

```python
@pytest.mark.slow
def test_orchestrator_with_all_pdf_options(tmp_path):
    """Test full orchestrator run with all pdf_options configured."""
    publish_yml = tmp_path / "publish.yml"
    publish_yml.write_text(FULL_CONFIG_YAML)
    
    result = run_orchestrator(
        root=tmp_path,
        manifest=publish_yml,
        profile="local"
    )
    
    # Validate output PDF against config
    pdf_path = tmp_path / "publish/output.pdf"
    validation = validate_pdf_against_config(pdf_path, FULL_CONFIG_YAML)
    
    assert validation.all_checks_passed
    assert len(validation.errors) == 0
```

### 3.4 PDF Validation API Design

#### Core API Module: `gitbook_worker/tools/testing/pdf_validator.py`

```python
"""PDF Content Validation API for testing publish.yml options."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
import subprocess
import re
from pypdf import PdfReader


@dataclass
class FontInfo:
    """Information about a font used in the PDF."""
    name: str
    type: str  # Type1, TrueType, CIDFontType0, etc.
    encoding: Optional[str]
    embedded: bool


@dataclass
class PageInfo:
    """Information about a PDF page."""
    page_num: int
    width_pt: float
    height_pt: float
    width_mm: float
    height_mm: float
    orientation: str  # "portrait" or "landscape"


@dataclass
class PDFValidationResult:
    """Result of PDF validation against configuration."""
    pdf_path: Path
    config: dict
    
    # Page properties
    num_pages: int
    page_sizes: List[PageInfo]
    
    # Font properties
    fonts_used: List[FontInfo]
    main_font_matches: bool
    emoji_font_found: bool
    harfbuzz_renderer_active: bool
    
    # Content properties
    has_toc: bool
    toc_depth: int
    
    # Validation results
    all_checks_passed: bool
    errors: List[str]
    warnings: List[str]


class PDFValidator:
    """Validate PDF content against publish.yml configuration."""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        
    def get_page_sizes(self) -> List[PageInfo]:
        """Extract page sizes from PDF."""
        PT_TO_MM = 25.4 / 72.0
        pages = []
        for i, page in enumerate(self.reader.pages, start=1):
            width_pt = float(page.mediabox.width)
            height_pt = float(page.mediabox.height)
            pages.append(PageInfo(
                page_num=i,
                width_pt=width_pt,
                height_pt=height_pt,
                width_mm=width_pt * PT_TO_MM,
                height_mm=height_pt * PT_TO_MM,
                orientation="portrait" if height_pt > width_pt else "landscape"
            ))
        return pages
    
    def get_fonts(self) -> List[FontInfo]:
        """Extract font information using pdffonts tool."""
        # Try external tool first for comprehensive info
        try:
            output = subprocess.check_output(
                ["pdffonts", str(self.pdf_path)],
                encoding="utf-8",
                stderr=subprocess.DEVNULL
            )
            return self._parse_pdffonts_output(output)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to pypdf
            return self._extract_fonts_pypdf()
    
    def _parse_pdffonts_output(self, output: str) -> List[FontInfo]:
        """Parse pdffonts command output."""
        fonts = []
        for line in output.splitlines()[2:]:  # Skip header lines
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                fonts.append(FontInfo(
                    name=parts[0],
                    type=parts[1],
                    encoding=parts[2] if len(parts) > 2 else None,
                    embedded="yes" in line.lower()
                ))
        return fonts
    
    def _extract_fonts_pypdf(self) -> List[FontInfo]:
        """Extract fonts using pypdf (fallback method)."""
        fonts = []
        for page in self.reader.pages:
            if "/Font" in page["/Resources"]:
                font_dict = page["/Resources"]["/Font"]
                for font_name in font_dict:
                    font_obj = font_dict[font_name].get_object()
                    fonts.append(FontInfo(
                        name=str(font_obj.get("/BaseFont", "Unknown")),
                        type=str(font_obj.get("/Subtype", "Unknown")),
                        encoding=None,
                        embedded=("/FontDescriptor" in font_obj)
                    ))
        return fonts
    
    def validate_against_config(self, config: dict) -> PDFValidationResult:
        """Validate PDF against publish.yml configuration."""
        pdf_options = config.get("pdf_options", {})
        
        errors = []
        warnings = []
        
        # Validate page sizes
        page_sizes = self.get_page_sizes()
        expected_format = pdf_options.get("paper_format", "a4").upper()
        if expected_format in PAPER_SIZES:
            expected_size = PAPER_SIZES[expected_format]
            for page in page_sizes:
                if not self._page_size_matches(page, expected_size):
                    errors.append(
                        f"Page {page.page_num} size mismatch: "
                        f"expected {expected_size}, got ({page.width_mm:.1f}, {page.height_mm:.1f})mm"
                    )
        
        # Validate fonts
        fonts = self.get_fonts()
        font_names = [f.name for f in fonts]
        
        main_font = pdf_options.get("main_font")
        main_font_matches = any(main_font in name for name in font_names) if main_font else True
        if main_font and not main_font_matches:
            errors.append(f"Main font '{main_font}' not found in PDF")
        
        # Check emoji configuration
        emoji_color = pdf_options.get("emoji_color", False)
        emoji_font_found = any("emoji" in name.lower() for name in font_names)
        
        if emoji_color and not emoji_font_found:
            errors.append("emoji_color=true but no emoji font found in PDF")
        
        # Check for HarfBuzz renderer (indirect: look for emoji font with mode=harf in config)
        fallback = pdf_options.get("mainfont_fallback", "")
        harfbuzz_active = "mode=harf" in fallback and emoji_font_found
        
        return PDFValidationResult(
            pdf_path=self.pdf_path,
            config=config,
            num_pages=len(page_sizes),
            page_sizes=page_sizes,
            fonts_used=fonts,
            main_font_matches=main_font_matches,
            emoji_font_found=emoji_font_found,
            harfbuzz_renderer_active=harfbuzz_active,
            has_toc=self._has_toc(),
            toc_depth=self._get_toc_depth(),
            all_checks_passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _page_size_matches(self, page: PageInfo, expected: Tuple[float, float], tolerance: float = 5.0) -> bool:
        """Check if page size matches expected size within tolerance (mm)."""
        exp_width, exp_height = expected
        return (abs(page.width_mm - exp_width) <= tolerance and
                abs(page.height_mm - exp_height) <= tolerance)
    
    def _has_toc(self) -> bool:
        """Check if PDF has a table of contents."""
        return self.reader.outline is not None and len(self.reader.outline) > 0
    
    def _get_toc_depth(self) -> int:
        """Get maximum depth of table of contents."""
        if not self.reader.outline:
            return 0
        return self._calc_outline_depth(self.reader.outline)
    
    def _calc_outline_depth(self, outline, current_depth=1) -> int:
        """Recursively calculate outline depth."""
        max_depth = current_depth
        for item in outline:
            if isinstance(item, list):
                depth = self._calc_outline_depth(item, current_depth + 1)
                max_depth = max(max_depth, depth)
        return max_depth


# Paper sizes in mm (width, height)
PAPER_SIZES = {
    "A4": (210, 297),
    "A3": (297, 420),
    "A2": (420, 594),
    "A1": (594, 841),
    "LETTER": (215.9, 279.4),
    "LEGAL": (215.9, 355.6),
}


def validate_pdf_against_config(pdf_path: Path, config: dict) -> PDFValidationResult:
    """Convenience function to validate a PDF against configuration."""
    validator = PDFValidator(pdf_path)
    return validator.validate_against_config(config)


__all__ = [
    "PDFValidator",
    "PDFValidationResult",
    "FontInfo",
    "PageInfo",
    "validate_pdf_against_config",
    "PAPER_SIZES",
]
```

### 3.5 Combined Markdown Validation API

#### Core API Module: `gitbook_worker/tools/testing/markdown_validator.py`

```python
"""Combined Markdown Validation API for testing preprocessing pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re


@dataclass
class EmojiSpan:
    """Represents an emoji span in markdown."""
    unicode: str
    codepoint: str
    line_num: int
    context: str  # Surrounding text


@dataclass
class MarkdownValidationResult:
    """Result of combined markdown validation."""
    md_path: Path
    
    # Structure
    has_frontmatter: bool
    frontmatter_data: dict
    num_chapters: int
    chapter_titles: List[str]
    
    # Content
    emoji_spans: List[EmojiSpan]
    num_images: int
    num_tables: int
    num_code_blocks: int
    
    # Escaping
    unescaped_special_chars: List[Tuple[int, str]]  # (line_num, char)
    latex_escaping_correct: bool
    
    # Asset resolution
    asset_links: List[str]
    broken_asset_links: List[str]
    
    # Validation
    all_checks_passed: bool
    errors: List[str]
    warnings: List[str]


class MarkdownValidator:
    """Validate combined markdown content."""
    
    # LaTeX special characters that need escaping
    LATEX_SPECIAL_CHARS = r'%$&_#{}~^\\'
    
    # Regex patterns
    EMOJI_SPAN_PATTERN = re.compile(r':[\w-]+:|[\U0001F300-\U0001FAFF]')
    IMAGE_PATTERN = re.compile(r'!\[.*?\]\((.*?)\)')
    CHAPTER_PATTERN = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    def __init__(self, md_path: Path):
        self.md_path = md_path
        self.content = md_path.read_text(encoding="utf-8")
        self.lines = self.content.splitlines()
    
    def validate(self, config: Optional[dict] = None) -> MarkdownValidationResult:
        """Validate combined markdown."""
        errors = []
        warnings = []
        
        # Extract frontmatter
        has_frontmatter, frontmatter_data = self._extract_frontmatter()
        
        # Find chapters
        chapter_titles = self.CHAPTER_PATTERN.findall(self.content)
        
        # Find emojis
        emoji_spans = self._find_emoji_spans()
        
        # Check LaTeX escaping
        unescaped = self._find_unescaped_special_chars()
        if unescaped:
            errors.append(f"Found {len(unescaped)} unescaped LaTeX special characters")
        
        # Validate asset links
        asset_links = self._find_asset_links()
        broken_links = self._check_broken_links(asset_links)
        if broken_links:
            warnings.append(f"Found {len(broken_links)} potentially broken asset links")
        
        return MarkdownValidationResult(
            md_path=self.md_path,
            has_frontmatter=has_frontmatter,
            frontmatter_data=frontmatter_data,
            num_chapters=len(chapter_titles),
            chapter_titles=chapter_titles,
            emoji_spans=emoji_spans,
            num_images=len(asset_links),
            num_tables=self.content.count("|"),  # Rough estimate
            num_code_blocks=self.content.count("```"),
            unescaped_special_chars=unescaped,
            latex_escaping_correct=len(unescaped) == 0,
            asset_links=asset_links,
            broken_asset_links=broken_links,
            all_checks_passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _extract_frontmatter(self) -> Tuple[bool, dict]:
        """Extract YAML frontmatter if present."""
        match = self.FRONTMATTER_PATTERN.match(self.content)
        if not match:
            return False, {}
        
        import yaml
        try:
            data = yaml.safe_load(match.group(1))
            return True, data or {}
        except yaml.YAMLError:
            return True, {}
    
    def _find_emoji_spans(self) -> List[EmojiSpan]:
        """Find all emoji occurrences."""
        emojis = []
        for line_num, line in enumerate(self.lines, start=1):
            for match in self.EMOJI_SPAN_PATTERN.finditer(line):
                emoji_char = match.group(0)
                codepoint = f"U+{ord(emoji_char):04X}"
                emojis.append(EmojiSpan(
                    unicode=emoji_char,
                    codepoint=codepoint,
                    line_num=line_num,
                    context=line[max(0, match.start()-20):match.end()+20]
                ))
        return emojis
    
    def _find_unescaped_special_chars(self) -> List[Tuple[int, str]]:
        """Find LaTeX special characters that aren't properly escaped."""
        unescaped = []
        
        # Skip code blocks and inline code
        in_code_block = False
        for line_num, line in enumerate(self.lines, start=1):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            # Check for unescaped special chars (simplified check)
            for char in self.LATEX_SPECIAL_CHARS:
                if char in line:
                    # Check if it's escaped
                    idx = 0
                    while idx < len(line):
                        idx = line.find(char, idx)
                        if idx == -1:
                            break
                        # Check if preceded by backslash
                        if idx == 0 or line[idx-1] != '\\':
                            # Could be unescaped (needs more sophisticated check)
                            unescaped.append((line_num, char))
                        idx += 1
        
        return unescaped
    
    def _find_asset_links(self) -> List[str]:
        """Find all asset links (images, etc.)."""
        return self.IMAGE_PATTERN.findall(self.content)
    
    def _check_broken_links(self, links: List[str]) -> List[str]:
        """Check if asset links are broken."""
        broken = []
        base_dir = self.md_path.parent
        
        for link in links:
            # Skip external URLs
            if link.startswith(("http://", "https://")):
                continue
            
            # Check if file exists
            asset_path = base_dir / link
            if not asset_path.exists():
                broken.append(link)
        
        return broken


def validate_combined_markdown(md_path: Path, config: Optional[dict] = None) -> MarkdownValidationResult:
    """Convenience function to validate combined markdown."""
    validator = MarkdownValidator(md_path)
    return validator.validate(config)


__all__ = [
    "MarkdownValidator",
    "MarkdownValidationResult",
    "EmojiSpan",
    "validate_combined_markdown",
]
```

## 4. Test Coverage Matrix

### 4.1 `pdf_options` Coverage

| Option | Unit Test | Integration Test | E2E Test | Notes |
|--------|-----------|------------------|----------|-------|
| `emoji_color` | ✅ Exists | ⚠️ Partial | ❌ Missing | Needs PDF content validation |
| `emoji_bxcoloremoji` | ✅ Exists | ❌ Missing | ❌ Missing | Needs bxcoloremoji vs HarfBuzz validation |
| `main_font` | ✅ Exists | ⚠️ Partial | ❌ Missing | Needs PDF font extraction check |
| `sans_font` | ✅ Exists | ❌ Missing | ❌ Missing | Needs PDF font extraction check |
| `mono_font` | ✅ Exists | ❌ Missing | ❌ Missing | Needs PDF font extraction check |
| `mainfont_fallback` | ✅ Exists | ⚠️ Partial | ❌ Missing | Needs fallback activation validation |
| `paper_format` | ⚠️ Partial | ❌ Missing | ❌ Missing | Needs page size validation |
| `geometry` | ⚠️ Partial | ❌ Missing | ❌ Missing | Needs margin validation |
| `toc_depth` | ❌ Missing | ❌ Missing | ❌ Missing | Needs TOC structure validation |
| `pdf_engine` | ⚠️ Partial | ❌ Missing | ❌ Missing | Needs engine verification |

**Legende:**
- ✅ Exists: Test vorhanden und vollständig
- ⚠️ Partial: Test vorhanden aber unvollständig
- ❌ Missing: Test fehlt komplett

### 4.2 Neue Tests die implementiert werden müssen

#### test_pdf_content_validation.py (NEU)
```python
"""Integration tests for PDF content validation."""

import pytest
from pathlib import Path
from gitbook_worker.tools.testing.pdf_validator import (
    PDFValidator,
    validate_pdf_against_config,
    PAPER_SIZES
)
from gitbook_worker.tools.publishing import publisher


@pytest.mark.integration
class TestPDFContentValidation:
    """Test that generated PDFs match configuration.
    
    IMPORTANT: These tests are configuration-aware. They read the current
    fonts.yml to determine expected font names, not hardcoded values.
    This ensures tests remain valid when users customize their font setup.
    """
    
    def test_emoji_color_produces_colored_emojis(
        self, tmp_path, expected_emoji_font, default_font_config
    ):
        """Verify emoji_color=true produces configured emoji font in PDF.
        
        This test dynamically determines which emoji font should be present
        based on fonts.yml configuration. If user changes from Twemoji Mozilla
        to another emoji font, test adapts automatically.
        """
        md_content = "# Emoji Test\n\nHello 😀 World 🌍 Test 🎉"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        
        pdf_file = tmp_path / "test.pdf"
        
        # Build with emoji_color=true using configured emoji font
        emoji_fallback = f"{expected_emoji_font}:mode=harf"
        
        success, error = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False),
            variables={"mainfontfallback": emoji_fallback}
        )
        
        assert success, f"PDF generation failed: {error}"
        assert pdf_file.exists()
        
        # Validate PDF content against configuration
        validator = PDFValidator(pdf_file)
        fonts = validator.get_fonts()
        font_names = [f.name for f in fonts]
        
        # Check that CONFIGURED emoji font is present (not hardcoded "Twemoji Mozilla")
        emoji_font_found = any(
            expected_emoji_font.lower() in name.lower() for name in font_names
        )
        assert emoji_font_found, (
            f"Configured emoji font '{expected_emoji_font}' not found in PDF. "
            f"Available fonts: {font_names}. "
            f"Check fonts.yml configuration."
        )
    
    def test_emoji_bxcoloremoji_false_uses_harfbuzz(self, tmp_path):
        """Verify emoji_bxcoloremoji=false activates HarfBuzz renderer."""
        md_content = "# Test 😀"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        
        pdf_file = tmp_path / "test.pdf"
        
        success, _ = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False)
        )
        
        assert success
        
        # Check that bxcoloremoji was NOT used (indirect check via fonts)
        validator = PDFValidator(pdf_file)
        fonts = validator.get_fonts()
        
        # Twemoji Mozilla should be embedded as TrueType/CIDFont, not via bxcoloremoji
        emoji_fonts = [f for f in fonts if "emoji" in f.name.lower()]
        assert len(emoji_fonts) > 0, "No emoji font found"
        assert any(f.embedded for f in emoji_fonts), "Emoji font not embedded"
    
    def test_paper_format_a4(self, tmp_path):
        """Verify paper_format=a4 produces A4 pages."""
        self._test_paper_format(tmp_path, "a4", PAPER_SIZES["A4"])
    
    def test_paper_format_a3(self, tmp_path):
        """Verify paper_format=a3 produces A3 pages."""
        self._test_paper_format(tmp_path, "a3", PAPER_SIZES["A3"])
    
    def test_paper_format_letter(self, tmp_path):
        """Verify paper_format=letter produces Letter pages."""
        self._test_paper_format(tmp_path, "letter", PAPER_SIZES["LETTER"])
    
    def _test_paper_format(self, tmp_path, format_name, expected_size):
        """Helper to test paper format."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent", encoding="utf-8")
        
        pdf_file = tmp_path / f"test-{format_name}.pdf"
        
        success, _ = publisher.build_pdf(
            path=str(md_file),
            out=pdf_file.name,
            typ="file",
            publish_dir=str(tmp_path),
            paper_format=format_name
        )
        
        assert success
        
        # Validate page size
        validator = PDFValidator(pdf_file)
        pages = validator.get_page_sizes()
        
        assert len(pages) > 0
        page = pages[0]
        
        # Allow 5mm tolerance
        assert abs(page.width_mm - expected_size[0]) <= 5.0, \
            f"Width mismatch: expected {expected_size[0]}mm, got {page.width_mm}mm"
        assert abs(page.height_mm - expected_size[1]) <= 5.0, \
            f"Height mismatch: expected {expected_size[1]}mm, got {page.height_mm}mm"
    
    def test_main_font_setting(self, tmp_path, expected_main_fonts):
        """Verify main_font setting is respected using configured fonts."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nSome text content.", encoding="utf-8")
        
        pdf_file = tmp_path / "test.pdf"
        
        # Use CONFIGURED serif font, not hardcoded
        expected_serif = expected_main_fonts["serif"]
        
        success, _ = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            variables={"mainfont": expected_serif}
        )
        
        assert success
        
        # Check that CONFIGURED font is used
        validator = PDFValidator(pdf_file)
        fonts = validator.get_fonts()
        font_names = [f.name for f in fonts]
        
        # Flexible matching: check if configured font name appears in PDF fonts
        serif_found = any(expected_serif.lower() in name.lower() for name in font_names)
        assert serif_found, (
            f"Configured main font '{expected_serif}' not found in PDF. "
            f"Available fonts: {font_names}"
        )
    
    def test_validate_against_full_config(
        self, tmp_path, test_publish_config, expected_emoji_font, expected_main_fonts
    ):
        """Test validation against complete publish.yml config.
        
        Config is generated from fonts.yml, ensuring tests remain valid
        when font configuration changes.
        """
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test 😀\n\nContent", encoding="utf-8")
        
        pdf_file = tmp_path / "test.pdf"
        
        # Use dynamically generated config from fonts.yml
        config = test_publish_config
        
        success, _ = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            emoji_options=publisher.EmojiOptions(
                color=config["pdf_options"]["emoji_color"],
                bxcoloremoji=config["pdf_options"]["emoji_bxcoloremoji"]
            ),
            variables={
                "mainfont": config["pdf_options"]["main_font"],
                "mainfontfallback": config["pdf_options"]["mainfont_fallback"]
            }
        )
        
        assert success
        
        # Validate using API - config matches fonts.yml
        result = validate_pdf_against_config(pdf_file, config)
        
        assert result.all_checks_passed, f"Validation errors: {result.errors}"
        assert result.emoji_font_found, (
            f"Expected emoji font '{expected_emoji_font}' not found in PDF"
        )
        assert result.main_font_matches
        assert len(result.errors) == 0
```

#### test_combined_markdown_validation.py (NEU)
```python
"""Tests for combined markdown validation."""

import pytest
from pathlib import Path
from gitbook_worker.tools.testing.markdown_validator import (
    MarkdownValidator,
    validate_combined_markdown
)
from gitbook_worker.tools.publishing import publisher


@pytest.mark.integration
class TestCombinedMarkdownValidation:
    """Test validation of preprocessed combined markdown."""
    
    def test_combined_markdown_structure(self, tmp_path):
        """Test that combined markdown has correct structure."""
        # Create test content
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        
        (content_dir / "chapter1.md").write_text("# Chapter 1\n\nContent 1", encoding="utf-8")
        (content_dir / "chapter2.md").write_text("# Chapter 2\n\nContent 2", encoding="utf-8")
        
        publish_dir = tmp_path / "publish"
        publish_dir.mkdir()
        
        # Build PDF with keep_combined=True
        success, _ = publisher.build_pdf(
            path=str(content_dir),
            out="test.pdf",
            typ="folder",
            publish_dir=str(publish_dir),
            keep_combined=True
        )
        
        assert success
        
        # Validate combined markdown
        combined_md = publish_dir / "test.md"
        assert combined_md.exists(), "Combined markdown not found"
        
        validator = MarkdownValidator(combined_md)
        result = validator.validate()
        
        assert result.num_chapters >= 2, f"Expected at least 2 chapters, got {result.num_chapters}"
        assert "Chapter 1" in result.chapter_titles
        assert "Chapter 2" in result.chapter_titles
    
    def test_emoji_spans_detected(self, tmp_path):
        """Test that emoji spans are correctly detected."""
        md_content = "# Test\n\n😀 Hello 🌍 World 🎉"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        
        validator = MarkdownValidator(md_file)
        result = validator.validate()
        
        assert len(result.emoji_spans) >= 3, f"Expected 3 emojis, found {len(result.emoji_spans)}"
    
    def test_latex_escaping_check(self, tmp_path):
        """Test LaTeX special character escaping detection."""
        # Content with unescaped LaTeX chars (intentionally problematic)
        md_content = "# Test\n\nPrice: $100 & more\n\nDiscount: 50%"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        
        validator = MarkdownValidator(md_file)
        result = validator.validate()
        
        # Should detect unescaped $ & %
        assert len(result.unescaped_special_chars) > 0, \
            "Should detect unescaped LaTeX special characters"
```

## 5. Implementation Plan

### Phase 1: Foundation (Week 1)
**Ziel:** Basis-Infrastruktur schaffen

1. **Dependency Installation**
   ```bash
   pip install pypdf pyyaml
   ```

2. **Test Fixtures für Configuration-Aware Testing** ⭐ CRITICAL
   - [ ] Erweitere `gitbook_worker/tests/conftest.py` mit Font-Fixtures:
     - `@pytest.fixture default_font_config` - Lädt aktuelle fonts.yml
     - `@pytest.fixture test_font_config` - Isolated test configuration
     - `@pytest.fixture expected_emoji_font` - Dynamisch aus fonts.yml
     - `@pytest.fixture expected_main_fonts` - Serif/Sans/Mono aus config
     - `@pytest.fixture test_publish_config` - Gültige publish.yml basierend auf fonts.yml
   - [ ] Dokumentiere Fixture-Usage in Docstrings
   - [ ] Schreibe Unit Tests für Fixtures selbst

3. **API Module Creation**
   - [ ] Erstelle `gitbook_worker/tools/testing/__init__.py`
   - [ ] Implementiere `pdf_validator.py` (Core API)
     - **WICHTIG:** Validator MUSS `expected_fonts` als Parameter akzeptieren
     - Keine hardcoded Font-Namen in Assertions
   - [ ] Implementiere `markdown_validator.py` (Core API)
   - [ ] Schreibe Docstrings und Type Hints mit Config-Awareness-Hinweisen

4. **Basic Unit Tests**
   - [ ] Test `PDFValidator.get_page_sizes()`
   - [ ] Test `PDFValidator.get_fonts()`
   - [ ] Test `MarkdownValidator._find_emoji_spans()`
   - [ ] Test Font-Fixtures mit verschiedenen fonts.yml Varianten

**Deliverables:**
- Funktionierende Validation APIs (configuration-aware!)
- Font-Configuration Fixtures in conftest.py
- Unit tests mit >=80% coverage für neue Module
- Dokumentation: "How to write config-agnostic tests"

### Phase 2: Integration Tests (Week 2)
**Ziel:** PDF Content Validation Tests

1. **PDF Content Tests**
   - [ ] Erstelle `test_pdf_content_validation.py`
   - [ ] Implementiere Emoji-Farb-Tests
   - [ ] Implementiere Paper-Format-Tests
   - [ ] Implementiere Font-Tests

2. **Combined Markdown Tests**
   - [ ] Erstelle `test_combined_markdown_validation.py`
   - [ ] Implementiere Struktur-Tests
   - [ ] Implementiere Emoji-Span-Tests
   - [ ] Implementiere LaTeX-Escaping-Tests

**Deliverables:**
- Mindestens 10 neue Integration Tests
- Alle Tests grün (oder dokumentierte Failures für bestehende Bugs)

### Phase 3: Coverage Extension (Week 3)
**Ziel:** 100% Coverage aller `pdf_options`

1. **Fehlende Option Tests**
   - [ ] `toc_depth` Tests
   - [ ] `geometry` Tests (Margin-Validierung)
   - [ ] `pdf_engine` Tests (LuaLaTeX vs XeLaTeX)
   - [ ] Alle Fallback-Font-Kombinationen

2. **Edge Cases**
   - [ ] Leere Konfiguration (Defaults)
   - [ ] Invalide Werte (Error Handling)
   - [ ] Kombinationen (emoji_color + bxcoloremoji Interaktionen)

**Deliverables:**
- Test Coverage Matrix zu 100% gefüllt
- Dokumentation aller erwarteten Verhaltensweisen

### Phase 4: CI/CD Integration (Week 4)
**Ziel:** Automatisierung und Monitoring

1. **Pytest Configuration**
   - [ ] Marker für `@pytest.mark.pdf_validation`
   - [ ] Separate Test-Suite für lange Tests
   - [ ] Coverage Reports für neue Module

2. **GitHub Actions Workflow**
   - [ ] Add PDF validation tests zu CI
   - [ ] Matrix-Tests für verschiedene Konfigurationen
   - [ ] Artifact Upload für Failed PDFs

3. **Dokumentation**
   - [ ] README für Testing-APIs
   - [ ] Beispiele für neue Tests
   - [ ] Troubleshooting Guide

**Deliverables:**
- CI Pipeline mit PDF Validation
- Vollständige Dokumentation

## 6. Acceptance Criteria

### Funktionale Kriterien
- ✅ Alle `pdf_options` Schalter haben mindestens einen Integration Test
- ✅ PDF Content Validation API kann:
  - Seitengrößen extrahieren und validieren
  - Verwendete Fonts identifizieren
  - Emoji-Font-Aktivierung prüfen
  - HarfBuzz Renderer erkennen
- ✅ Combined Markdown Validation API kann:
  - Struktur analysieren (Chapters, Sections)
  - Emoji-Spans zählen
  - LaTeX-Escaping prüfen
  - Asset-Links validieren
- ✅ Alle Tests laufen automatisiert in CI/CD
- ✅ Regression Detection: Neue Changes brechen keine bestehenden Validierungen

### Qualitätskriterien
- ✅ Test Coverage >= 80% für neue Module
- ✅ Alle Tests dokumentiert mit klaren Docstrings
- ✅ Type Hints für alle Public APIs
- ✅ Performance: Validation läuft in < 1 Sekunde pro PDF
- ✅ Keine False Positives in Validation Errors

### Dokumentationskriterien
- ✅ Backlog-Dokument im `gitbook_worker/docs/backlog/` (dieses Dokument)
- ✅ API Dokumentation in Docstrings
- ✅ Beispiel-Tests für neue Entwickler
- ✅ Troubleshooting Guide für häufige Probleme

## 7. Offene Fragen & Diskussionspunkte

### Technische Entscheidungen
1. **PyPDF vs pdfplumber vs External Tools?**
   - Vorschlag: Hybrid mit pypdf + pdfinfo/pdffonts
   - Diskussion: Welche Balance zwischen Plattformunabhängigkeit und Zuverlässigkeit?

2. **Emoji-Farb-Erkennung**
   - Problem: Keine direkte API zur Erkennung ob Emojis farbig gerendert wurden
   - Lösungsansätze:
     - Font-basiert: Prüfe ob **konfigurierter** Color-Emoji-Font verwendet wurde ✅
     - Rendering-basiert: Convert zu PNG und analysiere Pixel (komplex)
     - LaTeX-Log-basiert: Parse Compiler-Output für HarfBuzz-Meldungen
   - **Entscheidung benötigt**: Welcher Ansatz ist zuverlässig genug?
   - **WICHTIG**: Test muss `expected_emoji_font` aus fonts.yml lesen, nicht "Twemoji Mozilla" hardcoden!

3. **Configuration Isolation in Tests**
   - Frage: Wie verhindern wir Cross-Test-Contamination bei Font-Configs?
   - Ansatz: Jeder Unit-Test bekommt `test_font_config` fixture mit tmp_path
   - Integration Tests nutzen `default_font_config` (read-only, shared)
   - Wichtig für Parallelisierung mit pytest-xdist

3. **Test Performance**
   - Integration Tests mit PDF-Generierung sind langsam (~5-10 Sekunden pro Test)
   - Mitigation: Caching, Parallele Execution, Test-Sharding?

### Scope-Fragen
1. **Sollten wir andere Output-Formate testen?**
   - Aktuell nur PDF
   - HTML/EPUB auch relevant?

2. **Sollten wir Performance-Benchmarks hinzufügen?**
   - Z.B. Build-Zeit pro Konfiguration messen
   - Regressions-Alerts bei Performance-Verschlechterung

3. **Sollten wir Visual Regression Tests hinzufügen?**
   - Z.B. Screenshot-Vergleiche von PDFs
   - Tools: Percy, BackstopJS, PDF-to-Image + ImageMagick

## 8. Risiken & Mitigations

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| pypdf kann nicht alle PDF-Features lesen | Mittel | Hoch | Fallback auf externe Tools (pdffonts, pdfinfo) |
| Tests sind zu langsam für CI | Hoch | Mittel | Parallelisierung, Test-Sharding, Caching |
| False Positives in Validierung | Mittel | Hoch | Toleranzen einbauen, manuelle Review-Phase |
| Emoji-Farb-Erkennung unzuverlässig | Hoch | Hoch | Mehrere Indikatoren kombinieren (Font + Log + Config) |
| Breaking Changes in Pandoc | Niedrig | Hoch | Version-Pinning, Compatibility Layer |

## 9. Success Metrics

### Quantitative Metriken
- **Test Coverage:** >= 80% für neue Module, >= 90% für kritische Pfade
- **Regression Rate:** < 1 unentdeckte Regression pro Release
- **Test Execution Time:** < 5 Minuten für Full Suite
- **False Positive Rate:** < 5% in Validation Errors

### Qualitative Metriken
- **Developer Confidence:** Entwickler vertrauen darauf dass Tests Breaking Changes erkennen
- **Debugging Speed:** Zeit zur Diagnose von PDF-Problemen reduziert um 50%
- **Documentation Quality:** Alle `pdf_options` haben dokumentiertes erwartetes Verhalten

## 10. Referenzen & Ressourcen

### Externe Libraries
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [pdfplumber Repository](https://github.com/jsvine/pdfplumber)
- [Pandoc Manual - PDF Options](https://pandoc.org/MANUAL.html#creating-a-pdf)

### Interne Dokumentation
- `AGENTS.md`: Testing-Requirements (Zeile 4)
- `test_publisher.py`: Bestehende Unit Tests
- `test_pdf_integration.py`: Bestehende Integration Tests
- `publisher.py`: PDF Generation Pipeline

### Tools
- `pdffonts`: Teil von Poppler Utils
- `pdfinfo`: Teil von Poppler Utils
- `pytest`: Testing Framework
- `pytest-xdist`: Parallelisierung

## 11. Anti-Patterns: How NOT to Write Tests

### ❌ WRONG: Hardcoded Font Assumptions
```python
def test_emoji_wrong():
    """BAD: Breaks when user changes fonts.yml"""
    pdf = generate_pdf("Test 😀")
    fonts = extract_fonts(pdf)
    
    # ❌ Hardcoded expectation
    assert "Twemoji Mozilla" in fonts
    
    # Problem: If user configures a different emoji font, test fails!
```

### ✅ RIGHT: Configuration-Aware Test
```python
def test_emoji_correct(expected_emoji_font):
    """GOOD: Adapts to current fonts.yml configuration"""
    pdf = generate_pdf("Test 😀")
    fonts = extract_fonts(pdf)
    
    # ✅ Dynamic expectation from fixtures
    assert expected_emoji_font in fonts, (
        f"Expected '{expected_emoji_font}' from fonts.yml, "
        f"but found: {fonts}"
    )
```

### ❌ WRONG: System-Dependent Paths
```python
def test_font_path_wrong():
    """BAD: Only works on developer's machine"""
    font_path = "/home/developer/fonts/emoji.ttf"  # ❌
    assert Path(font_path).exists()
```

### ✅ RIGHT: Fixture-Driven Paths
```python
def test_font_path_correct(default_font_config):
    """GOOD: Resolves paths from configuration"""
    emoji_config = default_font_config.get_font("EMOJI")
    
    # Fonts may be downloaded or in fonts-storage/
    # Let FontConfigLoader resolve the actual path
    assert emoji_config is not None
    assert len(emoji_config.paths) > 0
```

### ❌ WRONG: Coupling to Specific Font Versions
```python
def test_version_wrong():
    """BAD: Fails when fonts get updated"""
    assert get_emoji_font_version() == "15.1.0"  # ❌
```

### ✅ RIGHT: Version-Agnostic or Config-Based
```python
def test_version_correct(default_font_config):
    """GOOD: Validates version format, not specific value"""
    emoji_config = default_font_config.get_font("EMOJI")
    
    # Check that version is specified (compliance requirement)
    assert emoji_config.version is not None
    assert emoji_config.version != ""
    
    # Optionally validate semver format
    assert re.match(r'^\d+\.\d+\.\d+', emoji_config.version)
```

### Key Principle
**Tests should validate BEHAVIOR, not CONFIGURATION DETAILS.**

Good test: "When emoji_color=true, PDF uses the configured emoji font"
Bad test: "When emoji_color=true, PDF uses Twemoji Mozilla v15.1.0"

## 12. Next Steps nach Konzept-Review

**Nach Abstimmung mit Dir:**

1. **Priorisierung:** Welche Phase sollen wir zuerst angehen?
   - Empfehlung: Phase 1 (Foundation) + Emoji-Problem Fix
   
2. **Scope Refinement:** Welche `pdf_options` sind kritisch?
   - Empfehlung: emoji_color, emoji_bxcoloremoji, main_font, paper_format

3. **Emoji-Problem Debugging:** Sollen wir zuerst das aktuelle Problem lösen?
   - Ja, dann haben wir ein konkretes Beispiel für die Tests

4. **Timeline:** Realistischer Zeitrahmen?
   - 4 Wochen für alle Phasen oder länger?

5. **Font Fixture Implementation:** Soll ich die conftest.py Fixtures jetzt schon implementieren?
   - Vorteil: Können sofort für Emoji-Debugging genutzt werden
   - Nachteil: Noch kein vollständiger Test-Plan approved

---

**Version:** 0.1.0  
**Status:** Konzept - Wartet auf Review und Abstimmung  
**Nächster Schritt:** Diskussion und Priorisierung mit Maintainer
