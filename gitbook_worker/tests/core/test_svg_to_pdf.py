from __future__ import annotations

import time
import os
from pathlib import Path

from gitbook_worker.core.application.svg_to_pdf import ensure_svg_pdf


class _FakeOkConverter:
    name = "ok"

    def is_available(self) -> bool:  # pragma: no cover
        return True

    def convert(self, *, svg_file: Path, pdf_file: Path) -> None:
        pdf_file.write_bytes(b"%PDF-1.4\n%fake\n")


class _FakeFailConverter:
    name = "fail"

    def is_available(self) -> bool:  # pragma: no cover
        return True

    def convert(self, *, svg_file: Path, pdf_file: Path) -> None:
        raise RuntimeError("boom")


def test_ensure_svg_pdf_prefers_named_converters(tmp_path: Path) -> None:
    svg = tmp_path / "demo.svg"
    svg.write_text("<svg width='10' height='10'></svg>", encoding="utf-8")

    pdf = tmp_path / "demo.pdf"

    result = ensure_svg_pdf(
        svg,
        pdf_file=pdf,
        converters=[_FakeOkConverter(), _FakeFailConverter()],
        prefer=("fail", "ok"),
    )

    assert result.converted is True
    assert result.used_converter == "ok"
    assert pdf.exists()


def test_ensure_svg_pdf_skips_when_pdf_newer(tmp_path: Path) -> None:
    svg = tmp_path / "demo.svg"
    svg.write_text("<svg width='10' height='10'></svg>", encoding="utf-8")

    pdf = tmp_path / "demo.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%old\n")

    # Make the PDF appear newer than SVG
    now = time.time()
    pdf.touch()
    pdf_mtime = now
    svg_mtime = now - 100
    Path(svg).touch()

    # Windows timestamp resolution can be coarse; force both via utime
    os.utime(svg, (svg_mtime, svg_mtime))
    os.utime(pdf, (pdf_mtime, pdf_mtime))

    result = ensure_svg_pdf(
        svg,
        pdf_file=pdf,
        converters=[_FakeFailConverter()],
        prefer=("fail",),
    )

    assert result.converted is True
    assert result.used_converter is None


def test_ensure_svg_pdf_returns_false_without_converters(tmp_path: Path) -> None:
    svg = tmp_path / "demo.svg"
    svg.write_text("<svg width='10' height='10'></svg>", encoding="utf-8")

    result = ensure_svg_pdf(svg, converters=[], prefer=("whatever",))
    assert result.converted is False
    assert result.used_converter is None
