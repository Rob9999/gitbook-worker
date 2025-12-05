"""
Tests for the proof-of-concept package.

In the full implementation, this would be the entire test suite
from .github/gitbook_worker/tests/
"""

import pytest
from erda_workflow_tools import hello, __version__


def test_greet():
    """Test the greet function."""
    result = hello.greet("Test")
    assert result == "Hello, Test!"


def test_greet_with_empty_string():
    """Test greeting with empty string."""
    result = hello.greet("")
    assert result == "Hello, !"


def test_get_version():
    """Test version retrieval."""
    version = hello.get_version()
    assert version == __version__
    assert version == "0.1.0"


def test_package_imports():
    """Test that package can be imported."""
    import erda_workflow_tools

    assert hasattr(erda_workflow_tools, "__version__")
    assert hasattr(erda_workflow_tools, "hello")


def test_cli_main():
    """Test CLI entry point."""
    from erda_workflow_tools.__main__ import main

    exit_code = main()
    assert exit_code == 0
