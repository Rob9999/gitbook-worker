#!/usr/bin/env python3
"""Test if svglib pollutes source directory during SVG to PDF conversion."""

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import tempfile
import pathlib
import shutil

svg_source = pathlib.Path("de/content/.gitbook/assets/neutral-grid.svg")
temp_dir = pathlib.Path(tempfile.mkdtemp())

print(f"Source SVG: {svg_source}")
print(f"Temp directory: {temp_dir}")

# Copy SVG to temp
temp_svg = temp_dir / "test.svg"
shutil.copy2(svg_source, temp_svg)
print(f"\nCopied to: {temp_svg}")

# Convert in temp
drawing = svg2rlg(str(temp_svg))
temp_pdf = temp_dir / "test.pdf"
renderPDF.drawToFile(drawing, str(temp_pdf))
print(f"PDF created: {temp_pdf}")

# Check pollution
print(f"\nFiles in temp: {sorted(temp_dir.iterdir())}")
pdf_in_content = list(svg_source.parent.glob("neutral-grid.pdf"))
print(f"PDFs in content assets: {pdf_in_content}")

if pdf_in_content:
    print("\n❌ POLLUTION DETECTED!")
else:
    print("\n✅ No pollution - content directory clean")
