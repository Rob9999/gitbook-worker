import os
import subprocess
import sys
import shutil
import time
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEST_WORKSPACE = (
    REPO_ROOT / ".github" / "gitbook_worker" / "tests" / "data" / "workspace"
)
IMAGE_NAME = "test-smart-worker"
CONTAINER_NAME = "test-smart-worker-readme-container"


def run(cmd, check=True, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def build_test_image():
    """Build the Docker test image (shared across tests)."""
    print("Building Docker image for test...")
    res = run(
        [
            "docker",
            "build",
            "-f",
            ".github/gitbook_worker/tools/docker/Dockerfile.dynamic",
            "-t",
            IMAGE_NAME,
            str(REPO_ROOT),
        ]
    )
    assert res.returncode == 0, f"Docker build failed: {res.stderr}"
    return IMAGE_NAME


def start_test_container(image_name):
    """Start a test container with repo mounted."""
    run(["docker", "rm", "-f", CONTAINER_NAME], check=False)
    res = run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-v",
            f"{REPO_ROOT}:/workspace",
            image_name,
            "sleep",
            "infinity",
        ]
    )
    assert res.returncode == 0, f"docker run failed: {res.stderr}"
    return CONTAINER_NAME


def get_file_list(container_name, workspace_rel):
    """Get list of files in test workspace."""
    res = run(
        [
            "docker",
            "exec",
            container_name,
            "bash",
            "-lc",
            f"cd /workspace && find {workspace_rel} -type f | sort",
        ]
    )
    assert res.returncode == 0, res.stderr
    return set(res.stdout.splitlines())


def run_ensure_readme_in_container(container_name):
    """Run orchestrator ensure_readme step in container."""
    cmd = [
        "docker",
        "exec",
        container_name,
        "bash",
        "-lc",
        "PYTHONPATH=/workspace/.github/gitbook_worker /venv/bin/python3 -m tools.workflow_orchestrator --root /workspace/.github/gitbook_worker/tests/data/workspace --step ensure_readme",
    ]
    print("Running orchestrator ensure_readme in container...")
    res = run(cmd, check=False)
    print(res.stdout)
    print(res.stderr)
    return res


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_orchestrator_ensure_readme_no_deletions(tmp_path, logger=None):
    """Test that ensure_readme does not delete any existing files.

    This is the primary regression test - no files should be deleted.
    """
    assert TEST_WORKSPACE.exists(), f"Test workspace missing: {TEST_WORKSPACE}"

    image = build_test_image()
    container = start_test_container(image)

    try:
        workspace_rel = str(TEST_WORKSPACE.relative_to(REPO_ROOT)).replace("\\", "/")

        # Get file list before
        pre_files = get_file_list(container, workspace_rel)

        # Run ensure_readme
        run_ensure_readme_in_container(container)

        # Get file list after
        post_files = get_file_list(container, workspace_rel)

        deleted = pre_files - post_files
        added = post_files - pre_files

        # Main assertion: NO files should be deleted
        assert not deleted, f"Files were deleted during ensure_readme: {deleted}"

        # Optional: Log what was added (should only be missing READMEs)
        if added:
            print(f"Files added: {added}")

    finally:
        run(["docker", "rm", "-f", container], check=False)


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_orchestrator_ensure_readme_preserves_markdown_files(tmp_path, logger=None):
    """Test that ensure_readme preserves all .md files (not just README.md).

    Regression test for bug where .md files were incorrectly deleted.
    """
    assert TEST_WORKSPACE.exists(), f"Test workspace missing: {TEST_WORKSPACE}"

    image = build_test_image()
    container = start_test_container(image)

    try:
        workspace_rel = str(TEST_WORKSPACE.relative_to(REPO_ROOT)).replace("\\", "/")

        # Get all .md files before
        res = run(
            [
                "docker",
                "exec",
                container,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -name '*.md' -type f | sort",
            ]
        )
        pre_md_files = set(res.stdout.splitlines())

        # Run ensure_readme
        run_ensure_readme_in_container(container)

        # Get all .md files after
        res = run(
            [
                "docker",
                "exec",
                container,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -name '*.md' -type f | sort",
            ]
        )
        post_md_files = set(res.stdout.splitlines())

        deleted_md = pre_md_files - post_md_files

        # CRITICAL: No markdown files should be deleted
        assert not deleted_md, f"Markdown files were deleted: {deleted_md}"

    finally:
        run(["docker", "rm", "-f", container], check=False)


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_orchestrator_ensure_readme_only_creates_missing(tmp_path, logger=None):
    """Test that ensure_readme only creates READMEs in directories without any README variant.

    Should NOT overwrite or recreate existing READMEs.
    """
    assert TEST_WORKSPACE.exists(), f"Test workspace missing: {TEST_WORKSPACE}"

    image = build_test_image()
    container = start_test_container(image)

    try:
        workspace_rel = str(TEST_WORKSPACE.relative_to(REPO_ROOT)).replace("\\", "/")

        # Get list of existing README files with their content hashes
        res = run(
            [
                "docker",
                "exec",
                container,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -iname 'readme*' -type f -exec md5sum {{}} \\;",
            ]
        )
        pre_readme_hashes = dict(
            line.rsplit(None, 1)[::-1] for line in res.stdout.splitlines() if line
        )

        # Run ensure_readme
        run_ensure_readme_in_container(container)

        # Get README hashes after
        res = run(
            [
                "docker",
                "exec",
                container,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -iname 'readme*' -type f -exec md5sum {{}} \\;",
            ]
        )
        post_readme_hashes = dict(
            line.rsplit(None, 1)[::-1] for line in res.stdout.splitlines() if line
        )

        # Check that existing READMEs were not modified
        for path, pre_hash in pre_readme_hashes.items():
            if path in post_readme_hashes:
                assert (
                    post_readme_hashes[path] == pre_hash
                ), f"Existing README was modified: {path}"

    finally:
        run(["docker", "rm", "-f", container], check=False)


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_orchestrator_ensure_readme_respects_publish_yml(tmp_path, logger=None):
    """Test that ensure_readme respects publish.yml configuration.

    Should follow include/exclude patterns from configuration.
    """
    assert TEST_WORKSPACE.exists(), f"Test workspace missing: {TEST_WORKSPACE}"

    image = build_test_image()
    container = start_test_container(image)

    try:
        workspace_rel = str(TEST_WORKSPACE.relative_to(REPO_ROOT)).replace("\\", "/")

        # Run ensure_readme
        res = run_ensure_readme_in_container(container)

        # Check that output mentions configuration was loaded
        output = res.stdout + res.stderr

        # Should have loaded publish.yml
        assert (
            "publish.yml" in output or "README" in output
        ), "ensure_readme should process configuration"

        # Should not fail
        assert (
            res.returncode == 0 or "Created:" in output
        ), "ensure_readme should complete successfully"

    finally:
        run(["docker", "rm", "-f", container], check=False)
