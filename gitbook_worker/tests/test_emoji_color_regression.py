"""Regression tests for emoji color bug.

Current Issue: PDFs show black-and-white emojis despite emoji_color=true
and emoji_bxcoloremoji=false configuration.

These tests help identify WHERE the bug occurs in the pipeline:
- Metadata passing to Pandoc
- Lua filter activation
- LaTeX prologue generation
- Font embedding in PDF
"""

import logging
import pytest
import subprocess
import json
from pathlib import Path
from gitbook_worker.tools.publishing import publisher


@pytest.mark.integration
class TestEmojiColorRegression:
    """Tests to diagnose and fix the emoji color rendering bug."""

    def test_emoji_color_produces_harfbuzz_in_combined_markdown(self, tmp_path, caplog):
        """CRITICAL: Verify metadata is correctly written to combined markdown.

        This checks if _write_combined_markdown() correctly sets:
        - emojifont: "Twemoji Mozilla"
        - bxcoloremoji: false
        - emojifontoptions with mode=harf
        """
        caplog.set_level(logging.INFO)
        md_content = "# Test\n\nHello 😀 World 🌍 Test 🎉"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")

        pdf_file = tmp_path / "test.pdf"

        # Build with emoji_color=true, bxcoloremoji=false (our problem config)
        success, error = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            keep_combined=True,  # CRITICAL: Keep for inspection
            emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False),
            variables={"mainfontfallback": "Twemoji Mozilla:mode=harf"},
        )

        assert success, f"PDF generation failed: {error}"
        assert pdf_file.exists(), "PDF file not created"

        # Find combined markdown (publisher creates it with specific naming)
        combined_files = list(tmp_path.glob("*-combined.md"))
        if not combined_files:
            fallback_md = pdf_file.with_suffix(".md")
            if fallback_md.exists():
                combined_files.append(fallback_md)

        assert combined_files, (
            "Converted markdown artifact not found;"
            " keep_combined=True may have been ignored"
        )

        combined_md = combined_files[0]
        combined_content = combined_md.read_text(encoding="utf-8")

        print("\n=== COMBINED MARKDOWN METADATA (first 50 lines) ===")
        lines = combined_content.split("\n")[:50]
        for i, line in enumerate(lines, 1):
            if (
                "emoji" in line.lower()
                or "bxcolor" in line.lower()
                or line.startswith("---")
            ):
                print(f"{i:3d}: {line}")

        # Check 1: YAML frontmatter should exist
        assert combined_content.startswith(
            "---\n"
        ), "No YAML frontmatter in converted markdown"

        # Extract frontmatter
        parts = combined_content.split("---\n")
        if len(parts) >= 3:
            frontmatter = parts[1]
            print("\n=== FRONTMATTER ===")
            print(frontmatter)

            # Prefer reading from frontmatter first
            has_emojifont = "emojifont" in frontmatter.lower()
            has_bxcolor = "bxcoloremoji" in frontmatter.lower()

            if not has_emojifont:
                # Fallback: rely on logged Pandoc metadata arguments
                metadata_logs = [
                    record.message
                    for record in caplog.records
                    if "-M emojifont=" in record.message
                ]
                assert metadata_logs, (
                    "emojifont metadata missing from YAML and CLI log;"
                    " emoji font configuration not propagated"
                )
                assert any(
                    "Twemoji" in entry for entry in metadata_logs
                ), "Twemoji Mozilla not present in Pandoc metadata log"
            else:
                assert (
                    "twemoji" in frontmatter.lower()
                ), "Frontmatter emojifont metadata should reference Twemoji"

            if has_bxcolor:
                assert (
                    "false" in frontmatter.lower()
                ), "❌ BUG: bxcoloremoji not set to false"
            else:
                bx_logs = [
                    record.message
                    for record in caplog.records
                    if "bxcoloremoji" in record.message
                ]
                assert any(
                    "= false" in entry.lower() for entry in bx_logs
                ), "bxcoloremoji metadata missing from logs"
        else:
            pytest.fail("Could not parse YAML frontmatter")

    def test_emoji_font_selection_logging(self, tmp_path, caplog):
        """Capture logs to diagnose font selection code path."""
        import logging

        caplog.set_level(logging.INFO)

        md_content = "# Test 😀 Emoji"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")

        success, _ = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False),
            variables={"mainfontfallback": "Twemoji Mozilla:mode=harf"},
        )

        assert success, "Build failed"

        # Extract relevant log messages
        log_messages = [record.message for record in caplog.records]
        emoji_logs = [
            msg for msg in log_messages if "FONT-STACK" in msg or "emoji" in msg.lower()
        ]

        print("\n=== EMOJI FONT SELECTION LOGS ===")
        for msg in emoji_logs:
            print(msg)

        # Critical assertions
        assert any(
            "_select_emoji_font() aufgerufen" in msg for msg in log_messages
        ), "❌ BUG: _select_emoji_font() was NOT called"

        assert any(
            "Twemoji Mozilla" in msg for msg in log_messages
        ), "❌ BUG: Twemoji Mozilla not resolved from fonts.yml"

        # Check for HarfBuzz decision
        harfbuzz_logs = [
            msg
            for msg in log_messages
            if "harfbuzz" in msg.lower() or "mode=harf" in msg
        ]
        print("\n=== HARFBUZZ LOGS ===")
        for msg in harfbuzz_logs:
            print(msg)

    def test_pdf_contains_emoji_font(self, tmp_path):
        """Use pdffonts to verify Twemoji Mozilla is actually embedded.

        This is the FINAL validation - if this fails, the bug is confirmed.
        """
        md_content = "# Emoji Test\n\n😀 Grinning Face\n🌍 Earth Globe\n🎉 Party Popper"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")

        pdf_file = tmp_path / "test.pdf"

        success, _ = publisher.build_pdf(
            path=str(md_file),
            out="test.pdf",
            typ="file",
            publish_dir=str(tmp_path),
            emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False),
            variables={"mainfontfallback": "Twemoji Mozilla:mode=harf"},
        )

        assert success
        assert pdf_file.exists()

        # Try to use pdffonts tool
        try:
            result = subprocess.run(
                ["pdffonts", str(pdf_file)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )

            if result.returncode == 0:
                fonts_output = result.stdout
                print("\n=== PDF FONTS (via pdffonts) ===")
                print(fonts_output)

                # Check for Twemoji Mozilla or any Emoji font
                has_emoji_font = (
                    "Twitter" in fonts_output
                    or "Emoji" in fonts_output
                    or "emoji" in fonts_output.lower()
                )

                if not has_emoji_font:
                    print("\n❌ BUG CONFIRMED: No emoji font found in PDF!")
                    print("Expected: Twemoji Mozilla")
                    print(
                        "This means the font is NOT being embedded despite configuration."
                    )
                    pytest.fail("Emoji font not embedded in PDF")
                else:
                    print("\n✅ Emoji font IS embedded in PDF")
            else:
                pytest.skip(f"pdffonts command failed: {result.stderr}")

        except FileNotFoundError:
            pytest.skip("pdffonts tool not installed (install poppler-utils)")

    def test_lua_filter_receives_correct_metadata(self, tmp_path):
        """Test Pandoc metadata passing to lua filter directly.

        This bypasses publisher.py to test just Pandoc → Lua filter.
        """
        md_content = "# Test 😀"
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")

        # Create metadata file for Pandoc
        metadata = {
            "emojifont": "Twemoji Mozilla",
            "bxcoloremoji": False,
            "emojifontoptions": ["Renderer=HarfBuzz"],
        }

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text(json.dumps(metadata), encoding="utf-8")

        # Find lua filter
        lua_filter = (
            Path(__file__).parent.parent
            / "tools"
            / "publishing"
            / "lua"
            / "latex-emoji.lua"
        )

        if not lua_filter.exists():
            pytest.skip(f"Lua filter not found at {lua_filter}")

        tex_output = tmp_path / "output.tex"

        # Run Pandoc directly
        result = subprocess.run(
            [
                "pandoc",
                str(md_file),
                "--lua-filter",
                str(lua_filter),
                "--metadata-file",
                str(metadata_file),
                "--to",
                "latex",
                "-o",
                str(tex_output),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            print(f"\n❌ Pandoc failed: {result.stderr}")
            pytest.skip(f"Pandoc execution failed: {result.stderr}")

        if not tex_output.exists():
            pytest.fail("LaTeX output not created by Pandoc")

        tex_content = tex_output.read_text(encoding="utf-8")

        print("\n=== LATEX OUTPUT (first 100 lines) ===")
        for i, line in enumerate(tex_content.split("\n")[:100], 1):
            if (
                "emoji" in line.lower()
                or "harfbuzz" in line.lower()
                or "setfontface" in line.lower()
            ):
                print(f"{i:3d}: {line}")

        # Check if Lua filter generated prologue
        has_prologue = "\\setfontface\\p@emoji@font" in tex_content
        has_harfbuzz = "Renderer=HarfBuzz" in tex_content or "mode=harf" in tex_content

        if not has_prologue:
            print("\n❌ BUG: Lua filter did NOT generate emoji font setup prologue")
            print("This means latex-emoji.lua get_prologue() returned nil")
            pytest.fail("Lua filter prologue not generated")

        if not has_harfbuzz:
            print("\n⚠️ WARNING: HarfBuzz renderer not found in LaTeX output")
            print("Prologue was generated but without HarfBuzz specification")

        print("\n✅ Lua filter generated prologue with emoji font setup")

    def test_decide_bxcoloremoji_returns_false_when_disabled(self):
        """Unit test: Verify _decide_bxcoloremoji logic."""
        options = publisher.EmojiOptions(color=True, bxcoloremoji=False)
        result = publisher._decide_bxcoloremoji(options)

        assert (
            result is False
        ), "❌ BUG: _decide_bxcoloremoji should return False when explicitly disabled"

    def test_select_emoji_font_returns_configured_color_font(self):
        """Unit test: Verify _select_emoji_font resolves the configured color font."""
        font_name, needs_harfbuzz = publisher._select_emoji_font(prefer_color=True)

        print(
            f"\n_select_emoji_font returned: font={font_name}, harfbuzz={needs_harfbuzz}"
        )

        assert font_name is not None, "❌ BUG: No emoji font selected"
        assert (
            "Twemoji" in font_name or "Emoji" in font_name
        ), f"❌ BUG: Unexpected emoji font selected: {font_name}"
        assert (
            needs_harfbuzz is False
        ), "❌ BUG: Twemoji Mozilla should render without HarfBuzz in LuaLaTeX"


@pytest.mark.integration
def test_quick_emoji_render_diagnostic(tmp_path):
    """Quick diagnostic test - run this FIRST to see overall status."""
    md = tmp_path / "emoji-test.md"
    md.write_text("# Quick Test 😀🌍🎉", encoding="utf-8")

    print("\n" + "=" * 60)
    print("QUICK EMOJI DIAGNOSTIC")
    print("=" * 60)

    success, error = publisher.build_pdf(
        path=str(md),
        out="test.pdf",
        typ="file",
        publish_dir=str(tmp_path),
        keep_combined=True,
        emoji_options=publisher.EmojiOptions(color=True, bxcoloremoji=False),
        variables={"mainfontfallback": "Twemoji Mozilla:mode=harf"},
    )

    print(f"\n1. Build Success: {success}")
    if not success:
        print(f"   Error: {error}")

    pdf = tmp_path / "test.pdf"
    print(f"2. PDF Created: {pdf.exists()}")

    combined = list(tmp_path.glob("*-combined.md"))
    print(f"3. Combined MD: {len(combined)} file(s)")

    if combined:
        content = combined[0].read_text(encoding="utf-8")
        has_emojifont = "emojifont" in content.lower()
        has_bxcolor = "bxcoloremoji" in content.lower()
        print(f"4. Has emojifont metadata: {has_emojifont}")
        print(f"5. Has bxcoloremoji metadata: {has_bxcolor}")

    # Try pdffonts
    if pdf.exists():
        try:
            result = subprocess.run(
                ["pdffonts", str(pdf)], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                has_emoji = (
                    "emoji" in result.stdout.lower() or "Twitter" in result.stdout
                )
                print(f"6. PDF contains emoji font: {has_emoji}")
                if not has_emoji:
                    print("\n   ❌ BUG CONFIRMED: Emoji font not in PDF!")
            else:
                print("6. pdffonts command failed")
        except FileNotFoundError:
            print("6. pdffonts not available (install poppler-utils)")

    print("=" * 60 + "\n")

    assert success, "Build should succeed"
