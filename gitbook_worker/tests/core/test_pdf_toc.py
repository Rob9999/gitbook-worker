from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.core.application.pdf_toc import extract_pdf_toc
from gitbook_worker.core.ports.pdf_toc import PdfTocEntry


class _FakeOkExtractor:
    name = "ok"

    def is_available(self) -> bool:  # pragma: no cover
        return True

    def extract(self, *, pdf_file: Path) -> list[PdfTocEntry]:
        return [PdfTocEntry(title="Intro", page=1, level=1)]


class _FakeFailExtractor:
    name = "fail"

    def is_available(self) -> bool:  # pragma: no cover
        return True

    def extract(self, *, pdf_file: Path) -> list[PdfTocEntry]:
        raise RuntimeError("boom")


def test_extract_pdf_toc_prefers_named_extractors(tmp_path: Path) -> None:
    pdf = tmp_path / "demo.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%fake\n")

    entries = extract_pdf_toc(
        pdf,
        extractors=[_FakeOkExtractor(), _FakeFailExtractor()],
        prefer=("fail", "ok"),
    )

    assert entries == [PdfTocEntry(title="Intro", page=1, level=1)]


def test_extract_pdf_toc_returns_empty_without_extractors(tmp_path: Path) -> None:
    pdf = tmp_path / "demo.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%fake\n")

    entries = extract_pdf_toc(pdf, extractors=[])
    assert entries == []


def test_pypdf_adapter_smoke_extracts_outline(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")

    from gitbook_worker.adapters.pdf.pypdf_toc_extractor import PyPdfTocExtractor

    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)

    # pypdf versions differ slightly; support both APIs.
    if hasattr(writer, "add_outline_item"):
        writer.add_outline_item("Intro", 0)
    else:
        writer.addBookmark("Intro", 0)

    pdf_path = tmp_path / "with_outline.pdf"
    with pdf_path.open("wb") as f:
        writer.write(f)

    extractor = PyPdfTocExtractor()
    assert extractor.is_available() is True

    entries = extractor.extract(pdf_file=pdf_path)
    assert any(e.title == "Intro" and e.level == 1 for e in entries)
