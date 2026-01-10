#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.tools.publishing.font_attribution import (
    generate_font_attribution_files,
)


@pytest.fixture()
def license_fonts_stub(tmp_path: Path) -> Path:
    path = tmp_path / "LICENSE-FONTS"
    path.write_text(
        """
Header text

-----------------------------------------------------------------------
Creative Commons Attribution 4.0 International (for ERDA fonts)
-----------------------------------------------------------------------

CC-BY TEXT START
CC-BY TEXT END

-----------------------------------------------------------------------
Bitstream Vera License (for bundled DejaVu fonts)
-----------------------------------------------------------------------

BITSTREAM TEXT START
BITSTREAM TEXT END
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture()
def fonts_yml_stub(tmp_path: Path) -> Path:
    path = tmp_path / "fonts.yml"
    path.write_text(
        """
version: 1.0.0
fonts:
  EMOJI:
    name: "Twemoji Mozilla"
    paths: ["/tmp/TwemojiMozilla.ttf"]
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    source_url: "https://example.com/twemoji"
    version: "0.1"
    usage_note: "Emoji font"
  SERIF:
    name: "DejaVu Serif"
    paths: []
    license: "Bitstream Vera License + Public Domain"
    license_url: "https://dejavu-fonts.github.io/License.html"
    source_url: "https://example.com/dejavu"
    version: "2.37"
""".lstrip(),
        encoding="utf-8",
    )
    return path


def test_generate_attribution_writes_files(
    tmp_path: Path, fonts_yml_stub: Path, license_fonts_stub: Path
) -> None:
    out_dir = tmp_path / "out"
    result = generate_font_attribution_files(
        out_dir=out_dir,
        fonts_config_path=fonts_yml_stub,
        license_fonts_path=license_fonts_stub,
    )

    assert result.attribution_path.exists()
    assert (out_dir / "LICENSE-CC-BY-4.0").exists()
    assert (out_dir / "LICENSE-BITSTREAM-VERA").exists()

    attribution_text = result.attribution_path.read_text(encoding="utf-8")
    assert "Twemoji Mozilla" in attribution_text
    assert "DejaVu Serif" in attribution_text


def test_generate_attribution_requires_license_metadata(
    tmp_path: Path, license_fonts_stub: Path
) -> None:
    fonts_yml = tmp_path / "fonts.yml"
    fonts_yml.write_text(
        """
version: 1.0.0
fonts:
  EMOJI:
    name: "Twemoji Mozilla"
    paths: ["/tmp/TwemojiMozilla.ttf"]
    license: "CC BY 4.0"
    license_url: ""  # missing
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required fields"):
        generate_font_attribution_files(
            out_dir=tmp_path / "out",
            fonts_config_path=fonts_yml,
            license_fonts_path=license_fonts_stub,
        )
