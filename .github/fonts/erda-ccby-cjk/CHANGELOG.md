# Changelog - ERDA CC-BY CJK Font Generator

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-08 - Devanagari/Hindi Support

### Added
- **Devanagari (Hindi) Script Support** (`generator/devanagari.py`)
  - 38 Devanagari characters (base + extended)
  - Essential Hindi characters: ह, ि, न, ्, द, ी, य, ं
  - Extended consonants and vowels for comprehensive coverage
  - Combining marks support (vowel signs, anusvara, virama)
  - CC BY 4.0 licensed 8×8 monospace bitmaps
  
- **Character Index Updates**
  - Added Devanagari source to character index
  - Updated statistics output to include Devanagari count
  - Extended character lookup to support Hindi characters

### Changed
- **Font Size**: Increased from ~90 KB to 141 KB
- **Character Count**: Expanded from 303 to 543 glyphs
- **Character Sources**:
  - Hanzi/Kanji: 137 → 206 (37.9%)
  - Hangul: 91 → 124 (22.8%)
  - Katakana: 27 → 84 (15.5%)
  - Hiragana: 27 → 35 (6.4%)
  - Devanagari: 0 → 38 (7.0%) **NEW**
  - Punctuation: 11 → 46 (8.5%)
  - Fallback: 10 (1.8%)

### Fixed
- Missing Devanagari characters in PDF builds
- Font warnings for Hindi license translations

---

## [1.0.0] - 2025-11-08 - Sprint 1 Foundation & Critical Fixes

### Added
- **Character Index System** (`generator/character_index.py`, 210 LOC)
  - O(1) character lookup replacing O(n) linear search
  - Pre-computed Dakuten/Handakuten combinations
  - Singleton pattern for efficient reuse
  - Character statistics and introspection
  
- **Configuration System** (`generator/config.py`, 363 LOC)
  - Dataclass-based configuration with validation
  - YAML configuration file support
  - GridConfig, FontMetadata, BuildConfig, CharacterConfig sections
  - Externalized hardcoded constants (EM, PIXELS, CELL, MARGIN)
  - Example configuration file (`font-config.example.yaml`)
  
- **Benchmarking Suite** (`tools/benchmark.py`, 277 LOC)
  - Performance tracking with build time, file size, processing rate
  - Multiple run averaging with standard deviation
  - Git commit tracking for historical comparison
  - JSON result export for long-term analysis
  - Baseline benchmark saved (`benchmarks/benchmark-20251108-205331.json`)
  
- **Translation Module** (`generator/translations.py`, 124 LOC)
  - Extracted translation strings to separate module
  - TranslationSet dataclass with character analysis
  - Support for Japanese, Korean, Chinese Traditional translations
  
- **Duplicate Removal Tool** (`tools/remove_duplicates.py`, 148 LOC)
  - Automated duplicate character detection
  - Safe removal with --fix flag
  - Dry-run mode for validation
  
- **Dependencies File** (`requirements.txt`)
  - Python 3.11+ requirements
  - fonttools>=4.47.0, PyYAML>=6.0.1
  - pytest, pytest-cov for testing
  - black, ruff for code quality

### Changed
- **Build Performance**: 46% improvement (0.26s → 0.14s build time)
  - Eliminated 15+ dictionary checks per character
  - Processing rate: 1,744 chars/sec
  
- **Code Quality**: Removed all 4 TODO comments
  - Documented CJK character inclusion strategy
  - Clarified design decisions with inline comments
  
- **Character Data**: Removed 45 duplicate definitions from `hanzi.py`
  - Reduced file size by 570 lines (2,651 → 2,081 lines, -21%)
  - Fixed: 人, 工, 智, 同, 動, 改, 作, 授, 權, and 36 more duplicates
  
- **Module Organization**: Better separation of concerns
  - Translations moved from inline to dedicated module
  - Configuration externalized from build script
  - Character lookup centralized in index

### Fixed
- **Duplicate Character Definitions**: Eliminated all 45 duplicates in hanzi.py
  - Previously: Last definition silently overwrote earlier ones
  - Now: Each character has exactly one definition
  
- **Hard-Coded Constants**: Now configurable via YAML
  - Grid size, font metadata, build paths all configurable
  - Supports 8×8, 16×16, 24×24, 32×32 grid sizes

### Documentation
- Created comprehensive code review (CODE-REVIEW-2025-11.md, 53 pages)
- Created CJK font standards research (CJK-FONT-STANDARDS.md, 42 pages)
- Created improvement plan with 3-sprint roadmap (IMPROVEMENT-PLAN-2025-11.md, 95 pages)
- Created executive summary for management (EXECUTIVE-SUMMARY-2025-11.md)

## [1.0.1] - 2025-10 (Pre-Sprint 1)

### Initial State
- Basic 8×8 bitmap font generator
- Manual character definitions in separate modules
- 303 glyphs: 137 Hanzi, 91 Hangul, 27 Hiragana, 27 Katakana, 11 Punctuation
- Build time: ~0.26 seconds
- Output: ~90 KB TrueType font file

---

## Future Roadmap

### Sprint 2: Scale & Quality (Planned)
- Expand to 1,000 most common CJK characters
- Implement 16×16 grid support
- Add comprehensive unit test suite
- Set up CI/CD pipeline with GitHub Actions

### Sprint 3: Advanced Features (Planned)
- Proportional width support (non-monospace)
- Anti-aliasing for smoother glyphs
- Format export: WOFF2, EOT
- Expand to 5,000 characters (GB-2312 coverage)

---

## License

- Code: MIT License
- Font Glyphs: CC BY 4.0
- See LICENSE and LICENSE-CODE files for details
