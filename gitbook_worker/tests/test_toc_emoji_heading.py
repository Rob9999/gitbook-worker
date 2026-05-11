"""Regression tests for emoji rendering in PDF Table of Contents.

Issue: When headings contain emoji (e.g. ## 🇩🇪 DE - Germany), the emoji
disappear from the TOC / PDF bookmarks showing as '??' instead.

Root cause: latex-emoji.lua defined \\panEmoji in the document body
(doc.blocks[1]) but \\tableofcontents is rendered BEFORE $body$ in the
Pandoc default LaTeX template.  LaTeX writes \\panEmoji{…} to the .toc
file during the first pass, but on the second pass \\tableofcontents
reads the .toc file before \\panEmoji is defined → undefined command.

Fix: Move the \\panEmoji definition from doc.blocks (body) into
meta['header-includes'] (preamble), so the command is defined before
\\begin{document} and available when \\tableofcontents processes .toc
entries.

---
version: "1.0.0"
date: 2025-07-13
history:
  - 1.0.0: Initial regression test for TOC emoji heading bug
"""

import logging
import pytest
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths to Lua filters under test
# ---------------------------------------------------------------------------
LUA_DIR = Path(__file__).parent.parent / "tools" / "publishing" / "lua"
EMOJI_SPAN_LUA = LUA_DIR / "emoji-span.lua"
TEXT_SYMBOLS_LUA = LUA_DIR / "text-symbols.lua"
URL_BREAKS_LUA = LUA_DIR / "url-breaks.lua"
LATEX_EMOJI_LUA = LUA_DIR / "latex-emoji.lua"

# ---------------------------------------------------------------------------
# Sample markdown with emoji in headings – flag emoji are the hardest case
# because they are composed of two Regional Indicator codepoints.
# ---------------------------------------------------------------------------
MD_WITH_EMOJI_HEADINGS = """\
# Introduction

Some introductory text.

## 🇩🇪 DE - Germany (Deutschland)

Content for Germany section.

## 🇫🇷 FR - France (Frankreich)

Content for France section.

## 🌍 Overview

Content for overview section.

### 😀 Sub-heading with smiley

More content here.
"""


def _check_pandoc_available():
    """Skip tests if pandoc is not on PATH."""
    try:
        subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("pandoc not available")


def _check_lua_filters():
    """Skip tests if Lua filters are missing."""
    if not EMOJI_SPAN_LUA.exists():
        pytest.skip(f"emoji-span.lua not found at {EMOJI_SPAN_LUA}")
    if not TEXT_SYMBOLS_LUA.exists():
        pytest.skip(f"text-symbols.lua not found at {TEXT_SYMBOLS_LUA}")
    if not URL_BREAKS_LUA.exists():
        pytest.skip(f"url-breaks.lua not found at {URL_BREAKS_LUA}")
    if not LATEX_EMOJI_LUA.exists():
        pytest.skip(f"latex-emoji.lua not found at {LATEX_EMOJI_LUA}")


def _run_pandoc_to_latex(
    md_content: str,
    tmp_path: Path,
    *,
    with_toc: bool = False,
    standalone: bool = True,
) -> str:
    """Run Pandoc with both emoji Lua filters and return LaTeX output.

    Parameters
    ----------
    md_content : str
        Markdown source with emoji in headings.
    tmp_path : Path
        pytest temporary directory.
    with_toc : bool
        Whether to pass ``--toc`` to Pandoc.
    standalone : bool
        Whether to pass ``-s`` (standalone) to Pandoc.

    Returns
    -------
    str
        The generated LaTeX source.

    Notes
    -----
    Metadata is passed via ``--metadata`` CLI flags instead of
    ``--metadata-file`` because Pandoc parses JSON/YAML metadata files
    into MetaInlines (splitting on spaces), causing
    ``tosingle("emojifont")`` in latex-emoji.lua to fail when the font
    name contains a space (e.g. "Twemoji Mozilla" → two Str elements).
    """
    md_file = tmp_path / "input.md"
    md_file.write_text(md_content, encoding="utf-8")

    tex_file = tmp_path / "output.tex"

    cmd = [
        "pandoc",
        str(md_file),
        "--lua-filter",
        str(EMOJI_SPAN_LUA),
        "--lua-filter",
        str(TEXT_SYMBOLS_LUA),
        "--lua-filter",
        str(URL_BREAKS_LUA),
        "--lua-filter",
        str(LATEX_EMOJI_LUA),
        # Pass metadata via --metadata flags (avoids MetaInlines splitting)
        "--metadata",
        "emojifont=Twemoji Mozilla",
        "--metadata",
        "bxcoloremoji=false",
        "--metadata",
        "emojifontoptions=Renderer=HarfBuzz",
        "--to",
        "latex",
        "-o",
        str(tex_file),
    ]
    if standalone:
        cmd.append("-s")
    if with_toc:
        cmd.append("--toc")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )

    if result.returncode != 0:
        pytest.fail(f"Pandoc failed (rc={result.returncode}): {result.stderr}")

    if not tex_file.exists():
        pytest.fail("Pandoc produced no output file")

    return tex_file.read_text(encoding="utf-8")


# ===========================================================================
# Tests
# ===========================================================================


@pytest.mark.integration
class TestTocEmojiHeading:
    """Verify that emoji in headings survive into the TOC correctly."""

    # -----------------------------------------------------------------------
    # Core regression test: \\panEmoji must be defined in the preamble
    # -----------------------------------------------------------------------
    def test_panemoji_defined_in_preamble_not_body(self, tmp_path):
        r"""CRITICAL: \\panEmoji MUST be defined in the preamble.

        Pandoc's default LaTeX template places \\tableofcontents BEFORE
        $body$.  If \\panEmoji is only defined inside the body, the TOC
        cannot render emoji → they appear as '??'.

        This test splits the LaTeX output at \\begin{document} and verifies
        that the \\panEmoji definition appears in the PREAMBLE part.
        """
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=True)

        # Split at \begin{document}
        if r"\begin{document}" not in tex:
            pytest.fail(
                r"\begin{document} not found – is Pandoc producing standalone output?"
            )

        preamble, body = tex.split(r"\begin{document}", maxsplit=1)

        # \\panEmoji must appear in preamble (header-includes)
        assert (
            r"\DeclareRobustCommand*{\panEmoji}" in preamble
            or r"\DeclareRobustCommand{\panEmoji}" in preamble
            or r"\newcommand*{\panEmoji}" in preamble
            or r"\renewcommand*{\panEmoji}" in preamble
        ), (
            "REGRESSION: \\panEmoji is NOT defined in the preamble.\n"
            "This means emoji in TOC headings will render as '??' because\n"
            "\\tableofcontents reads the .toc file before the body where\n"
            "\\panEmoji is currently (incorrectly) defined.\n\n"
            "--- Preamble (first 80 lines) ---\n" + "\n".join(preamble.split("\n")[:80])
        )

        # Also verify the emoji font face is set up in preamble
        assert (
            r"\setfontface" in preamble
        ), "\\setfontface for emoji font not found in preamble"

    # -----------------------------------------------------------------------
    # Verify \\panEmoji is NOT duplicated in body (it should ONLY be in
    # preamble after the fix)
    # -----------------------------------------------------------------------
    def test_panemoji_not_in_body_after_fix(self, tmp_path):
        r"""After fix: \\panEmoji should be in preamble only, not in body.

        Before the fix, \\panEmoji was ONLY in the body.  The fix moves it
        to header-includes.  Verify it does not remain in the body as well
        (duplicate definitions are harmless but untidy).
        """
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=True)

        _, body = tex.split(r"\begin{document}", maxsplit=1)

        # After the fix the body should NOT contain the panEmoji definition
        assert (
            r"\newcommand*{\panEmoji}" not in body
            and r"\DeclareRobustCommand*{\panEmoji}" not in body
        ), "\\panEmoji definition still present in body (should only be in preamble)"

    # -----------------------------------------------------------------------
    # Emoji headings must be wrapped in \\panEmoji{…}
    # -----------------------------------------------------------------------
    def test_emoji_headings_wrapped_in_panemoji(self, tmp_path):
        r"""Headings containing emoji must use \\panEmoji{…} wrapping."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(
            MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=False, standalone=False
        )

        # Flag emoji 🇩🇪 is composed of U+1F1E9 U+1F1EA
        assert r"\panEmoji{" in tex, (
            "No \\panEmoji{…} wrapping found in LaTeX output.\n"
            "emoji-span.lua or latex-emoji.lua did not process the emoji spans."
        )

    def test_text_checkbox_symbols_are_not_wrapped_as_emoji(self, tmp_path):
        r"""Checklist box symbols must stay in the text font fallback path."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(
            """\
# ✅ Checkliste

- ☐ Offen
- ☑ Erledigt
- ☒ Abgelehnt
""",
            tmp_path,
            with_toc=False,
            standalone=False,
        )

        assert r"\panEmoji{✅}" in tex
        assert r"\panEmoji{☐}" not in tex
        assert r"\panEmoji{☑}" not in tex
        assert r"\panEmoji{☒}" not in tex
        assert r"\erdaTextSymbol{☐}" in tex
        assert r"\erdaTextSymbol{☑}" in tex
        assert r"\erdaTextSymbol{☒}" in tex
        assert r"\item[$\square$]" not in tex
        assert r"\item[$\boxtimes$]" not in tex

    def test_visible_urls_are_rendered_with_breakable_url_macro(self, tmp_path):
        r"""Visible URL text must be emitted as \url{...} for line breaking."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(
            """\
# Quellen

Helberger et al. https://doi.org/10.1080/01972243.2017.1391919.

[https://decidim.org](https://decidim.org)
""",
            tmp_path,
            with_toc=False,
            standalone=False,
        )

        assert r"\url{https://doi.org/10.1080/01972243.2017.1391919}" in tex
        assert r"\url{https://decidim.org}" in tex
        assert r"\href{https://decidim.org}{https://decidim.org}" not in tex
        assert r"\href{https://decidim.org}{\url{" not in tex

    def test_visible_url_links_do_not_nest_url_inside_href(self, tmp_path):
        r"""Visible URL links must not emit \href{...}{\url{...}}."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(
            """\
# Quellen

[https://example.invalid/legal-content/DE/TXT/?uri=CELEX(2024)1234](https://example.invalid/legal-content/DE/TXT/?uri=CELEX(2024)1234) (Zugriff: 2026-05-11)
""",
            tmp_path,
            with_toc=False,
            standalone=False,
        )

        assert (
            r"\url{https://example.invalid/legal-content/DE/TXT/?uri=CELEX(2024)1234}"
            in tex
        )
        assert r"\href{https://example.invalid" not in tex

    def test_url_filter_keeps_access_marker_outside_url_macro(self, tmp_path):
        r"""A missing space before access metadata must not poison \url{...}."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(
            """\
# Quellen

Quelle https://example.invalid/legal-content/DE/TXT/?uri=CELEX(Zugriff: 2026-05-11)
""",
            tmp_path,
            with_toc=False,
            standalone=False,
        )

        assert r"\url{https://example.invalid/legal-content/DE/TXT/?uri=CELEX}" in tex
        assert (
            r"\url{https://example.invalid/legal-content/DE/TXT/?uri=CELEX(Zugriff"
            not in tex
        )
        assert "(Zugriff:" in tex

    # -----------------------------------------------------------------------
    # Prologue must contain the emoji font face setup
    # -----------------------------------------------------------------------
    def test_prologue_contains_font_setup(self, tmp_path):
        r"""The generated prologue must set up \\panEmojiFont."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=False)

        assert r"\setfontface\panEmojiFont" in tex or r"\p@emoji@font" in tex, (
            "Emoji font face setup not found in LaTeX output.\n"
            "get_prologue() in latex-emoji.lua may not have generated the block."
        )

        assert (
            "Twemoji Mozilla" in tex
        ), "Emoji font name 'Twemoji Mozilla' not found in LaTeX output."

    # -----------------------------------------------------------------------
    # With --toc, the prologue block should still be present
    # -----------------------------------------------------------------------
    def test_toc_mode_includes_prologue(self, tmp_path):
        r"""When --toc is active, the \\panEmoji definition must still be present."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=True)

        has_panemoji_def = (
            r"\DeclareRobustCommand*{\panEmoji}" in tex
            or r"\DeclareRobustCommand{\panEmoji}" in tex
            or r"\newcommand*{\panEmoji}" in tex
            or r"\renewcommand*{\panEmoji}" in tex
        )

        assert (
            has_panemoji_def
        ), "\\panEmoji definition missing entirely from LaTeX output with --toc."

    # -----------------------------------------------------------------------
    # Verify codepoint declarations for flag emoji
    # -----------------------------------------------------------------------
    def test_flag_emoji_codepoints_declared(self, tmp_path):
        r"""Regional Indicator codepoints for flag emoji must be declared."""
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=False)

        # 🇩🇪 = U+1F1E9 U+1F1EA  →  "1F1E9" and "1F1EA" in ltjdefcharrange
        assert (
            "1F1E9" in tex
        ), "Regional Indicator U+1F1E9 (D) not declared in codepoint list"
        assert (
            "1F1EA" in tex
        ), "Regional Indicator U+1F1EA (E) not declared in codepoint list"

    # -----------------------------------------------------------------------
    # Template ordering sanity check
    # -----------------------------------------------------------------------
    def test_toc_before_body_in_standalone(self, tmp_path):
        r"""Confirm that \\tableofcontents appears before the emoji body content.

        This is a sanity check that the Pandoc template ordering is what
        we expect.  If this fails, the template has changed and the fix
        strategy may need revisiting.
        """
        _check_pandoc_available()
        _check_lua_filters()

        tex = _run_pandoc_to_latex(MD_WITH_EMOJI_HEADINGS, tmp_path, with_toc=True)

        toc_pos = tex.find(r"\tableofcontents")
        if toc_pos == -1:
            # Some Pandoc versions use \setcounter{tocdepth} but no explicit \tableofcontents
            # in that case the test is not applicable
            pytest.skip("\\tableofcontents not found in standalone output")

        # Find first occurrence of \panEmoji{ in body text (heading usage)
        panemoji_usage_pos = tex.find(r"\panEmoji{")
        if panemoji_usage_pos == -1:
            pytest.fail("No \\panEmoji{…} usage found in output")

        assert toc_pos < panemoji_usage_pos, (
            "Expected \\tableofcontents to appear before \\panEmoji{…} usage.\n"
            "This confirms that the definition must be in the preamble."
        )
