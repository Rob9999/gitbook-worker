"""Unit tests for LaTeX escaping utilities.

These tests verify the correct escaping of LaTeX special characters
without requiring Pandoc or LaTeX installation.
"""

import pytest


def _escape_latex_simple(value: str) -> str:
    """Escape LaTeX special characters for use in LaTeX documents.

    This is a reference implementation showing how LaTeX special characters
    should be escaped. The production code in publisher.py uses a similar
    approach via the _escape_latex() function.

    Args:
        value: String containing potential LaTeX special characters

    Returns:
        String with LaTeX special characters properly escaped
    """
    if not value:
        return value

    # Replace backslash first
    esc = value.replace("\\", "\\textbackslash{}")

    # Replace other special characters
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    for k, v in replacements.items():
        esc = esc.replace(k, v)

    return esc


# ============================================================================
# Unit Tests
# ============================================================================


@pytest.mark.unit
def test_escape_latex_simple_ampersand():
    r"""Test that ampersand is escaped with single backslash, not double.

    This verifies the escaping produces \& not \\& which would be double-escaped.
    """
    # Test single ampersand
    result = _escape_latex_simple("Title & Subtitle")
    assert (
        result == r"Title \& Subtitle"
    ), f"Expected 'Title \\& Subtitle' but got '{result}'"
    # Verify it's a single backslash (2 chars: \ and &)
    assert (
        result.count("\\") == 1
    ), f"Should have exactly 1 backslash, but has {result.count(chr(92))}"

    # Test the actual title from the test file
    result = _escape_latex_simple("Complex Document & Test File")
    assert result == r"Complex Document \& Test File"
    # Should NOT be double-escaped like \\&
    assert "\\\\&" not in result, "Should not contain double-escaped backslash"
    assert r"\&" in result, "Should contain single-escaped ampersand"


@pytest.mark.unit
def test_escape_latex_simple_all_special_chars():
    """Test escaping of all LaTeX special characters."""
    test_cases = [
        ("A & B", r"A \& B"),
        ("100%", r"100\%"),
        ("$100", r"\$100"),
        ("#hashtag", r"\#hashtag"),
        ("test_var", r"test\_var"),
        ("{key}", r"\{key\}"),
        ("~home", r"\textasciitilde{}home"),
        ("x^2", r"x\textasciicircum{}2"),
    ]

    for input_str, expected in test_cases:
        result = _escape_latex_simple(input_str)
        assert (
            result == expected
        ), f"For '{input_str}': expected '{expected}', got '{result}'"


@pytest.mark.unit
def test_escape_latex_simple_combined():
    """Test escaping of multiple special characters in one string."""
    input_str = "Kapitel 2: Spezielle Zeichen & Tests (100% #1)"
    result = _escape_latex_simple(input_str)

    # Should contain escaped versions
    assert r"\&" in result
    assert r"\%" in result
    assert r"\#" in result

    # Should NOT contain double-escaped versions
    assert "\\\\&" not in result
    assert "\\\\%" not in result
    assert "\\\\#" not in result


@pytest.mark.unit
def test_escape_latex_empty_string():
    """Test that empty strings are handled gracefully."""
    assert _escape_latex_simple("") == ""
    assert _escape_latex_simple(None) is None


@pytest.mark.unit
def test_escape_latex_no_special_chars():
    """Test that strings without special characters remain unchanged."""
    test_str = "Simple Title Without Special Characters"
    assert _escape_latex_simple(test_str) == test_str
