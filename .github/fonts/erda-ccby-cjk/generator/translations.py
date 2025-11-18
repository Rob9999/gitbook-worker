"""
Translation strings for font build character collection.

This module contains translation strings used to collect required characters
from various languages. These strings ensure that the font covers all characters
needed for displaying license and documentation text in multiple languages.

The translations are connected to ../dataset/ markdown files and serve as
the primary source for determining which characters must be included in the
generated font.

License: MIT (code), CC BY 4.0 (font glyphs)
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TranslationSet:
    """A set of translations for character collection."""

    japanese: str
    korean: str
    chinese_traditional: str
    chinese_simplified: str = ""

    def all_texts(self) -> List[str]:
        """Get all translation texts as a list.

        Returns:
            List of all non-empty translation strings
        """
        texts = [
            self.japanese,
            self.korean,
            self.chinese_traditional,
        ]

        if self.chinese_simplified:
            texts.append(self.chinese_simplified)

        return [t for t in texts if t]

    def all_characters(self) -> set:
        """Get all unique characters from all translations.

        Returns:
            Set of unique characters across all translations
        """
        chars = set()
        for text in self.all_texts():
            chars.update(text)
        return chars


# License and attribution translations
LICENSE_TRANSLATIONS = TranslationSet(
    japanese="""
本作品のあらゆる利用・処理・再処理は、人工知能・機械学習・自動化システムによるものを含め、オープンライセンス CC BY-SA 4.0（表示・同一条件での共有）に従います。これには、派生作品、AIが生成したコンテンツ、リミックス・プロジェクト、および アルゴリズムで変換された形式が明示的に含まれます。改変されていない引用は、別ライセンスのコレクションの一部として掲載できますが、当該コンテンツは引き続き CC BY-SA 4.0 です。
""".strip(),
    korean="""
한국어 (대한민국)
이 저작물의 모든 이용, 처리 또는 재처리는 인공지능, 기계학습, 자동화 시스템을 통한 경우를 포함하여 오픈 라이선스 CC BY-SA 4.0 (저작자 표시, 동일조건변경허락)을 따릅니다. 이는 명시적으로 2차적 저작물, AI 생성 콘텐츠, 리믹스 프로젝트 및 알고리즘으로 변환된 형식을 포함합니다. 변경되지 않은 수록물은 다른 라이선스의 모음집에 포함될 수 있지만, 해당 콘텐츠는 CC BY-SA 4.0으로 유지됩니다.
""".strip(),
    chinese_traditional="""
本作品的任何使用、處理或再處理——包括透過人工智慧、機器學習或自動化系統——皆須遵循開放授權 CC BY-SA 4.0（姓名標示、相同方式分享）。此授權明確涵蓋衍生作品、AI 產生的內容、重混專案及演算法轉換的格式。未經改動的收錄可作為其他授權之集合的一部分，但相關內容仍屬 CC BY-SA 4.0。
""".strip(),
)


# Convenience accessors for backwards compatibility
JAPANESE_TRANSLATION = LICENSE_TRANSLATIONS.japanese
KOREAN_TRANSLATION = LICENSE_TRANSLATIONS.korean
CHINESE_TRADITIONAL_TRANSLATION = LICENSE_TRANSLATIONS.chinese_traditional


def get_all_translation_characters() -> set:
    """Get all unique characters from all translations.

    This is the primary function for collecting characters that must be
    included in the font to properly display all translation strings.

    Returns:
        Set of unique characters across all translations
    """
    return LICENSE_TRANSLATIONS.all_characters()


if __name__ == "__main__":
    # Test translations
    print("Translation Character Analysis")
    print("=" * 70)

    print(f"\n📊 Statistics:")
    print(f"   Japanese:            {len(LICENSE_TRANSLATIONS.japanese)} chars")
    print(f"   Korean:              {len(LICENSE_TRANSLATIONS.korean)} chars")
    print(
        f"   Chinese Traditional: {len(LICENSE_TRANSLATIONS.chinese_traditional)} chars"
    )

    all_chars = get_all_translation_characters()
    print(f"\n   Total unique chars:  {len(all_chars)}")

    # Character type breakdown
    hiragana = sum(1 for c in all_chars if 0x3040 <= ord(c) <= 0x309F)
    katakana = sum(1 for c in all_chars if 0x30A0 <= ord(c) <= 0x30FF)
    hangul = sum(1 for c in all_chars if 0xAC00 <= ord(c) <= 0xD7A3)
    cjk_unified = sum(1 for c in all_chars if 0x4E00 <= ord(c) <= 0x9FFF)

    print(f"\n📝 Character Types:")
    print(f"   Hiragana:       {hiragana}")
    print(f"   Katakana:       {katakana}")
    print(f"   Hangul:         {hangul}")
    print(f"   CJK Unified:    {cjk_unified}")
    print(
        f"   Other:          {len(all_chars) - hiragana - katakana - hangul - cjk_unified}"
    )

    print("\n" + "=" * 70)
