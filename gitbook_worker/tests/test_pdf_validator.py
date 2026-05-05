from __future__ import annotations

import textwrap
from pathlib import Path

from gitbook_worker.tools.testing.pdf_validator import (
    FontInfo,
    count_unicode_ranges,
    font_name_matches,
    load_expected_fonts,
    normalize_font_name,
    parse_pdffonts_output,
    validate_pdf_font_gate,
)


def test_normalize_font_name_removes_subset_prefix_and_punctuation() -> None:
    assert normalize_font_name("/IRPKLE+TwemojiMozilla") == "twemojimozilla"
    assert normalize_font_name("DNMTDM+ERDACCbyCJK-Regular") == "erdaccbycjkregular"


def test_font_name_matches_configured_erda_cjk_subset() -> None:
    assert font_name_matches("ERDA CC-BY CJK", "DNMTDM+ERDACCbyCJK-Regular")


def test_font_name_matches_configured_twemoji_subset() -> None:
    assert font_name_matches("Twemoji Mozilla", "IRPKLE+TwemojiMozilla")


def test_parse_pdffonts_output_handles_multiword_types() -> None:
    output = textwrap.dedent(
        """
        Syntax Error: No display font for 'ArialUnicode'
        name                                 type              encoding         emb sub uni object ID
        ------------------------------------ ----------------- ---------------- --- --- --- ---------
        IRPKLE+TwemojiMozilla                CID TrueType      Identity-H       yes yes yes    353  0
        DNMTDM+ERDACCbyCJK-Regular           CID TrueType      Identity-H       yes yes yes    469  0
        Times-Roman                          Type 1            WinAnsi          no  no  no    1423  0
        """
    )

    fonts = parse_pdffonts_output(output)

    assert fonts[0] == FontInfo(
        name="IRPKLE+TwemojiMozilla",
        font_type="CID TrueType",
        encoding="Identity-H",
        embedded=True,
        subset=True,
        unicode_map=True,
        source="pdffonts",
    )
    assert fonts[2].embedded is False


def test_load_expected_fonts_reads_configured_names(tmp_path: Path) -> None:
    config = tmp_path / "fonts.yml"
    config.write_text(
        textwrap.dedent(
            """
            version: 1.0.0
            fonts:
              EMOJI:
                name: Custom Emoji
                paths: []
                license: Test
                license_url: https://example.invalid/license
              CJK:
                name: Custom CJK
                paths: []
                license: Test
                license_url: https://example.invalid/license
            """
        ),
        encoding="utf-8",
    )

    expected = load_expected_fonts(config)

    assert expected == {"EMOJI": "Custom Emoji", "CJK": "Custom CJK"}


def test_validate_pdf_font_gate_accepts_required_fonts_and_cjk_text(
    tmp_path: Path,
) -> None:
    config = tmp_path / "fonts.yml"
    config.write_text(
        textwrap.dedent(
            """
            version: 1.0.0
            fonts:
              EMOJI:
                name: Twemoji Mozilla
                paths: []
                license: CC BY 4.0
                license_url: https://creativecommons.org/licenses/by/4.0/
              CJK:
                name: ERDA CC-BY CJK
                paths: []
                license: CC BY 4.0
                license_url: https://creativecommons.org/licenses/by/4.0/
            """
        ),
        encoding="utf-8",
    )
    fonts = [
        FontInfo("IRPKLE+TwemojiMozilla", "CID TrueType", embedded=True),
        FontInfo("DNMTDM+ERDACCbyCJK-Regular", "CID TrueType", embedded=True),
    ]

    result = validate_pdf_font_gate(
        tmp_path / "sample.pdf",
        fonts_config_path=config,
        fonts=fonts,
        text="Hallo 你好世界",
    )

    assert result.passed
    assert result.text_ranges["CJK"] == 4
    assert not result.errors


def test_validate_pdf_font_gate_reports_missing_or_unembedded_fonts(
    tmp_path: Path,
) -> None:
    config = tmp_path / "fonts.yml"
    config.write_text(
        textwrap.dedent(
            """
            version: 1.0.0
            fonts:
              EMOJI:
                name: Twemoji Mozilla
                paths: []
                license: CC BY 4.0
                license_url: https://creativecommons.org/licenses/by/4.0/
              CJK:
                name: ERDA CC-BY CJK
                paths: []
                license: CC BY 4.0
                license_url: https://creativecommons.org/licenses/by/4.0/
            """
        ),
        encoding="utf-8",
    )
    fonts = [FontInfo("IRPKLE+TwemojiMozilla", "CID TrueType", embedded=False)]

    result = validate_pdf_font_gate(
        tmp_path / "sample.pdf",
        fonts_config_path=config,
        fonts=fonts,
        text="Hallo",
    )

    assert not result.passed
    assert "not embedded" in result.errors[0]
    assert any("CJK" in error for error in result.errors)


def test_count_unicode_ranges_ignores_unknown_ranges() -> None:
    assert count_unicode_ranges("abc 你好", ["CJK", "Unknown"]) == {"CJK": 2}
