#!/usr/bin/env python3
"""Common directory paths for tests."""

import pathlib

# Absolute .github test Directory
GH_TESTS_DIR = pathlib.Path(__file__).parent

# Absolute Temporary directory for tests
GH_TEST_TMP_DIR = pathlib.Path(__file__).parent / "tmp"
GH_TEST_TMP_DIR.mkdir(exist_ok=True, mode=0o755)

# Logs
GH_TEST_LOGS_DIR = GH_TEST_TMP_DIR / "logs"
GH_TEST_LOGS_DIR.mkdir(exist_ok=True, mode=0o755)

# Output
GH_TEST_OUTPUT_DIR = GH_TEST_TMP_DIR / "output"
GH_TEST_OUTPUT_DIR.mkdir(exist_ok=True, mode=0o755)

# Artifacts
GH_TEST_ARTIFACTS_DIR = GH_TEST_TMP_DIR / "artifacts"
GH_TEST_ARTIFACTS_DIR.mkdir(exist_ok=True, mode=0o755)

# Test Data
GH_TEST_DATA_DIR = pathlib.Path(__file__).parent / "data"
GH_TEST_DATA_DIR.mkdir(exist_ok=True, mode=0o755)
