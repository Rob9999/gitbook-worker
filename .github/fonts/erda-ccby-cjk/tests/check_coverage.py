import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "dataset"
GENERATOR_DIR = ROOT / "generator"

sys.path.insert(0, str(GENERATOR_DIR))

# Import data modules
import generator.hanzi as hanzi_mod
import generator.katakana as kata_mod
import generator.punctuation as punct_mod
import generator.hangul as hangul_mod
import generator.hiragana as hira_mod


def load_dataset_texts(dataset_dir):
    texts = []
    for p in dataset_dir.glob("*.md"):
        texts.append(p.read_text(encoding="utf-8"))
    return "\n".join(texts)


def unique_chars(s):
    return set(c for c in s if not c.isspace())


if __name__ == "__main__":
    text = load_dataset_texts(DATASET_DIR)
    chars = unique_chars(text)
    print(f"Total unique dataset chars: {len(chars)}")

    hanzi_keys = set(hanzi_mod.HANZI_KANJI.keys())
    kata_keys = (
        set(kata_mod.KATAKANA_BASE.keys())
        | set(kata_mod.SMALL_KATAKANA.keys())
        | set(kata_mod.DAKUTEN_COMBOS.keys())
        | set(kata_mod.HANDAKUTEN_COMBOS.keys())
    )
    punct_keys = set(punct_mod.PUNCTUATION.keys())
    hira_keys = set(hira_mod.HIRAGANA.keys())

    missing = {}
    covered = set()

    for ch in sorted(chars):
        code = ord(ch)
        if ch in hanzi_keys:
            covered.add(ch)
            continue
        if ch in kata_keys:
            covered.add(ch)
            continue
        if ch in hira_keys:
            covered.add(ch)
            continue
        if ch in punct_keys:
            covered.add(ch)
            continue
        # Hangul syllable block
        if 0xAC00 <= code <= 0xD7A3:
            covered.add(ch)
            continue
        # ASCII/Latin and digits
        if code < 128:
            covered.add(ch)
            continue
        missing[ch] = f"U+{code:04X}"

    print("\nCovered characters:", len(covered))
    print("\nMissing characters:")
    for ch, cp in missing.items():
        print(f"{ch} {cp}")
    if not missing:
        print("\nNo missing characters found.")
    else:
        print(
            f"\n{len(missing)} missing characters - consider adding bitmap placeholders to hanzi/katakana/punctuation modules or extend algorithmic coverage."
        )
