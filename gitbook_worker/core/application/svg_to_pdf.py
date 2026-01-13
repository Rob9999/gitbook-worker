from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from gitbook_worker.core.ports.svg_to_pdf import SvgToPdfConverterPort


@dataclass(frozen=True)
class SvgToPdfResult:
    converted: bool
    used_converter: str | None


def default_svg_to_pdf_converters() -> list[SvgToPdfConverterPort]:
    """Return available SVG->PDF converter adapters.

    The list contains *instances* so adapters can cache imports.
    """

    from gitbook_worker.adapters.svg.cairosvg_svg_to_pdf import (
        CairoSvgSvgToPdfConverter,
    )
    from gitbook_worker.adapters.svg.svglib_svg_to_pdf import SvglibSvgToPdfConverter

    candidates: list[SvgToPdfConverterPort] = [
        CairoSvgSvgToPdfConverter(),
        SvglibSvgToPdfConverter(),
    ]
    return [c for c in candidates if c.is_available()]


def _order_converters(
    converters: Iterable[SvgToPdfConverterPort],
    prefer: Sequence[str] | None,
) -> list[SvgToPdfConverterPort]:
    converters_list = list(converters)
    if not prefer:
        return converters_list

    by_name = {c.name: c for c in converters_list}
    ordered: list[SvgToPdfConverterPort] = []

    for name in prefer:
        converter = by_name.pop(name, None)
        if converter is not None:
            ordered.append(converter)

    # Append remaining converters in original order
    for converter in converters_list:
        if converter.name in by_name:
            ordered.append(converter)
            by_name.pop(converter.name, None)

    return ordered


def ensure_svg_pdf(
    svg_file: Path,
    *,
    pdf_file: Path | None = None,
    prefer: Sequence[str] | None = None,
    converters: Iterable[SvgToPdfConverterPort] | None = None,
    logger: logging.Logger | None = None,
) -> SvgToPdfResult:
    """Ensure a matching PDF exists for an SVG file.

    - Skips conversion if the target PDF is already newer than the SVG.
    - Tries a set of converter adapters in order.

    Returns:
        SvgToPdfResult(converted, used_converter)
    """

    log = logger or logging.getLogger(__name__)

    if not svg_file.exists() or svg_file.suffix.lower() != ".svg":
        return SvgToPdfResult(converted=False, used_converter=None)

    resolved_svg = svg_file.resolve()
    target_pdf = (pdf_file or resolved_svg.with_suffix(".pdf")).resolve()

    try:
        if target_pdf.exists():
            if target_pdf.stat().st_mtime >= resolved_svg.stat().st_mtime:
                return SvgToPdfResult(converted=True, used_converter=None)
    except OSError:
        # Best-effort: if stat fails, try conversion.
        pass

    target_pdf.parent.mkdir(parents=True, exist_ok=True)

    chosen_converters = (
        list(converters) if converters is not None else default_svg_to_pdf_converters()
    )
    if not chosen_converters:
        return SvgToPdfResult(converted=False, used_converter=None)

    ordered = _order_converters(chosen_converters, prefer)

    for converter in ordered:
        try:
            converter.convert(svg_file=resolved_svg, pdf_file=target_pdf)
            log.info("Converted SVG → PDF (%s): %s", converter.name, target_pdf)
            return SvgToPdfResult(converted=True, used_converter=converter.name)
        except Exception as exc:
            log.debug("SVG→PDF converter '%s' failed: %s", converter.name, exc)

    return SvgToPdfResult(converted=False, used_converter=None)
