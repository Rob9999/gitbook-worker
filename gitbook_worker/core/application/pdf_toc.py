from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Sequence

from gitbook_worker.core.ports.pdf_toc import PdfTocEntry, PdfTocExtractorPort


def default_pdf_toc_extractors() -> list[PdfTocExtractorPort]:
    """Return available PDF TOC extractor adapters.

    The list contains *instances* so adapters can cache imports.
    """

    from gitbook_worker.adapters.pdf.pypdf_toc_extractor import PyPdfTocExtractor

    candidates: list[PdfTocExtractorPort] = [PyPdfTocExtractor()]
    return [c for c in candidates if c.is_available()]


def _order_extractors(
    extractors: Iterable[PdfTocExtractorPort],
    prefer: Sequence[str] | None,
) -> list[PdfTocExtractorPort]:
    extractors_list = list(extractors)
    if not prefer:
        return extractors_list

    by_name = {e.name: e for e in extractors_list}
    ordered: list[PdfTocExtractorPort] = []

    for name in prefer:
        extractor = by_name.pop(name, None)
        if extractor is not None:
            ordered.append(extractor)

    # Append remaining extractors in original order
    for extractor in extractors_list:
        if extractor.name in by_name:
            ordered.append(extractor)
            by_name.pop(extractor.name, None)

    return ordered


def extract_pdf_toc(
    pdf_file: Path,
    *,
    prefer: Sequence[str] | None = None,
    extractors: Iterable[PdfTocExtractorPort] | None = None,
    logger: logging.Logger | None = None,
) -> list[PdfTocEntry]:
    """Extract TOC/outline entries from a PDF.

    The application layer selects an adapter (extractor) and delegates the IO.
    """

    log = logger or logging.getLogger(__name__)

    if not pdf_file.exists() or pdf_file.suffix.lower() != ".pdf":
        return []

    resolved_pdf = pdf_file.resolve()

    chosen_extractors = (
        list(extractors) if extractors is not None else default_pdf_toc_extractors()
    )
    if not chosen_extractors:
        return []

    ordered = _order_extractors(chosen_extractors, prefer)

    for extractor in ordered:
        try:
            entries = extractor.extract(pdf_file=resolved_pdf)
            log.info("Extracted PDF TOC (%s): %s", extractor.name, resolved_pdf)
            return entries
        except Exception as exc:
            log.debug("PDF TOC extractor '%s' failed: %s", extractor.name, exc)

    return []
