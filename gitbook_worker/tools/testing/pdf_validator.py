"""Validate PDF font embedding and text-range signals.

This module is intentionally small and scriptable. It supports release smoke
checks where the important question is whether the PDF still embeds the
configured emoji and CJK fonts after a publisher change.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from pypdf import PdfReader

from gitbook_worker.tools.publishing.font_config import FontConfigLoader


DEFAULT_REQUIRED_FONT_KEYS = ("EMOJI", "CJK")
DEFAULT_REQUIRED_TEXT_RANGES = ("CJK",)

UNICODE_RANGES = {
    "CJK": ("\u4e00", "\u9fff"),
    "Hiragana": ("\u3040", "\u309f"),
    "Katakana": ("\u30a0", "\u30ff"),
    "Hangul": ("\uac00", "\ud7af"),
    "Arabic": ("\u0600", "\u06ff"),
    "Devanagari": ("\u0900", "\u097f"),
    "Ethiopic": ("\u1200", "\u137f"),
    "Hebrew": ("\u0590", "\u05ff"),
    "Thai": ("\u0e00", "\u0e7f"),
    "Tamil": ("\u0b80", "\u0bff"),
    "Bengali": ("\u0980", "\u09ff"),
}

_FONT_SUBSET_PREFIX = re.compile(r"^/?[A-Z]{6}\+")
_FONT_NAME_CHARS = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class FontInfo:
    """Font information extracted from a PDF."""

    name: str
    font_type: str
    encoding: str | None = None
    embedded: bool = False
    subset: bool | None = None
    unicode_map: bool | None = None
    source: str = "unknown"


@dataclass(frozen=True)
class RequiredFontCheck:
    """Validation result for one configured font."""

    key: str
    expected_name: str
    matched_name: str | None
    embedded: bool

    @property
    def passed(self) -> bool:
        return self.matched_name is not None and self.embedded


@dataclass(frozen=True)
class PDFValidationResult:
    """Result of a PDF font/text smoke validation."""

    pdf_path: Path
    fonts: tuple[FontInfo, ...]
    required_fonts: tuple[RequiredFontCheck, ...]
    text_ranges: Mapping[str, int]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


def normalize_font_name(name: str) -> str:
    """Return a comparable font name without subset prefix or punctuation."""

    without_subset = _FONT_SUBSET_PREFIX.sub("", name.strip())
    without_subset = without_subset.removeprefix("/")
    return _FONT_NAME_CHARS.sub("", without_subset.lower())


def font_name_matches(expected_name: str, actual_name: str) -> bool:
    """Match configured font names against embedded subset font names."""

    expected = normalize_font_name(expected_name)
    actual = normalize_font_name(actual_name)
    if not expected or not actual:
        return False
    return expected in actual or actual in expected


def parse_pdffonts_output(output: str) -> list[FontInfo]:
    """Parse Poppler pdffonts output into FontInfo entries."""

    fonts: list[FontInfo] = []
    in_table = False
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("----"):
            in_table = True
            continue
        if not in_table:
            continue

        columns = re.split(r"\s{2,}", line)
        if len(columns) < 6:
            continue

        fonts.append(
            FontInfo(
                name=columns[0],
                font_type=columns[1],
                encoding=columns[2] or None,
                embedded=columns[3].lower() == "yes",
                subset=columns[4].lower() == "yes",
                unicode_map=columns[5].lower() == "yes",
                source="pdffonts",
            )
        )
    return _dedupe_fonts(fonts)


def extract_pdf_fonts(pdf_path: Path) -> list[FontInfo]:
    """Extract fonts with pdffonts first, then pypdf as fallback."""

    try:
        completed = subprocess.run(
            ["pdffonts", str(pdf_path)],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return extract_pdf_fonts_with_pypdf(pdf_path)

    parsed = parse_pdffonts_output(completed.stdout)
    return parsed or extract_pdf_fonts_with_pypdf(pdf_path)


def extract_pdf_fonts_with_pypdf(pdf_path: Path) -> list[FontInfo]:
    """Extract embedded font names using pypdf."""

    reader = PdfReader(str(pdf_path))
    fonts: list[FontInfo] = []
    for page in reader.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        page_fonts = resources.get("/Font")
        if not page_fonts:
            continue
        font_dict = page_fonts.get_object()
        for font_ref in font_dict.values():
            font_obj = font_ref.get_object()
            fonts.append(
                FontInfo(
                    name=str(font_obj.get("/BaseFont", "Unknown")),
                    font_type=str(font_obj.get("/Subtype", "Unknown")),
                    encoding=str(font_obj.get("/Encoding", "")) or None,
                    embedded=_font_object_is_embedded(font_obj),
                    source="pypdf",
                )
            )
    return _dedupe_fonts(fonts)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract concatenated PDF text using pypdf."""

    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def count_unicode_ranges(
    text: str,
    ranges: Iterable[str] = UNICODE_RANGES.keys(),
) -> dict[str, int]:
    """Count characters in configured Unicode ranges."""

    counts: dict[str, int] = {}
    for range_name in ranges:
        bounds = UNICODE_RANGES.get(range_name)
        if bounds is None:
            continue
        low, high = bounds
        counts[range_name] = sum(1 for char in text if low <= char <= high)
    return counts


def load_expected_fonts(
    fonts_config_path: Path | None = None,
    font_keys: Sequence[str] = DEFAULT_REQUIRED_FONT_KEYS,
) -> dict[str, str]:
    """Load expected font family names from fonts.yml."""

    loader = FontConfigLoader(fonts_config_path)
    expected: dict[str, str] = {}
    for font_key in font_keys:
        font = loader.get_font(font_key)
        if font and font.name:
            expected[font_key] = font.name
    return expected


def validate_pdf_font_gate(
    pdf_path: Path | str,
    fonts_config_path: Path | None = None,
    required_font_keys: Sequence[str] = DEFAULT_REQUIRED_FONT_KEYS,
    required_text_ranges: Sequence[str] = DEFAULT_REQUIRED_TEXT_RANGES,
    fonts: Sequence[FontInfo] | None = None,
    text: str | None = None,
) -> PDFValidationResult:
    """Validate that configured fonts and text ranges are visible in a PDF."""

    path = Path(pdf_path)
    expected_fonts = load_expected_fonts(fonts_config_path, required_font_keys)
    extracted_fonts = tuple(fonts if fonts is not None else extract_pdf_fonts(path))
    extracted_text = text if text is not None else extract_pdf_text(path)
    text_ranges = count_unicode_ranges(extracted_text, required_text_ranges)

    errors: list[str] = []
    warnings: list[str] = []
    required_checks: list[RequiredFontCheck] = []

    missing_keys = [key for key in required_font_keys if key not in expected_fonts]
    for missing_key in missing_keys:
        errors.append(f"Required font key {missing_key!r} not found in fonts.yml")

    for font_key, expected_name in expected_fonts.items():
        match = _find_font_match(expected_name, extracted_fonts)
        check = RequiredFontCheck(
            key=font_key,
            expected_name=expected_name,
            matched_name=match.name if match else None,
            embedded=bool(match and match.embedded),
        )
        required_checks.append(check)
        if match is None:
            errors.append(
                f"Configured font {font_key}={expected_name!r} not found in PDF"
            )
        elif not match.embedded:
            errors.append(
                f"Configured font {font_key}={expected_name!r} found as {match.name!r}, "
                "but it is not embedded"
            )

    for range_name in required_text_ranges:
        if text_ranges.get(range_name, 0) <= 0:
            errors.append(
                f"Required Unicode range {range_name!r} not found in PDF text"
            )

    if not extracted_fonts:
        warnings.append("No fonts could be extracted from PDF")

    return PDFValidationResult(
        pdf_path=path,
        fonts=extracted_fonts,
        required_fonts=tuple(required_checks),
        text_ranges=text_ranges,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def result_to_dict(result: PDFValidationResult) -> dict[str, object]:
    """Convert a validation result into JSON-serializable data."""

    data = asdict(result)
    data["pdf_path"] = str(result.pdf_path)
    data["passed"] = result.passed
    return data


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI parser for manual PDF smoke checks."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path, help="PDF file to validate")
    parser.add_argument(
        "--fonts-config",
        type=Path,
        default=None,
        help="Path to fonts.yml; defaults to the package configuration",
    )
    parser.add_argument(
        "--font-key",
        action="append",
        dest="font_keys",
        default=None,
        help="Required font key from fonts.yml; repeatable. Defaults to EMOJI and CJK",
    )
    parser.add_argument(
        "--text-range",
        action="append",
        dest="text_ranges",
        default=None,
        help="Required Unicode text range; repeatable. Defaults to CJK",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the PDF validator CLI."""

    args = build_arg_parser().parse_args(argv)
    result = validate_pdf_font_gate(
        args.pdf,
        fonts_config_path=args.fonts_config,
        required_font_keys=tuple(args.font_keys or DEFAULT_REQUIRED_FONT_KEYS),
        required_text_ranges=tuple(args.text_ranges or DEFAULT_REQUIRED_TEXT_RANGES),
    )
    if args.json:
        print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
    else:
        print(f"PDF: {result.pdf_path}")
        print(f"Passed: {result.passed}")
        print("Required fonts:")
        for check in result.required_fonts:
            matched = check.matched_name or "<missing>"
            print(
                f"  {check.key}: expected={check.expected_name!r} "
                f"matched={matched!r} embedded={check.embedded}"
            )
        print("Text ranges:")
        for range_name, count in result.text_ranges.items():
            print(f"  {range_name}: {count}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
    return 0 if result.passed else 1


def _find_font_match(expected_name: str, fonts: Iterable[FontInfo]) -> FontInfo | None:
    for font in fonts:
        if font_name_matches(expected_name, font.name):
            return font
    return None


def _dedupe_fonts(fonts: Iterable[FontInfo]) -> list[FontInfo]:
    unique: list[FontInfo] = []
    seen: set[tuple[str, str, str | None, bool]] = set()
    for font in fonts:
        key = (font.name, font.font_type, font.encoding, font.embedded)
        if key not in seen:
            seen.add(key)
            unique.append(font)
    return unique


def _font_object_is_embedded(font_obj: object) -> bool:
    descriptor = _resolve_pdf_object(font_obj.get("/FontDescriptor"))
    if descriptor and _descriptor_has_font_file(descriptor):
        return True

    descendant_fonts = font_obj.get("/DescendantFonts")
    if not descendant_fonts:
        return False
    for descendant_ref in descendant_fonts:
        descendant = _resolve_pdf_object(descendant_ref)
        if not descendant:
            continue
        descriptor = _resolve_pdf_object(descendant.get("/FontDescriptor"))
        if descriptor and _descriptor_has_font_file(descriptor):
            return True
    return False


def _descriptor_has_font_file(descriptor: object) -> bool:
    return any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))


def _resolve_pdf_object(value: object) -> object | None:
    if value is None:
        return None
    if hasattr(value, "get_object"):
        return value.get_object()
    return value


if __name__ == "__main__":
    raise SystemExit(main())
