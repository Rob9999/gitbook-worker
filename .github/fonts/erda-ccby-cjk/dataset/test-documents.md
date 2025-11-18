# Test Documents Dataset

This file contains all CJK characters from actual test documents that need to be supported by the ERDA CC-BY CJK font.

**Purpose:** Ensure font coverage for all characters used in integration tests and example documents.

## Source: scenario-3-single-file (complex-doc_with-special&chars@2024!.md)

### Chinese Section (中文)
这是一个测试文档，用于验证中文字符的正确显示。中华人民共和国的首都是北京。

人工智能 (Artificial Intelligence) - 机器学习 (Machine Learning) - 深度学习 (Deep Learning)

**Required characters:**
这、是、一、个、测、试、文、档、用、于、验、证、中、字、符、的、正、确、显、示、华、人、民、共、和、国、首、都、北、京

### Japanese Section (日本語)
これはテストドキュメントです。日本語の文字が正しく表示されることを確認します。

プログラミング (Programming) - データベース (Datenbank) - アルゴリズム (Algorithmus)

**Required characters:**
- Hiragana: こ、れ、は、て、す、と、く、ま、を、し、か、り、ち、そ、う、え、ん
- Katakana: テ、ス、ト、ド、キ、ュ、メ、ン、プ、ロ、グ、ラ、ミ、ン、グ、デ、タ、ベ、ア、ル、ゴ、リ、ズ、ム
- Kanji: 日、本、語、文、字、正、表、示、確、認

### Korean Section (한국어)
이것은 테스트 문서입니다. 한국어 문자가 올바르게 표시되는지 확인합니다.

소프트웨어 개발 (Softwareentwicklung) - 클라우드 컴퓨팅 (Cloud Computing) - 사이버 보안 (Cybersicherheit)

**Required Hangul syllables:**
이、것、은、테、스、트、문、서、입、니、다、한、국、어、자、가、올、바、르、게、시、되、는、지、확、인、합、소、프、트、웨、어、개、발、클、라、우、드、컴、퓨、팅、사、이、버、보、안

## Test Requirements

✅ **Coverage Goal**: 100% of characters from all test scenarios must render
✅ **No Boxes**: Characters must not display as ▯ or □
✅ **Font Embedding**: Font must be properly embedded in PDFs
✅ **Glyph Quality**: 8x8 pixel bitmap must be clear and readable

## Quality Metrics

- **Character Count**: Track total unique characters needed
- **Coverage Percentage**: (Implemented / Required) × 100%
- **Missing Characters**: List of characters not yet in font modules
- **Build Success**: Font builds without errors
- **PDF Rendering**: Characters render correctly in generated PDFs
