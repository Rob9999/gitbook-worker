"""Tests verifying the exact dimensions of tables in PDF output."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.skipif(
        shutil.which("lualatex") is None or shutil.which("pdfinfo") is None,
        reason="lualatex or pdfinfo not installed",
    ),
    pytest.mark.slow,  # These tests involve LaTeX compilation
]

# Constants for paper dimensions in mm
PAPER_SIZES = {"A4": (210, 297), "A3": (297, 420), "A2": (420, 594), "A1": (594, 841)}

# Conversion constants
PT_TO_MM = 25.4 / 72.0  # 1 pt = 1/72 inch, 1 inch = 25.4 mm
DIMENSION_TOLERANCE = 5  # Allowed variation in mm


def create_latex_document(
    content: str, page_width: float, page_height: float, landscape: bool = False
) -> str:
    """
    Create a complete LaTeX document with table content.

    Args:
        content (str): The main table content
        page_width (float): Target page width in mm
        page_height (float): Target page height in mm
        landscape (bool): Whether to use landscape orientation

    Returns:
        str: Complete LaTeX document content
    """

    def convert_table_to_latex(text: str) -> str:
        """Convert Markdown pipe tables in ``text`` to LaTeX ``longtable`` blocks."""

        lines = text.splitlines()
        out_lines: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            if (
                "|" in line
                and i + 1 < len(lines)
                and re.match(r"^\s*\|?\s*:?-+", lines[i + 1])
            ):
                header = [x.strip() for x in line.strip().strip("|").split("|")]
                alignments = [
                    x.strip() for x in lines[i + 1].strip().strip("|").split("|")
                ]
                column_specs: list[str] = []
                for align in alignments:
                    if align.startswith(":") and align.endswith(":"):
                        column_specs.append("c")
                    elif align.endswith(":"):
                        column_specs.append("r")
                    else:
                        column_specs.append("l")
                out_lines.append(
                    "\\begin{longtable}{@{}" + "".join(column_specs) + "@{}}"
                )
                out_lines.append("\\toprule")
                out_lines.append(f"{' & '.join(header)} \\\\")
                out_lines.append("\\midrule")
                out_lines.append("\\endhead")
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    row = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                    out_lines.append(f"{' & '.join(row)} \\\\")
                    i += 1
                out_lines.append("\\bottomrule")
                out_lines.append("\\end{longtable}")
            else:
                out_lines.append(line)
                i += 1

        return "\n".join(out_lines)

    # Process content
    content = convert_table_to_latex(content)

    latex_packages = [
        "\\usepackage{geometry}",
        "\\usepackage{calc}",
        "\\usepackage{longtable}",
        "\\usepackage{booktabs}",
        "\\usepackage{array}",
    ]
    geometry_settings = [
        f"paperwidth={page_width}mm",
        f"paperheight={page_height}mm",
        "left=15mm",
        "right=15mm",
        "top=15mm",
        "bottom=15mm",
    ]
    if landscape:
        geometry_settings.append("landscape")

    document_parts = [
        "\\documentclass{article}",
        *latex_packages,
        f"\\geometry{{{','.join(geometry_settings)}}}",
        "\\AtBeginDocument{\\pagestyle{empty}}",
        "\\begin{document}",
        content,
        "\\end{document}",
    ]

    return "\n".join(document_parts)


def generate_test_table(columns: int, content_multiplier: int = 1) -> str:
    """
    Generate a test table with specified number of columns and content length.

    Args:
        columns (int): Number of columns in the table
        content_multiplier (int): Factor to multiply content length

    Returns:
        str: Generated Markdown table
    """
    header = [f"Column{i:02d}" for i in range(columns)]
    separator = ["---" for _ in range(columns)]
    content = ["content" * content_multiplier for _ in range(columns)]

    return (
        f"| {' | '.join(header)} |\n"
        f"|{('|'.join(separator))}|\n"
        f"| {' | '.join(content)} |"
    )


def test_table_exact_dimensions(
    output_dir: Path, artifact_dir: Path, logger: logging.Logger
) -> None:
    """Test table dimensions with different content lengths and paper sizes."""
    test_cases = [
        (
            "| Col1 | Col2 | Col3 |\n|------|------|------|\n| abc | def | ghi |",
            *PAPER_SIZES["A4"],
        ),
        (generate_test_table(columns=10, content_multiplier=2), *PAPER_SIZES["A3"]),
        (generate_test_table(columns=15, content_multiplier=3), *PAPER_SIZES["A2"]),
        (generate_test_table(columns=20, content_multiplier=4), *PAPER_SIZES["A1"]),
    ]

    def process_and_verify_table(
        table_content: str,
        expected_width: float,
        expected_height: float,
        idx: int,
        landscape: bool = False,
    ) -> None:
        """Process a table and verify its dimensions in the resulting PDF."""

        md_file = output_dir / f"table{idx}.md"
        tex_file = output_dir / f"table{idx}.tex"
        pdf_file = output_dir / f"table{idx}.pdf"

        md_file.write_text(table_content, encoding="utf-8")
        logger.info("wrote markdown for table%s", idx)

        tex_content = create_latex_document(
            table_content, expected_width, expected_height, landscape=landscape
        )
        tex_file.write_text(tex_content, encoding="utf-8")
        logger.info("generated LaTeX for table%s", idx)

        try:
            result = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", str(tex_file)],
                cwd=output_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("LaTeX stdout for table%s:\n%s", idx, result.stdout)
            if result.stderr:
                logger.info("LaTeX stderr for table%s:\n%s", idx, result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error("LaTeX compilation failed for table%s", idx)
            logger.error(e.stdout)
            logger.error(e.stderr)
            raise

        assert pdf_file.is_file(), f"PDF file not created for table{idx}"

        info = subprocess.check_output(
            ["pdfinfo", str(pdf_file)], encoding="utf-8", errors="replace"
        )
        match = re.search(r"Page size:\s+(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) pts", info)
        assert match, f"Could not extract page size for table{idx}"

        actual_width = float(match.group(1)) * PT_TO_MM
        actual_height = float(match.group(2)) * PT_TO_MM

        assert abs(actual_width - expected_width) < DIMENSION_TOLERANCE, (
            f"Table {idx}: Width {actual_width:.1f}mm doesn't match "
            f"expected {expected_width}mm"
        )
        assert abs(actual_height - expected_height) < DIMENSION_TOLERANCE, (
            f"Table {idx}: Height {actual_height:.1f}mm doesn't match "
            f"expected {expected_height}mm"
        )

        shutil.copy(pdf_file, artifact_dir / pdf_file.name)

    for idx, (table_content, expected_width, expected_height) in enumerate(test_cases):
        process_and_verify_table(table_content, expected_width, expected_height, idx)


def test_table_exact_dimensions_landscape(
    output_dir: Path, artifact_dir: Path, logger: logging.Logger
) -> None:
    """Test table dimensions when the table should use landscape mode."""

    table_content = generate_test_table(columns=15, content_multiplier=3)
    width, height = PAPER_SIZES["A2"]
    expected_width, expected_height = height, width

    def process_and_verify_table(
        table_content: str,
        expected_width: float,
        expected_height: float,
        landscape: bool = True,
    ) -> None:
        """Process and verify a table in landscape mode."""

        md_file = output_dir / "table_landscape.md"
        tex_file = output_dir / "table_landscape.tex"
        pdf_file = output_dir / "table_landscape.pdf"

        md_file.write_text(table_content, encoding="utf-8")
        logger.info("wrote landscape markdown")

        tex_content = create_latex_document(
            table_content, width, height, landscape=landscape
        )
        tex_file.write_text(tex_content, encoding="utf-8")
        logger.info("generated landscape LaTeX")

        try:
            result = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", str(tex_file)],
                cwd=output_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("LaTeX stdout landscape:\n%s", result.stdout)
            if result.stderr:
                logger.info("LaTeX stderr landscape:\n%s", result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error("LaTeX compilation failed for landscape table")
            logger.error(e.stdout)
            logger.error(e.stderr)
            raise

        assert pdf_file.is_file(), "PDF file not created for landscape table"

        info = subprocess.check_output(
            ["pdfinfo", str(pdf_file)], encoding="utf-8", errors="replace"
        )
        match = re.search(r"Page size:\s+(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) pts", info)
        assert match, "Could not extract page size for landscape table"

        actual_width = float(match.group(1)) * PT_TO_MM
        actual_height = float(match.group(2)) * PT_TO_MM

        assert abs(actual_width - expected_width) < DIMENSION_TOLERANCE, (
            "Landscape table: Width "
            f"{actual_width:.1f}mm doesn't match expected {expected_width}mm"
        )
        assert abs(actual_height - expected_height) < DIMENSION_TOLERANCE, (
            "Landscape table: Height "
            f"{actual_height:.1f}mm doesn't match expected {expected_height}mm"
        )

        shutil.copy(pdf_file, artifact_dir / pdf_file.name)

    process_and_verify_table(table_content, expected_width, expected_height)


# def test_exact_dimensions():
