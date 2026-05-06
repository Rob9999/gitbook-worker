from configparser import ConfigParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_package_discovery_excludes_test_packages():
    config = ConfigParser()
    config.read(REPO_ROOT / "setup.cfg", encoding="utf-8")

    exclude_value = config.get("options.packages.find", "exclude")
    excludes = {line.strip() for line in exclude_value.splitlines() if line.strip()}

    assert "gitbook_worker.tests" in excludes
    assert "gitbook_worker.tests.*" in excludes


def test_manifest_prunes_release_noise():
    manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "prune gitbook_worker/tests" in manifest
    assert "global-exclude *.py[cod]" in manifest
    assert "global-exclude __pycache__/*" in manifest


def test_manifest_includes_docker_build_inputs():
    manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include gitbook_worker/tools/docker/Dockerfile" in manifest
    assert "include gitbook_worker/tools/docker/Dockerfile.dynamic" in manifest
    assert "include gitbook_worker/tools/docker/Dockerfile.python" in manifest
    assert "include gitbook_worker/tools/requirements.txt" in manifest
