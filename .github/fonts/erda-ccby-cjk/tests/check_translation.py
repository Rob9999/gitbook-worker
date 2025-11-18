#!/usr/bin/env python3
"""Check if characters are in translation strings."""

JAPANESE_TRANSLATION = """
本作品のあらゆる利用・処理・再処理は、人工知能・機械学習・自動化システムによるものを含め、オープンライセンス CC BY-SA 4.0（表示・同一条件での共有）に従います。これには、派生作品、AIが生成したコンテンツ、リミックス・プロジェクト、および アルゴリズムで変換された形式が明示的に含まれます。改変されていない引用は、別ライセンスのコレクションの一部として掲載できますが、当該コンテンツは引き続き CC BY-SA 4.0 です。
""".strip()

test_chars = ["語", "以", "下"]

print("Checking translation string:")
print("=" * 60)
for c in test_chars:
    in_text = c in JAPANESE_TRANSLATION
    print(f"{c} (U+{ord(c):04X}): {'✓' if in_text else '✗'}")

print(f"\nTotal unique characters: {len(set(JAPANESE_TRANSLATION))}")
