# Font Generator Modules

This directory contains the **modular font generation system** for ERDA CC-BY CJK.

---

## Architecture

```
generator/
├── build_ccby_cjk_font.py  # Main build script (to be moved here)
├── katakana.py              # Katakana character data
├── hangul.py                # Hangul/Korean Jamo patterns
├── hanzi.py                 # Hanzi/Kanji ideographs
├── punctuation.py           # CJK punctuation marks
└── README.md                # This file
```

---

## Module Overview

### 1. `katakana.py` (✅ Implemented)
**Purpose:** Katakana base characters, small variants, and diacritical marks.

**Data:**
- `KATAKANA_BASE` (50 base characters: ア, イ, ウ, ...)
- `SMALL_KATAKANA` (12 small variants: ァ, ィ, ゥ, ッ, ャ, ュ, ョ, ...)
- `DAKUTEN` (゛ diacritical mark bitmap)
- `HANDAKUTEN` (゜ diacritical mark bitmap)

**Coverage:** Full Japanese Katakana support (base + combinations)

---

### 2. `hangul.py` (✅ Implemented)
**Purpose:** Algorithmic Hangul generation using Jamo (L, V, T) patterns.

**Data:**
- `L_PATTERNS` (19 leading consonants: ㄱ, ㄲ, ㄴ, ...)
- `V_PATTERNS` (21 vowels: ㅏ, ㅐ, ㅑ, ...)
- `T_PATTERNS` (28 trailing consonants including empty: "", ㄱ, ㄲ, ...)

**Functions:**
- `get_hangul_syllable_code(l, v, t)` → Unicode code point
- `decompose_hangul_syllable(code)` → (l_index, v_index, t_index)
- `combine_patterns(l, v, t)` → 8x8 bitmap

**Coverage:** All 11,172 modern Hangul syllables (U+AC00 - U+D7A3)

---

### 3. `hanzi.py` (✅ Implemented)
**Purpose:** Explicitly defined Chinese/Japanese ideographs for license texts.

**Data:**
- `HANZI_KANJI` (107 hand-crafted characters)
  - Basic terms: 本, 作, 品, 用, 再, 人, 工, 知, 智, 能, ...
  - License text: 語, 以, 下, 同, 条, 件, 共, 有, ...

**Coverage:** 
- Traditional Chinese license text (full)
- Japanese license text (full)
- Fallback for undefined CJK characters (U+4E00 - U+9FFF)

---

### 4. `punctuation.py` (✅ Implemented)
**Purpose:** CJK punctuation marks and symbols.

**Data:**
- `PUNCTUATION` (50+ symbols)
  - CJK: 、。・「」『』《》〈〉
  - ASCII: , . : ; ! ? ( ) [ ] { } / \ |
  - Quotes: ' ' " " 
  - Dashes: － — ― ～ … ‥

**Coverage:** Full CJK and ASCII punctuation support

---

## Build Process

### Current State (before modularization)
```python
# build_ccby_cjk_font.py (3300+ lines)
# - All character data inline
# - Monolithic structure
# - Hard to maintain
```

### Future State (after modularization)
```python
# build_ccby_cjk_font.py (~500 lines)
from generator.katakana import KATAKANA_BASE, SMALL_KATAKANA
from generator.hangul import L_PATTERNS, V_PATTERNS, T_PATTERNS, combine_patterns
from generator.hanzi import HANZI_KANJI
from generator.punctuation import PUNCTUATION

# Clean, modular build logic
```

---

## Integration Plan

### Step 1: Module Creation (✅ Done)
- [x] Extract Katakana → `katakana.py`
- [x] Extract Hangul → `hangul.py`
- [x] Extract Hanzi → `hanzi.py`
- [x] Extract Punctuation → `punctuation.py`

### Step 2: Build Script Migration (⏳ Next)
- [ ] Move `build_ccby_cjk_font.py` to `generator/`
- [ ] Import character modules
- [ ] Remove inline data definitions
- [ ] Update paths in scripts

### Step 3: Logging System (⏳ Pending)
- [ ] Add logging to `logs/` directory
- [ ] Track font generation metrics
- [ ] Record character coverage
- [ ] Log build errors

### Step 4: Dataset Integration (⏳ Pending)
- [ ] Use `dataset/*.md` files for testing
- [ ] Generate coverage reports
- [ ] Validate against real license texts

---

## Testing

### Unit Tests (Future)
```bash
# Test individual modules
pytest generator/test_katakana.py
pytest generator/test_hangul.py
pytest generator/test_hanzi.py
pytest generator/test_punctuation.py
```

### Integration Tests
```bash
# Test full font build
python generator/build_ccby_cjk_font.py

# Test coverage
python tests/test_license_coverage.py japanese
python tests/test_license_coverage.py korean
python tests/test_license_coverage.py chinese
```

---

## Design Principles

1. **Modularity:** Each script type has its own module
2. **Maintainability:** Easy to update individual character sets
3. **Testability:** Clear interfaces for unit testing
4. **Documentation:** Inline comments + README
5. **Licensing:** CC BY 4.0 for all modules

---

## License

All modules in this directory are licensed under **CC BY 4.0**.

```
© 2025 ERDA Project
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
```

---

**Last Updated:** 2025-01-17
**Next Step:** Move `build_ccby_cjk_font.py` to this directory
