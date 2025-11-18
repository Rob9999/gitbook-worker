# ERDA CJK Font - Verbesserungsplan & Sprint-Roadmap
**Version:** 1.0  
**Datum:** 08. November 2025  
**Planungszeitraum:** November 2025 - Februar 2026  
**Team-Kapazität:** 1 Entwickler @ 40h/Woche

---

## Executive Summary

### 🎯 Ziele

1. **Performance:** Build-Zeit von 0.11s auf 0.03s reduzieren (-73%)
2. **Coverage:** Zeichen-Anzahl von 303 auf 5.000+ erweitern (+1.550%)
3. **Formats:** Zusätzliche Font-Formate (16×16, proportional) unterstützen
4. **Quality:** Code-Qualität durch Tests und CI/CD verbessern
5. **Maintainability:** Architektur refactoren für bessere Wartbarkeit

### 📊 Ressourcen-Übersicht

| Sprint | Dauer | Tasks | Story Points | Priorität |
|--------|-------|-------|--------------|-----------|
| Sprint 1 | 2 Wochen | 8 | 34 | P0 Critical |
| Sprint 2 | 2 Wochen | 10 | 55 | P1 High |
| Sprint 3 | 2 Wochen | 12 | 68 | P2 Medium |
| **TOTAL** | **6 Wochen** | **30** | **157** | - |

---

## Sprint 1: Foundation & Critical Fixes (P0)
**Zeitraum:** Woche 1-2  
**Ziel:** Kritische Bugs fixen, Performance-Basis schaffen

### Sprint-Ziele
- ✅ Code-Duplikate beseitigen
- ✅ Performance-Index-System implementieren
- ✅ Config-System einführen
- ✅ TODOs adressieren

### Tasks

#### Task 1.1: Code-Duplikate in hanzi.py beseitigen 🔴 P0
**Story Points:** 3  
**Aufwand:** 4 Stunden  
**Assignee:** Dev1

**Beschreibung:**
`hanzi.py` enthält mehrere Duplikate (z.B. "人", "工", "智"), die zu unerwartetem Verhalten führen können.

**Akzeptanzkriterien:**
- [ ] Alle Duplikate identifiziert und dokumentiert
- [ ] Script zur automatischen Duplikat-Erkennung erstellt
- [ ] Nur eine Definition pro Zeichen in `hanzi.py`
- [ ] Unit-Test für Duplikat-Erkennung

**Implementierung:**
```python
# tools/check_duplicates.py
from collections import defaultdict
from generator import hanzi

def find_duplicates():
    """Find duplicate character definitions."""
    seen = defaultdict(list)
    
    for i, (char, bitmap) in enumerate(hanzi.HANZI_KANJI.items()):
        seen[char].append(i)
    
    duplicates = {char: indices for char, indices in seen.items() if len(indices) > 1}
    return duplicates

if __name__ == "__main__":
    dups = find_duplicates()
    if dups:
        print(f"❌ Found {len(dups)} duplicates:")
        for char, indices in dups.items():
            print(f"  {char} (U+{ord(char):04X}): {len(indices)} definitions")
        sys.exit(1)
    else:
        print("✅ No duplicates found")
```

**Testing:**
```bash
python tools/check_duplicates.py
```

---

#### Task 1.2: Character-Index-System implementieren 🔴 P0
**Story Points:** 8  
**Aufwand:** 10 Stunden  
**Assignee:** Dev1

**Beschreibung:**
Aktuell werden für jedes Zeichen bis zu 15 Dictionary-Lookups durchgeführt. Ein Pre-Index reduziert dies auf 1 Lookup → ~50% schneller.

**Akzeptanzkriterien:**
- [ ] `CharacterIndex` Klasse implementiert
- [ ] Alle Character-Sources pre-indexed
- [ ] Dakuten-Kombinationen pre-computed
- [ ] Build-Zeit reduziert auf <0.08s
- [ ] Unit-Tests für Index-System

**Implementierung:**
```python
# generator/character_index.py
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CharacterInfo:
    """Character information."""
    bitmap: List[str]
    source: str
    unicode_block: str
    frequency_rank: Optional[int] = None

class CharacterIndex:
    """Fast O(1) lookup index for all character sources."""
    
    def __init__(self):
        self._index: Dict[str, CharacterInfo] = {}
        self._build_time = 0.0
        self._build_index()
    
    def _build_index(self):
        """Build unified character index with pre-computed combinations."""
        import time
        start = time.time()
        
        # Import character modules
        from katakana import KATAKANA_BASE, SMALL_KATAKANA, DAKUTEN, HANDAKUTEN
        from katakana import DAKUTEN_COMBOS, HANDAKUTEN_COMBOS
        from hiragana import HIRAGANA
        from hanzi import HANZI_KANJI
        from punctuation import PUNCTUATION
        
        # Index Katakana base
        for char, bitmap in KATAKANA_BASE.items():
            self._index[char] = CharacterInfo(
                bitmap=bitmap,
                source="katakana",
                unicode_block="Katakana",
            )
        
        # Index Small Katakana
        for char, bitmap in SMALL_KATAKANA.items():
            self._index[char] = CharacterInfo(
                bitmap=bitmap,
                source="katakana-small",
                unicode_block="Katakana",
            )
        
        # Pre-compute Dakuten combinations
        for char, base_char in DAKUTEN_COMBOS.items():
            base = KATAKANA_BASE[base_char]
            merged = self._merge_bitmaps(base, DAKUTEN)
            self._index[char] = CharacterInfo(
                bitmap=merged,
                source="katakana-dakuten",
                unicode_block="Katakana",
            )
        
        # Pre-compute Handakuten combinations
        for char, base_char in HANDAKUTEN_COMBOS.items():
            base = KATAKANA_BASE[base_char]
            merged = self._merge_bitmaps(base, HANDAKUTEN)
            self._index[char] = CharacterInfo(
                bitmap=merged,
                source="katakana-handakuten",
                unicode_block="Katakana",
            )
        
        # Index Hiragana
        for char, bitmap in HIRAGANA.items():
            self._index[char] = CharacterInfo(
                bitmap=bitmap,
                source="hiragana",
                unicode_block="Hiragana",
            )
        
        # Index Hanzi/Kanji
        for char, bitmap in HANZI_KANJI.items():
            self._index[char] = CharacterInfo(
                bitmap=bitmap,
                source="hanzi",
                unicode_block="CJK Unified Ideographs",
            )
        
        # Index Punctuation
        for char, bitmap in PUNCTUATION.items():
            self._index[char] = CharacterInfo(
                bitmap=bitmap,
                source="punctuation",
                unicode_block="CJK Symbols",
            )
        
        self._build_time = time.time() - start
    
    @staticmethod
    def _merge_bitmaps(*bitmaps: List[str]) -> List[str]:
        """Merge multiple bitmaps using OR logic."""
        if not bitmaps:
            return []
        
        width = len(bitmaps[0][0])
        height = len(bitmaps[0])
        grid = [["." for _ in range(width)] for _ in range(height)]
        
        for bitmap in bitmaps:
            for y, row in enumerate(bitmap):
                for x, cell in enumerate(row):
                    if cell == "#":
                        grid[y][x] = "#"
        
        return ["".join(row) for row in grid]
    
    def get(self, char: str) -> Optional[CharacterInfo]:
        """Fast O(1) character lookup."""
        return self._index.get(char)
    
    def contains(self, char: str) -> bool:
        """Check if character is indexed."""
        return char in self._index
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        sources = {}
        for info in self._index.values():
            sources[info.source] = sources.get(info.source, 0) + 1
        
        return {
            "total_chars": len(self._index),
            "build_time": self._build_time,
            "sources": sources,
        }
    
    def __len__(self) -> int:
        return len(self._index)
    
    def __contains__(self, char: str) -> bool:
        return char in self._index
```

**Usage in build_ccby_cjk_font.py:**
```python
# Before: 15+ if-checks per character
for char in REQUIRED_CHARS:
    if char in KATAKANA_BASE:
        add_char(char, KATAKANA_BASE[char], "katakana")
        continue
    if char in SMALL_KATAKANA:
        add_char(char, SMALL_KATAKANA[char], "katakana")
        continue
    # ... 10+ more checks

# After: 1 lookup per character
char_index = CharacterIndex()

for char in REQUIRED_CHARS:
    info = char_index.get(char)
    if info:
        add_char(char, info.bitmap, info.source)
        continue
    
    # Fallback handling...
```

**Performance-Vergleich:**
```python
# Benchmark
import time

# Old method
start = time.time()
for char in REQUIRED_CHARS:
    # 15 if-checks
    ...
old_time = time.time() - start

# New method
start = time.time()
for char in REQUIRED_CHARS:
    info = char_index.get(char)  # O(1)
new_time = time.time() - start

print(f"Old: {old_time:.3f}s")
print(f"New: {new_time:.3f}s")
print(f"Speedup: {old_time/new_time:.1f}x")
```

**Testing:**
```python
# tests/unit/test_character_index.py
import pytest
from generator.character_index import CharacterIndex

def test_character_index_build():
    index = CharacterIndex()
    assert len(index) > 200
    assert index.get_stats()["total_chars"] > 200

def test_character_lookup():
    index = CharacterIndex()
    
    # Test Katakana
    info = index.get("ア")
    assert info is not None
    assert info.source == "katakana"
    assert len(info.bitmap) == 8
    
    # Test Dakuten pre-computed
    info = index.get("ガ")
    assert info is not None
    assert info.source == "katakana-dakuten"

def test_character_not_found():
    index = CharacterIndex()
    info = index.get("💩")  # Emoji not in index
    assert info is None

def test_index_performance():
    """Index build should be fast (<10ms)."""
    import time
    start = time.time()
    index = CharacterIndex()
    elapsed = time.time() - start
    assert elapsed < 0.01  # Under 10ms
```

---

#### Task 1.3: Config-System implementieren 🟡 P1
**Story Points:** 5  
**Aufwand:** 6 Stunden  
**Assignee:** Dev1

**Beschreibung:**
Hardcoded Konstanten durch flexibles Config-System ersetzen.

**Akzeptanzkriterien:**
- [ ] `FontConfig` dataclass implementiert
- [ ] Alle Konstanten in Config ausgelagert
- [ ] Config per YAML/JSON ladbar
- [ ] Default-Config vorhanden
- [ ] Config-Validierung implementiert

**Implementierung:**
```python
# generator/config.py
from dataclasses import dataclass, field
from typing import Literal, Optional
import yaml
from pathlib import Path

@dataclass
class FontConfig:
    """Font generation configuration."""
    
    # Grid settings
    grid_size: Literal[8, 12, 16, 24] = 16
    monospace: bool = True
    em_size: int = 1000
    
    # Character sets
    include_hiragana_full: bool = True
    include_katakana_full: bool = True
    hanzi_count: int = 500  # Top N most frequent
    hangul_count: int = 200  # Top N most frequent
    include_ascii: bool = True
    include_punctuation_full: bool = True
    
    # Performance
    use_character_index: bool = True
    use_glyph_cache: bool = False
    parallel_generation: bool = False
    
    # Output
    output_dir: str = "../true-type"
    font_family: str = "ERDA CC-BY CJK"
    font_name: str = "erda-ccby-cjk"
    version: str = "1.0"
    
    # Font metadata
    vendor_id: str = "ERDA"
    copyright: str = "Copyright 2025 ERDA Project"
    license: str = "CC BY 4.0"
    license_url: str = "https://creativecommons.org/licenses/by/4.0/"
    
    # Build options
    verbose: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    @classmethod
    def from_yaml(cls, path: str) -> "FontConfig":
        """Load configuration from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_json(cls, path: str) -> "FontConfig":
        """Load configuration from JSON file."""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    def save_yaml(self, path: str):
        """Save configuration to YAML file."""
        import yaml
        from dataclasses import asdict
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)
    
    def validate(self) -> list[str]:
        """Validate configuration."""
        errors = []
        
        if self.grid_size not in [8, 12, 16, 24]:
            errors.append(f"Invalid grid_size: {self.grid_size}")
        
        if self.em_size < 100 or self.em_size > 10000:
            errors.append(f"Invalid em_size: {self.em_size}")
        
        if self.hanzi_count < 0 or self.hanzi_count > 20000:
            errors.append(f"Invalid hanzi_count: {self.hanzi_count}")
        
        if not Path(self.output_dir).parent.exists():
            errors.append(f"Output directory parent does not exist: {self.output_dir}")
        
        return errors
```

**Config-Dateien:**
```yaml
# config/default.yaml
grid_size: 8
monospace: true
em_size: 1000

include_hiragana_full: true
include_katakana_full: true
hanzi_count: 500
hangul_count: 200
include_ascii: true
include_punctuation_full: true

use_character_index: true
use_glyph_cache: false
parallel_generation: false

output_dir: "../true-type"
font_family: "ERDA CC-BY CJK"
font_name: "erda-ccby-cjk"
version: "1.0"

verbose: false
log_level: "INFO"
```

```yaml
# config/high-quality.yaml
grid_size: 16  # Higher resolution
monospace: false  # Proportional
em_size: 1000

include_hiragana_full: true
include_katakana_full: true
hanzi_count: 5000  # More characters
hangul_count: 1000
include_ascii: true
include_punctuation_full: true

use_character_index: true
use_glyph_cache: true  # Enable cache
parallel_generation: true  # Enable parallel

output_dir: "../true-type"
font_family: "ERDA CC-BY CJK HQ"
font_name: "erda-ccby-cjk-hq"
version: "1.0"

verbose: true
log_level: "DEBUG"
```

**Usage:**
```python
# generator/build_ccby_cjk_font.py
from config import FontConfig

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    
    # Load config
    config = FontConfig.from_yaml(args.config)
    
    # Validate
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    # Build with config
    builder = FontBuilder(config)
    builder.build()
```

---

#### Task 1.4: TODOs adressieren 🟡 P1
**Story Points:** 2  
**Aufwand:** 2 Stunden  
**Assignee:** Dev1

**Beschreibung:**
4 offene TODOs im Code-Base adressieren.

**TODO 1: Translation Strings auslagern**
```python
# Neu: generator/translations.py
"""License text translations for character requirements."""

TRANSLATIONS = {
    "japanese": """
本作品のあらゆる利用・処理・再処理は、人工知能・機械学習・自動化システムによるものを含め、オープンライセンス CC BY-SA 4.0（表示・同一条件での共有）に従います。これには、派生作品、AIが生成したコンテンツ、リミックス・プロジェクト、および アルゴリズムで変換された形式が明示的に含まれます。改変されていない引用は、別ライセンスのコレクションの一部として掲載できますが、当該コンテンツは引き続き CC BY-SA 4.0 です。
    """.strip(),
    
    "korean": """
한국어 (대한민국)
이 저작물의 모든 이용, 처리 또는 재처리는 인공지능, 기계학습, 자동화 시스템을 통한 경우를 포함하여 오픈 라이선스 CC BY-SA 4.0 (저작자 표시, 동일조건변경허락)을 따릅니다. 이는 명시적으로 2차적 저작물, AI 생성 콘텐츠, 리믹스 프로젝트 및 알고리즘으로 변환된 형식을 포함합니다. 변경되지 않은 수록물은 다른 라이선스의 모음집에 포함될 수 있지만, 해당 콘텐츠는 CC BY-SA 4.0으로 유지됩니다.
    """.strip(),
    
    "chinese_traditional": """
本作品的任何使用、處理或再處理——包括透過人工智慧、機器學習或自動化系統——皆須遵循開放授權 CC BY-SA 4.0（姓名標示、相同方式分享）。此授權明確涵蓋衍生作品、AI 產生的內容、重混專案及演算法轉換的格式。未經改動的收錄可作為其他授權之集合的一部分，但相關內容仍屬 CC BY-SA 4.0。
    """.strip(),
}

def get_all_translations() -> list[str]:
    """Get all translation strings."""
    return list(TRANSLATIONS.values())

def get_translation(language: str) -> str:
    """Get specific translation."""
    return TRANSLATIONS.get(language, "")
```

**TODO 2: Dataset-Verknüpfung dokumentieren**
```python
# Neu: generator/dataset_loader.py
"""Load character requirements from dataset markdown files."""

from pathlib import Path
from typing import Set

def load_dataset_chars(dataset_dir: str = "../dataset") -> Set[str]:
    """
    Load CJK characters from dataset markdown files.
    
    These files contain the actual license text translations that need
    to be rendered in the final font. By scanning these files, we ensure
    the font includes all required characters.
    
    Args:
        dataset_dir: Directory containing dataset markdown files
    
    Returns:
        Set of unique CJK characters found in dataset
    """
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        return set()
    
    all_chars = set()
    
    for md_file in dataset_path.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        
        # Extract CJK characters
        for char in text:
            code = ord(char)
            if (
                0x4E00 <= code <= 0x9FFF  # Hanzi
                or 0x3040 <= code <= 0x309F  # Hiragana
                or 0x30A0 <= code <= 0x30FF  # Katakana
                or 0xAC00 <= code <= 0xD7AF  # Hangul
                or 0xFF00 <= code <= 0xFFEF  # Fullwidth
            ):
                all_chars.add(char)
    
    return all_chars
```

**TODO 3 & 4: Bereits implementiert (können entfernt werden)**

---

#### Task 1.5: Performance-Benchmarking-Suite 🟢 P2
**Story Points:** 3  
**Aufwand:** 4 Stunden  
**Assignee:** Dev1

**Beschreibung:**
Automatisierte Performance-Tests für Regression-Detection.

**Implementierung:**
```python
# tests/performance/benchmark.py
import time
import statistics
from typing import Callable, List
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    """Benchmark result."""
    name: str
    mean: float
    median: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int

def benchmark(
    func: Callable,
    iterations: int = 10,
    warmup: int = 2
) -> BenchmarkResult:
    """Benchmark a function."""
    # Warmup
    for _ in range(warmup):
        func()
    
    # Measure
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return BenchmarkResult(
        name=func.__name__,
        mean=statistics.mean(times),
        median=statistics.median(times),
        std_dev=statistics.stdev(times) if len(times) > 1 else 0.0,
        min_time=min(times),
        max_time=max(times),
        iterations=iterations,
    )

def print_benchmark(result: BenchmarkResult):
    """Print benchmark result."""
    print(f"\n{result.name}:")
    print(f"  Mean:   {result.mean*1000:.2f}ms")
    print(f"  Median: {result.median*1000:.2f}ms")
    print(f"  StdDev: {result.std_dev*1000:.2f}ms")
    print(f"  Min:    {result.min_time*1000:.2f}ms")
    print(f"  Max:    {result.max_time*1000:.2f}ms")
    print(f"  Iterations: {result.iterations}")

if __name__ == "__main__":
    from generator.build_ccby_cjk_font import build_font
    from generator.character_index import CharacterIndex
    
    # Benchmark full build
    result = benchmark(
        lambda: build_font("../build/benchmark.ttf"),
        iterations=10
    )
    print_benchmark(result)
    
    # Benchmark character index build
    result = benchmark(
        lambda: CharacterIndex(),
        iterations=100
    )
    print_benchmark(result)
```

---

#### Task 1.6: CI/CD Pipeline einrichten 🟢 P2
**Story Points:** 5  
**Aufwand:** 6 Stunden  
**Assignee:** Dev1

**Implementierung:**
```yaml
# .github/workflows/font-ci.yml
name: Font Build CI

on:
  push:
    branches: [main, release_candidate]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install linters
        run: |
          pip install black flake8 mypy
      
      - name: Run black
        run: black --check .github/fonts/erda-ccby-cjk/
      
      - name: Run flake8
        run: flake8 .github/fonts/erda-ccby-cjk/ --max-line-length=100
      
      - name: Run mypy
        run: mypy .github/fonts/erda-ccby-cjk/generator/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r .github/fonts/erda-ccby-cjk/requirements.txt
          pip install pytest pytest-cov
      
      - name: Check for duplicates
        run: |
          cd .github/fonts/erda-ccby-cjk
          python tests/check_hanzi_dups.py
      
      - name: Check coverage
        run: |
          cd .github/fonts/erda-ccby-cjk
          python tests/check_coverage.py
      
      - name: Run unit tests
        run: |
          cd .github/fonts/erda-ccby-cjk
          pytest tests/ -v --cov=generator --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: .github/fonts/erda-ccby-cjk/coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r .github/fonts/erda-ccby-cjk/requirements.txt
      
      - name: Build font (8x8)
        run: |
          cd .github/fonts/erda-ccby-cjk/generator
          python build_ccby_cjk_font.py --config config/default.yaml
      
      - name: Verify font
        run: |
          cd .github/fonts/erda-ccby-cjk
          test -f true-type/erda-ccby-cjk.ttf
          size=$(stat -f%z true-type/erda-ccby-cjk.ttf 2>/dev/null || stat -c%s true-type/erda-ccby-cjk.ttf)
          echo "Font size: $size bytes"
          test $size -gt 50000  # At least 50KB
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: font-8x8
          path: .github/fonts/erda-ccby-cjk/true-type/*.ttf
          retention-days: 30

  benchmark:
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r .github/fonts/erda-ccby-cjk/requirements.txt
      
      - name: Run benchmarks
        run: |
          cd .github/fonts/erda-ccby-cjk
          python tests/performance/benchmark.py > benchmark-results.txt
      
      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: .github/fonts/erda-ccby-cjk/benchmark-results.txt
```

---

#### Task 1.7: Unit-Test-Grundgerüst 🟢 P2
**Story Points:** 5  
**Aufwand:** 6 Stunden  
**Assignee:** Dev1

**Implementierung:**
```python
# tests/unit/test_bitmap_operations.py
import pytest
from generator.build_ccby_cjk_font import _merge_bitmaps, _glyph_from_bitmap

def test_merge_bitmaps_simple():
    base = ["#.......", "........"]
    overlay = ["....#...", "........"]
    result = _merge_bitmaps(base, overlay)
    assert result == ["#...#...", "........"]

def test_merge_bitmaps_overlap():
    base = ["####....", "........"]
    overlay = ["..####..", "........"]
    result = _merge_bitmaps(base, overlay)
    assert result == ["######..", "........"]

def test_glyph_from_bitmap():
    bitmap = ["########"] * 8
    glyph, width = _glyph_from_bitmap(bitmap)
    assert glyph is not None
    assert width == 1000  # (8 + 2) * 100

# tests/unit/test_hangul.py
from generator.hangul import _bitmap_for_hangul

def test_hangul_first_syllable():
    char = "가"  # U+AC00
    bitmap = _bitmap_for_hangul(char)
    assert len(bitmap) == 8
    assert all(len(row) == 8 for row in bitmap)

def test_hangul_last_syllable():
    char = "힣"  # U+D7A3
    bitmap = _bitmap_for_hangul(char)
    assert len(bitmap) == 8

def test_hangul_out_of_range():
    with pytest.raises(ValueError):
        _bitmap_for_hangul("A")  # Not Hangul

# tests/unit/test_character_index.py
from generator.character_index import CharacterIndex

def test_index_build():
    index = CharacterIndex()
    assert len(index) > 200

def test_index_contains():
    index = CharacterIndex()
    assert "ア" in index
    assert "💩" not in index

def test_index_get():
    index = CharacterIndex()
    info = index.get("ア")
    assert info is not None
    assert info.source == "katakana"

# tests/integration/test_font_build.py
import pytest
from pathlib import Path
from generator.build_ccby_cjk_font import build_font

@pytest.fixture
def temp_output(tmp_path):
    return str(tmp_path / "test.ttf")

def test_font_build(temp_output):
    result = build_font(temp_output)
    assert Path(result).exists()
    assert Path(result).stat().st_size > 50000

def test_font_metadata(temp_output):
    from fontTools import ttLib
    build_font(temp_output)
    font = ttLib.TTFont(temp_output)
    
    # Check name table
    name_table = font['name']
    family_name = name_table.getDebugName(1)
    assert "ERDA" in family_name
    
    # Check glyph count
    assert len(font.getGlyphOrder()) > 300
```

---

#### Task 1.8: Dokumentation aktualisieren 📝
**Story Points:** 3  
**Aufwand:** 3 Stunden  
**Assignee:** Dev1

**Akzeptanzkriterien:**
- [ ] README.md aktualisiert mit neuen Features
- [ ] API-Dokumentation für neue Module
- [ ] Performance-Benchmarks dokumentiert
- [ ] Config-Beispiele hinzugefügt

---

### Sprint 1 Summary

**Total Story Points:** 34  
**Total Hours:** ~41 Stunden (ca. 1 Woche @ 1 Dev)  
**Deliverables:**
- ✅ Code-Duplikate beseitigt
- ✅ Character-Index-System (50% schneller)
- ✅ Config-System implementiert
- ✅ CI/CD Pipeline
- ✅ Unit-Test-Grundgerüst
- ✅ Performance-Benchmarking

**Expected Performance:** Build-Zeit: 0.11s → 0.06s (-45%)

---

## Sprint 2: Format-Erweiterung & Character-Coverage (P1)
**Zeitraum:** Woche 3-4  
**Ziel:** Zusätzliche Font-Formate, erweiterte Zeichen-Coverage

### Sprint-Ziele
- ✅ 16×16 Grid-Format implementieren
- ✅ Top 1.000 Hanzi hinzufügen
- ✅ Vollständige Hiragana/Katakana
- ✅ Proportional-Font-Grundlage

### Tasks

#### Task 2.1: 16×16 Grid-Format implementieren 🔴 P0
**Story Points:** 13  
**Aufwand:** 16 Stunden  
**Assignee:** Dev1

**Beschreibung:**
16×16 Pixel-Grid für bessere Lesbarkeit und mehr Details.

**Akzeptanzkriterien:**
- [ ] Grid-Size ist konfigurierbar (8, 12, 16, 24)
- [ ] Bestehende 8×8 Bitmaps werden hochskaliert
- [ ] Neue 16×16 Bitmaps für wichtige Zeichen
- [ ] Automatische Skalierungs-Pipeline
- [ ] Separate Font-Datei: `erda-ccby-cjk-16.ttf`

**Implementierung:**
```python
# generator/bitmap_scaler.py
from typing import List

class BitmapScaler:
    """Scale bitmaps to different grid sizes."""
    
    @staticmethod
    def scale_2x(bitmap: List[str]) -> List[str]:
        """Scale 8x8 bitmap to 16x16."""
        scaled = []
        for row in bitmap:
            scaled_row = ""
            for char in row:
                scaled_row += char * 2  # Double horizontally
            scaled.append(scaled_row)
            scaled.append(scaled_row)  # Double vertically
        return scaled
    
    @staticmethod
    def scale_3x(bitmap: List[str]) -> List[str]:
        """Scale 8x8 bitmap to 24x24."""
        scaled = []
        for row in bitmap:
            scaled_row = ""
            for char in row:
                scaled_row += char * 3
            for _ in range(3):
                scaled.append(scaled_row)
        return scaled
    
    @staticmethod
    def scale_nearest_neighbor(
        bitmap: List[str],
        target_size: int
    ) -> List[str]:
        """Scale to arbitrary size using nearest neighbor."""
        source_size = len(bitmap)
        scale_factor = target_size / source_size
        
        scaled = []
        for y in range(target_size):
            row = ""
            source_y = int(y / scale_factor)
            for x in range(target_size):
                source_x = int(x / scale_factor)
                row += bitmap[source_y][source_x]
            scaled.append(row)
        
        return scaled

# Usage in build script
from bitmap_scaler import BitmapScaler

def _glyph_from_bitmap_scaled(
    bitmap: List[str],
    grid_size: int = 8
) -> Tuple[object, int]:
    """Generate glyph with configurable grid size."""
    scaler = BitmapScaler()
    
    # Scale if needed
    if grid_size == 16 and len(bitmap) == 8:
        bitmap = scaler.scale_2x(bitmap)
    elif grid_size == 24 and len(bitmap) == 8:
        bitmap = scaler.scale_3x(bitmap)
    
    # Generate glyph
    pen = TTGlyphPen(None)
    rows = len(bitmap)
    cols = len(bitmap[0]) if rows else 0
    
    # Adjust cell size based on grid
    cell_size = EM // (grid_size + 2)
    margin = cell_size
    
    for row_index, row in enumerate(bitmap):
        for col_index, bit in enumerate(row):
            if bit != "#":
                continue
            x = margin + col_index * cell_size
            y = margin + (rows - 1 - row_index) * cell_size
            _draw_rect(pen, x, y, cell_size, cell_size)
    
    glyph = pen.glyph()
    width = (cols + 2) * cell_size
    return glyph, width
```

**High-Quality 16×16 Bitmaps (Beispiele):**
```python
# generator/hanzi_16x16.py
"""High-quality 16×16 Hanzi bitmaps."""

HANZI_16X16 = {
    "本": [  # book/origin - 16×16
        "......####......",
        ".....######.....",
        "................",
        "################",
        "................",
        "......####......",
        "......####......",
        "################",
        "................",
        ".....######.....",
        "....########....",
        "...##....##.....",
        "..##......##....",
        ".##........##...",
        "##..........##..",
        "................",
    ],
    # ... weitere High-Quality-Zeichen
}
```

---

#### Task 2.2: Top 1.000 Hanzi hinzufügen 🟡 P1
**Story Points:** 21  
**Aufwand:** 24 Stunden (aufgeteilt über mehrere Tage)  
**Assignee:** Dev1 + Community

**Beschreibung:**
Erweitere Hanzi-Coverage von 137 auf 1.000+ häufigste Zeichen.

**Strategie:**
1. Frequency-Liste verwenden (HSK 1-6)
2. Community-Sourcing für Bitmap-Design
3. Automatische Template-Generierung
4. Review-Prozess

**Akzeptanzkriterien:**
- [ ] Liste der Top 1.000 Hanzi erstellt
- [ ] Mindestens 500 neue Hanzi-Bitmaps (8×8)
- [ ] Qualitäts-Check für alle Bitmaps
- [ ] Dokumentation der Zeichen-Coverage

**Implementierung:**
```python
# tools/generate_hanzi_frequency_list.py
"""Generate frequency-based Hanzi list for font coverage."""

# HSK Levels (Chinese Proficiency Test)
HSK_LISTS = {
    "HSK1": 150,   # Beginner
    "HSK2": 300,   # Elementary
    "HSK3": 600,   # Intermediate
    "HSK4": 1200,  # Upper Intermediate
    "HSK5": 2500,  # Advanced
    "HSK6": 5000,  # Mastery
}

# Jun Da's Modern Chinese Character Frequency List
# http://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO
FREQUENCY_LIST = [
    # Top 1000 most frequent characters
    "的", "一", "是", "在", "不", "了", "有", "和", "人", "这",
    # ... (load from data file)
]

def get_top_n_hanzi(n: int = 1000) -> list[str]:
    """Get top N most frequent Hanzi."""
    return FREQUENCY_LIST[:n]

def get_hsk_level_chars(level: int) -> list[str]:
    """Get characters for specific HSK level."""
    # Load from HSK database
    ...
```

**Bitmap-Template-Generator:**
```python
# tools/generate_bitmap_templates.py
"""Generate 8x8 bitmap templates for new characters."""

def generate_template(char: str, hint: str = "") -> str:
    """Generate template for character bitmap."""
    return f'''
    "{char}": [  # {hint}
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
        "........",
    ],
'''

# Generate templates for missing characters
missing_chars = get_top_n_hanzi(1000)
existing_chars = set(HANZI_KANJI.keys())

for char in missing_chars:
    if char not in existing_chars:
        hint = get_character_meaning(char)  # From Unicode database
        print(generate_template(char, hint))
```

---

#### Task 2.3: Vollständige Hiragana (93 Zeichen) 🟡 P1
**Story Points:** 5  
**Aufwand:** 6 Stunden  
**Assignee:** Dev1

**Aktuell:** 27 Hiragana  
**Ziel:** 93 Hiragana (alle modernen Varianten)

**Fehlende Zeichen:**
```
Kleine Kana: ぁ ぃ ぅ ぇ ぉ ゃ ゅ ょ ゎ
Dakuten: が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど
Handakuten: ぱ ぴ ぷ ぺ ぽ
Kombinationen: きゃ きゅ きょ など
Obsolete: ゐ ゑ ゔ
```

**Implementierung:**
```python
# generator/hiragana_extended.py
"""Extended Hiragana coverage (93 characters)."""

# Small Hiragana
SMALL_HIRAGANA = {
    "ぁ": [  # small a
        "........",
        "...#....",
        "..###...",
        ".#...#..",
        "..####..",
        "........",
        "........",
        "........",
    ],
    # ... weitere
}

# Dakuten Hiragana (pre-computed)
DAKUTEN_HIRAGANA = {
    "が": _merge_bitmaps(HIRAGANA["か"], DAKUTEN),
    "ぎ": _merge_bitmaps(HIRAGANA["き"], DAKUTEN),
    # ... weitere
}

# Combined export
HIRAGANA_ALL = {
    **HIRAGANA,
    **SMALL_HIRAGANA,
    **DAKUTEN_HIRAGANA,
    **HANDAKUTEN_HIRAGANA,
}
```

---

#### Task 2.4: Vollständige Katakana (96 Zeichen) 🟡 P1
**Story Points:** 5  
**Aufwand:** 6 Stunden  
**Assignee:** Dev1

Analog zu Hiragana.

---

#### Task 2.5: Proportional-Font-Grundlage 🟢 P2
**Story Points:** 8  
**Aufwand:** 10 Stunden  
**Assignee:** Dev1

**Beschreibung:**
Basis für proportionale Fonts (variable Breiten).

**Implementierung:**
```python
# generator/proportional.py
"""Proportional font width calculations."""

class ProportionalWidths:
    """Calculate proportional widths for characters."""
    
    # Width categories (relative to EM size)
    NARROW = 0.4   # Punctuation, i, l, etc.
    NORMAL = 0.6   # a-z, 0-9
    WIDE = 0.8     # m, w, M, W
    CJK = 1.0      # CJK characters (square)
    
    @classmethod
    def get_width(cls, char: str, em_size: int = 1000) -> int:
        """Get proportional width for character."""
        code = ord(char)
        
        # CJK characters: always square
        if (
            0x4E00 <= code <= 0x9FFF or
            0x3040 <= code <= 0x30FF or
            0xAC00 <= code <= 0xD7AF
        ):
            return em_size
        
        # ASCII uppercase wide
        if char in "MWQG":
            return int(em_size * cls.WIDE)
        
        # ASCII narrow
        if char in "iljI1.,;:!'\"":
            return int(em_size * cls.NARROW)
        
        # Default
        return int(em_size * cls.NORMAL)
```

---

### Sprint 2 Summary

**Total Story Points:** 55  
**Total Hours:** ~68 Stunden (ca. 1.7 Wochen @ 1 Dev)  
**Deliverables:**
- ✅ 16×16 Font-Format
- ✅ 500+ neue Hanzi
- ✅ Vollständige Hiragana/Katakana
- ✅ Proportional-Font-Basis

**Expected Coverage:** 303 → 1.200+ Glyphen (+296%)

---

## Sprint 3: Advanced Features & Polish (P2)
**Zeitraum:** Woche 5-6  
**Ziel:** Advanced Features, Optimierung, Dokumentation

### Sprint-Ziele
- ✅ Glyph-Cache-System
- ✅ Parallel-Generierung
- ✅ Font-Hinting
- ✅ Umfassende Dokumentation

### Tasks

#### Task 3.1: Glyph-Cache-System 🟢 P2
**Story Points:** 8  
**Aufwand:** 10 Stunden

**Implementierung:**
```python
# generator/glyph_cache.py
import pickle
from pathlib import Path
from typing import Dict, Tuple, Optional
from hashlib import sha256

class GlyphCache:
    """Persistent cache for generated glyphs."""
    
    def __init__(self, cache_dir: str = "../build/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "glyph_cache.pkl"
        self._cache: Dict[str, Tuple] = {}
        self._dirty = False
        self._load()
    
    def _compute_key(self, char: str, grid_size: int) -> str:
        """Compute cache key."""
        return f"{char}:{grid_size}"
    
    def get(self, char: str, grid_size: int) -> Optional[Tuple]:
        """Get cached glyph."""
        key = self._compute_key(char, grid_size)
        return self._cache.get(key)
    
    def set(self, char: str, grid_size: int, glyph: object, width: int):
        """Cache glyph."""
        key = self._compute_key(char, grid_size)
        self._cache[key] = (glyph, width)
        self._dirty = True
    
    def save(self):
        """Persist cache."""
        if self._dirty:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self._cache, f)
            self._dirty = False
    
    def _load(self):
        """Load cache."""
        if self.cache_file.exists():
            with open(self.cache_file, 'rb') as f:
                self._cache = pickle.load(f)
    
    def clear(self):
        """Clear cache."""
        self._cache = {}
        self._dirty = True
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
```

---

#### Task 3.2: Parallel-Glyph-Generierung 🟢 P2
**Story Points:** 8  
**Aufwand:** 10 Stunden

**Implementierung:**
```python
# generator/parallel_builder.py
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple
import multiprocessing

def generate_glyph_worker(args: Tuple[str, List[str]]) -> Tuple[str, object, int]:
    """Worker function for parallel glyph generation."""
    char, bitmap = args
    glyph, width = _glyph_from_bitmap(bitmap)
    return char, glyph, width

class ParallelFontBuilder:
    """Build fonts with parallel glyph generation."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
    
    def generate_glyphs_parallel(
        self,
        char_bitmap_pairs: List[Tuple[str, List[str]]]
    ) -> Dict[str, Tuple[object, int]]:
        """Generate glyphs in parallel."""
        results = {}
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(generate_glyph_worker, pair): pair[0]
                for pair in char_bitmap_pairs
            }
            
            for future in as_completed(futures):
                char, glyph, width = future.result()
                results[char] = (glyph, width)
        
        return results
```

---

#### Task 3.3: Font-Hinting hinzufügen 🟢 P2
**Story Points:** 13  
**Aufwand:** 16 Stunden

**Implementierung:**
```python
# generator/font_hinting.py
"""TrueType hinting for better rendering at small sizes."""

def setup_hinting(fb: FontBuilder, em_size: int = 1000):
    """Add basic TrueType hinting."""
    
    # GASP table (grid-fitting and anti-aliasing)
    # Controls how font is rendered at different sizes
    fb.setupGasp({
        7: 0,     # < 8ppem: no hinting, no smoothing
        8: 2,     # 8-15ppem: grid-fit
        16: 7,    # 16-65535ppem: grid-fit + smoothing
        65535: 7,
    })
    
    # CVT table (Control Value Table)
    # Stores important measurements
    cvt = [
        em_size // 8,   # Thin stroke
        em_size // 4,   # Medium stroke
        em_size // 2,   # Thick stroke
    ]
    fb.setupCvt(cvt)
    
    # Prep table (Font Program)
    # Instructions executed once when font is loaded
    prep = [
        ("PUSHB", [0]),  # Push default values
        ("SRP0", []),    # Set reference point
    ]
    fb.setupPrep(prep)
```

---

#### Task 3.4-3.12: Weitere Tasks
- CJK Compatibility Characters
- Fullwidth Latin/ASCII
- Emoji-Support (optional)
- Advanced Testing
- Performance-Profiling
- Lokalisierte Dokumentation
- Font-Demo-Website
- Package für PyPI
- Contributor-Guide

---

## KPIs & Success Metrics

### Performance

| Metrik | Baseline | Sprint 1 | Sprint 2 | Sprint 3 | Ziel |
|--------|----------|----------|----------|----------|------|
| Build-Zeit (8×8) | 0.11s | 0.06s | 0.05s | 0.03s | <0.05s |
| Build-Zeit (16×16) | N/A | N/A | 0.12s | 0.08s | <0.10s |
| Cache-Hit-Rate | 0% | 0% | 0% | 80%+ | >70% |

### Coverage

| Metrik | Baseline | Sprint 1 | Sprint 2 | Sprint 3 | Ziel |
|--------|----------|----------|----------|----------|------|
| Total Glyphen | 303 | 303 | 1.200 | 2.000 | 1.000+ |
| Hanzi | 137 | 137 | 637 | 1.137 | 500+ |
| Hiragana | 27 | 27 | 93 | 93 | 93 |
| Katakana | 27 | 27 | 96 | 96 | 96 |
| Hangul | 91 | 91 | 291 | 500+ | 200+ |

### Quality

| Metrik | Baseline | Ziel |
|--------|----------|------|
| Test-Coverage | 0% | 80%+ |
| Code-Duplikate | 8 | 0 |
| TODOs | 4 | 0 |
| CI/CD | ❌ | ✅ |
| Dokumentation | 70% | 95%+ |

---

## Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Character-Design zu zeitaufwändig | Hoch | Mittel | Community-Sourcing, Templates |
| Performance-Ziel nicht erreicht | Mittel | Mittel | Profiling, iterative Optimierung |
| 16×16 Bitmap-Qualität unzureichend | Mittel | Niedrig | High-Quality-Samples, Review |
| CI/CD-Setup-Probleme | Niedrig | Niedrig | Erfahrene DevOps-Unterstützung |

---

## Resource-Allokation

### Team
- **Dev1 (Lead):** 100% (40h/Woche)
- **Community:** Best-effort (Bitmap-Design)

### Infrastruktur
- GitHub Actions (CI/CD)
- PyPI (Package-Publishing)
- GitHub Pages (Dokumentation)

---

## Deliverables-Übersicht

### Sprint 1 (Woche 1-2)
✅ Code-Duplikate beseitigt  
✅ Character-Index-System  
✅ Config-System  
✅ CI/CD Pipeline  
✅ Unit-Tests (Basic)  
✅ Performance-Benchmarks

### Sprint 2 (Woche 3-4)
✅ 16×16 Font-Format  
✅ Top 500+ Hanzi  
✅ Vollständige Hiragana/Katakana  
✅ Proportional-Font-Grundlage  
✅ Extended Character-Index

### Sprint 3 (Woche 5-6)
✅ Glyph-Cache-System  
✅ Parallel-Generierung  
✅ Font-Hinting  
✅ Umfassende Dokumentation  
✅ Demo-Website  
✅ PyPI-Package

---

## Next Steps (Immediate)

### Diese Woche
1. **Review akzeptieren** dieses Plans
2. **Sprint 1 Task 1.1 starten**: Code-Duplikate entfernen
3. **Tools einrichten**: pytest, black, mypy
4. **Repository vorbereiten**: Branch-Strategy, Issues

### Nächste Woche
1. **Sprint 1 Tasks 1.2-1.4** abschließen
2. **CI/CD Pipeline testen**
3. **Performance-Baseline messen**

---

## Anhang: Character-Listen

### A.1: Top 100 Hanzi (Frequency-Based)
```
的 一 是 在 不 了 有 和 人 这
中 大 为 上 个 国 我 以 要 他
时 来 用 们 生 到 作 地 于 出
就 分 对 成 会 可 主 发 年 动
同 工 也 能 下 过 子 说 产 种
面 而 方 后 多 定 行 学 法 所
民 得 经 十 三 之 进 着 等 部
度 家 电 力 里 如 水 化 高 自
二 理 起 小 物 现 实 加 量 都
两 体 制 机 当 使 点 从 业 本
```

### A.2: HSK Level Distribution
```
HSK 1 (150 chars): 基础汉字
HSK 2 (300 chars): +150
HSK 3 (600 chars): +300
HSK 4 (1200 chars): +600
HSK 5 (2500 chars): +1300
HSK 6 (5000 chars): +2500
```

---

**Dokument-Status:** ✅ Ready for Review  
**Letzte Aktualisierung:** 08. November 2025  
**Verantwortlich:** AI Code Analysis Team
