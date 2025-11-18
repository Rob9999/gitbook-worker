# ERDA CJK Font Tests

## Test-Dateien

### `test_chars.py`
Testet ob alle wichtigen japanischen Kanji in der Font enthalten sind.

```bash
python test_chars.py
```

**Output:**
```
Testing Japanese Kanji:
========================================
利 (U+5229): ✓
従 (U+5F93): ✓
...
20/20 characters present
```

### `test_dict.py`
Prüft ob Zeichen im `HANZI_KANJI` Dictionary vorhanden sind.

```bash
python test_dict.py
```

### `debug_chars.py`
Debug-Script um zu prüfen, warum bestimmte Zeichen nicht in der Font erscheinen.

```bash
python debug_chars.py
```

### `check_translation.py`
Prüft welche Zeichen in den Translation-Strings vorhanden sind.

```bash
python check_translation.py
```

### `test-font-version.html`
HTML-Testseite zum visuellen Testen der Font im Browser.

```bash
start test-font-version.html  # Windows
open test-font-version.html   # macOS
xdg-open test-font-version.html  # Linux
```

## Test-Zeichen

Die Tests prüfen folgende wichtige Zeichen:

**Japanisch (日本語):**
- 本作品 (this work)
- 利用 (use)
- 処理 (processing)
- 従います (follow)
- 派生 (derivative)
- 含まれます (include)
- 改変 (modification)
- 引用 (quote)
- 別 (separate)
- 掲載 (publication)
- 載 (load)
- 続き (continue)
- 語 (language)
- 以下 (below)
- 同一 (same)
- 条件 (condition)
- 共有 (share)
- 有 (have)

**Koreanisch (한국어):**
- Alle Hangul-Silben (11,172) werden algorithmisch generiert

**Traditionelles Chinesisch (繁體中文):**
- 100+ wichtigste Hanzi für Lizenztexte

## Neue Tests hinzufügen

Erstelle eine neue `.py` Datei in diesem Verzeichnis:

```python
#!/usr/bin/env python3
"""Test description."""

from fontTools.ttLib import TTFont

def test_your_feature():
    f = TTFont("../erda-ccby-cjk.ttf")
    cmap = f.getBestCmap()
    # Your test logic here
    assert ord('語') in cmap

if __name__ == "__main__":
    test_your_feature()
    print("✓ Test passed")
```
