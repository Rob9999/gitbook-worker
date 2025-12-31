import importlib.util
import pathlib

import pytest


def _load_module(module_name: str, module_path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError("Failed to create module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_import_guard_raises_for_missing_assets(tmp_path, monkeypatch):
    """Simulate a stray package without assets and expect a guard failure."""

    monkeypatch.setenv("GITBOOK_WORKER_PRINT_PATHS", "0")

    source_path = pathlib.Path(__file__).resolve().parents[1] / "gh_paths.py"
    fake_root = tmp_path / "fake_pkg"
    pkg_dir = fake_root / "gitbook_worker"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("")
    fake_gh_paths = pkg_dir / "gh_paths.py"
    fake_gh_paths.write_text(source_path.read_text())

    with pytest.raises(RuntimeError) as excinfo:
        _load_module("fake_gitbook_worker.gh_paths", fake_gh_paths)

    message = str(excinfo.value)
    assert "expected package assets not found" in message
    assert str(fake_root) in message


def test_prints_can_be_suppressed(capsys, monkeypatch):
    monkeypatch.setenv("GITBOOK_WORKER_PRINT_PATHS", "0")

    source_path = pathlib.Path(__file__).resolve().parents[1] / "gh_paths.py"
    _load_module("gh_paths_no_print", source_path)

    captured = capsys.readouterr()
    assert captured.out == ""
