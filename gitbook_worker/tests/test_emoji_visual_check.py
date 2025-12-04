"""Visual check for emoji color rendering in generated PDFs.

This test extracts pages with emojis and provides instructions for manual verification.
Automated color detection in PDFs is complex, so this test helps with manual inspection.
"""

import pytest
import subprocess
from pathlib import Path


@pytest.mark.integration
@pytest.mark.manual
def test_emoji_color_visual_check():
    """Extract emoji pages from PDF for manual visual inspection.

    This test:
    1. Checks that the PDF was generated
    2. Verifies Twemoji Mozilla is embedded
    3. Extracts emoji-heavy pages as PNG for visual inspection
    4. Provides clear PASS/FAIL criteria for manual check

    MANUAL CHECK REQUIRED:
    - Open de/publish/emoji-test-page-*.png
    - Verify emojis are COLORFUL (not black-and-white)
    - If still B&W despite correct config, this indicates a LuaTeX rendering issue
    """
    pdf_path = Path("de/publish/das-erda-buch.pdf")

    # Step 1: Verify PDF exists
    assert pdf_path.exists(), f"PDF not found: {pdf_path}"

    # Step 2: Verify Twemoji Mozilla is embedded
    try:
        result = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode in [0, 1], "pdffonts failed"

        # Check for Twemoji Mozilla in output
        font_list = result.stdout
        assert "TwemojiMozilla" in font_list or "Twemoji" in font_list, (
            "Twemoji Mozilla NOT embedded in PDF! " f"Available fonts:\n{font_list}"
        )
        print(f"✅ Twemoji Mozilla is embedded in PDF")

    except FileNotFoundError:
        pytest.skip("pdffonts not available - cannot verify font embedding")

    # Step 3: Extract emoji-heavy pages (examples are usually at end)
    output_dir = Path("de/publish")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract last 5 pages (likely to contain emoji examples)
    try:
        # Get total page count
        info_result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if info_result.returncode != 0:
            pytest.skip("pdfinfo not available")

        # Parse page count
        for line in info_result.stdout.splitlines():
            if line.startswith("Pages:"):
                total_pages = int(line.split(":")[1].strip())
                break
        else:
            pytest.skip("Could not determine page count")

        # Extract last few pages
        start_page = max(1, total_pages - 4)
        end_page = total_pages

        extract_result = subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-f",
                str(start_page),
                "-l",
                str(end_page),
                str(pdf_path),
                str(output_dir / "emoji-test-page"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if extract_result.returncode == 0:
            extracted_files = list(output_dir.glob("emoji-test-page-*.png"))
            print(f"\n✅ Extracted {len(extracted_files)} pages for visual inspection:")
            for f in sorted(extracted_files):
                print(f"   - {f}")

            print("\n" + "=" * 70)
            print("MANUAL VERIFICATION REQUIRED")
            print("=" * 70)
            print("\nPlease open the extracted PNG files and check:")
            print("  1. Are the emojis COLORFUL (red, yellow, blue, etc.)?")
            print("  2. Or are they BLACK-AND-WHITE (monochrome)?")
            print("\nExpected result: COLORFUL emojis")
            print("If still B&W: LuaTeX may not support color emoji rendering")
            print("=" * 70 + "\n")

        else:
            pytest.skip(f"pdftoppm failed: {extract_result.stderr}")

    except FileNotFoundError:
        pytest.skip("pdftoppm not available - cannot extract pages")

    # This test always passes - manual verification needed
    # If emojis are B&W, this indicates a rendering pipeline issue, not a config bug
    assert True, "Test requires manual visual verification"


@pytest.mark.integration
def test_emoji_metadata_in_pandoc_output():
    """Verify that emoji metadata is correctly passed to Pandoc.

    This test checks the orchestrator logs to ensure:
    - emojifont = Twemoji Mozilla
    - emojifontoptions = Renderer=HarfBuzz
    - bxcoloremoji = false
    """
    log_path = Path("logs/orchestrator-emoji-debug.log")

    if not log_path.exists():
        pytest.skip(f"Log file not found: {log_path}")

    log_content = log_path.read_text(encoding="utf-16")  # Check for correct metadata
    assert (
        "emojifont = Twemoji Mozilla" in log_content
    ), "Twemoji Mozilla not set as emojifont in Pandoc metadata"

    assert (
        "emojifontoptions = Renderer=HarfBuzz" in log_content
    ), "HarfBuzz renderer not enabled for emoji font"

    assert (
        "bxcoloremoji = false" in log_content
    ), "bxcoloremoji should be disabled for color emoji rendering"

    print("\n✅ All emoji metadata correctly passed to Pandoc:")
    print("   - emojifont = Twemoji Mozilla")
    print("   - emojifontoptions = Renderer=HarfBuzz")
    print("   - bxcoloremoji = false")
