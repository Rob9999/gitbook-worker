"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import importlib
import json
import logging
import pathlib
import subprocess
import sys
import os
from collections.abc import Iterator
from functools import lru_cache

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKER_DIR = REPO_ROOT / "gitbook_worker"
for _path in (WORKER_DIR, REPO_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


os.environ.setdefault("GITBOOK_WORKER_DISABLE_FONT_STORAGE_BOOTSTRAP", "1")


from . import GH_TEST_ARTIFACTS_DIR, GH_TEST_LOGS_DIR, GH_TEST_OUTPUT_DIR
from gitbook_worker.tools.logging_config import make_specific_logger
from gitbook_worker.tools.utils.smart_content import load_content_config
from gitbook_worker.tools.utils.smart_manifest import (
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)


def _ensure(pkg: str) -> None:
    """Install ``pkg`` with pip if it cannot be imported."""
    try:
        importlib.import_module(pkg)
    except ImportError:  # pragma: no cover - only runs when dependency missing
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


for _pkg in ["pyyaml", "tabulate", "emoji", "beautifulsoup4"]:
    _ensure(_pkg)


@pytest.fixture(scope="session", autouse=True)
def initialize_luaotfload_cache() -> None:
    """
    Ensure luaotfload font database is initialized before any tests run.

    This fixture runs once per test session and updates the LuaTeX font cache.
    If luaotfload-tool is not available, tests requiring it will be skipped.

    Note: This fixture is autouse=True, so it runs automatically for all tests.
    Individual tests can still skip if fonts are missing.
    """
    try:
        result = subprocess.run(
            ["luaotfload-tool", "--update", "--force"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            # Don't fail the entire test run, just log warning
            # Tests that need fonts will handle missing cache individually
            logging.getLogger("conftest").warning(
                f"Font cache initialization failed: {result.stderr}"
            )
    except FileNotFoundError:
        logging.getLogger("conftest").warning(
            "luaotfload-tool not available in test environment"
        )
    except subprocess.TimeoutExpired:
        logging.getLogger("conftest").warning("Font cache initialization timed out")


@pytest.fixture
def logger(request: pytest.FixtureRequest) -> Iterator[logging.Logger]:
    """Provide a test-specific logger that writes to GH_TEST_LOGS_DIR."""
    log_path = GH_TEST_LOGS_DIR / f"{request.node.name}.log"
    with make_specific_logger(
        request.node.name,
        log_path=log_path,
        rootless=False,
    ) as log:
        yield log


@pytest.fixture
def output_dir(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return a unique output directory for the current test."""
    path: pathlib.Path = GH_TEST_OUTPUT_DIR / request.node.name
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def artifact_dir(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return a unique artifacts directory for the current test."""
    path: pathlib.Path = GH_TEST_ARTIFACTS_DIR / request.node.name
    path.mkdir(parents=True, exist_ok=True)
    return path


# ========================= Path Resolution Fixtures ========================= #


def _find_repo_root(start_path: pathlib.Path | None = None) -> pathlib.Path:
    """Find the repository root using the shared smart-manifest helper."""

    base = start_path or pathlib.Path(__file__).resolve()
    return detect_repo_root(base)


@lru_cache(maxsize=1)
def _default_language_root(repo_root: pathlib.Path) -> pathlib.Path:
    """Return the local path for the default language configured in content.yaml."""

    config = load_content_config(
        cwd=repo_root, repo_root=repo_root, allow_missing=False
    )
    entry = config.get(config.default_id)
    if not entry.is_local:
        raise RuntimeError(
            f"Default language '{entry.id}' is not local; tests expect a local baseline"
        )
    root = entry.resolve_path(repo_root)
    if not root.exists():
        raise FileNotFoundError(
            f"Language root {root} (id={entry.id}) not found; sync repo before running tests"
        )
    return root


def _find_publish_yml(repo_root: pathlib.Path) -> pathlib.Path:
    """Resolve the publish manifest inside the default language root."""

    language_root = _default_language_root(repo_root)
    manifest = language_root / "publish.yml"
    if manifest.exists():
        return manifest

    # Fallback to smart manifest rules for backwards compatibility (e.g. test fixtures)
    try:
        return resolve_manifest(explicit=None, cwd=repo_root, repo_root=repo_root)
    except SmartManifestError as exc:  # pragma: no cover - mirrors runtime behaviour
        raise FileNotFoundError(str(exc)) from exc


def _find_book_json(start_path: pathlib.Path) -> pathlib.Path:
    """Locate book.json using the default language root before falling back."""

    try:
        language_root = _default_language_root(start_path)
    except Exception:
        language_root = None

    if language_root is not None:
        candidate = language_root / "book.json"
        if candidate.exists():
            return candidate.resolve()

    # Fallback to search up the tree (used by isolated test fixtures)
    for candidate in [start_path, *start_path.parents]:
        book_json = candidate / "book.json"
        if book_json.exists():
            return book_json.resolve()

    return (start_path / "book.json").resolve()


def _get_content_root(book_json_path: pathlib.Path) -> pathlib.Path:
    """Extract the content root directory from book.json.

    This matches the logic in gitbook_style.py's _build_summary_context().
    """
    if not book_json_path.exists():
        return book_json_path.parent

    with book_json_path.open("r", encoding="utf-8") as f:
        book_data = json.load(f)

    root_value = book_data.get("root", ".")
    # Remove trailing slash if present
    root_value = root_value.rstrip("/")

    if not root_value or root_value == ".":
        return book_json_path.parent

    return (book_json_path.parent / root_value).resolve()


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    """Return the repository root directory."""
    return _find_repo_root()


@pytest.fixture(scope="session")
def publish_yml_path(repo_root: pathlib.Path) -> pathlib.Path:
    """Return the path to publish.yml (or publish.yaml)."""
    return _find_publish_yml(repo_root)


@pytest.fixture(scope="session")
def book_json_path(repo_root: pathlib.Path) -> pathlib.Path:
    """Return the path to book.json."""
    return _find_book_json(repo_root)


@pytest.fixture(scope="session")
def book_json_data(book_json_path: pathlib.Path) -> dict:
    """Return the parsed book.json data."""
    with book_json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def content_root(book_json_path: pathlib.Path) -> pathlib.Path:
    """Return the content root directory from book.json configuration.

    For integration tests, this returns the actual repo content directory.
    Individual tests should use their own test data fixtures if they need
    controlled test content instead of the full repository content.
    """
    return _get_content_root(book_json_path)


@pytest.fixture
def test_content_root() -> pathlib.Path:
    """Return the test data directory for controlled test scenarios.

    Use this fixture instead of content_root when tests need isolated
    test data rather than the full repository content directory.
    """
    return pathlib.Path(__file__).parent / "data"
