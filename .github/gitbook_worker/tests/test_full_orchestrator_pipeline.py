"""Full end-to-end orchestrator pipeline test to catch README deletion bug.

This test runs the COMPLETE default profile orchestrator pipeline (not just ensure_readme)
to catch interactions between different steps that might cause file deletions.
"""

import subprocess
import shutil
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEST_WORKSPACE = (
    REPO_ROOT / ".github" / "gitbook_worker" / "tests" / "data" / "workspace"
)
IMAGE_NAME = "test-full-orchestrator"
CONTAINER_NAME = "test-full-orchestrator-container"


def run(cmd, check=True, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
@pytest.mark.slow
def test_full_orchestrator_pipeline_no_deletions():
    """Run the FULL orchestrator pipeline and verify no content files are deleted.

    This tests the complete workflow including:
    - check_if_to_publish
    - ensure_readme
    - update_citation
    - converter
    - engineering-document-formatter
    - publisher

    The bug might be caused by interactions between these steps.
    """
    import shutil

    assert TEST_WORKSPACE.exists(), f"Test workspace missing: {TEST_WORKSPACE}"

    # Build image
    print("Building Docker image for full pipeline test...")
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

    # Cleanup old container
    run(["docker", "rm", "-f", CONTAINER_NAME], check=False)

    # Start container
    res = run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-v",
            f"{REPO_ROOT}:/workspace",
            IMAGE_NAME,
            "sleep",
            "infinity",
        ]
    )
    assert res.returncode == 0, f"docker run failed: {res.stderr}"

    try:
        workspace_rel = str(TEST_WORKSPACE.relative_to(REPO_ROOT)).replace("\\", "/")

        # Get pre-run file list
        pre = run(
            [
                "docker",
                "exec",
                CONTAINER_NAME,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -type f -name '*.md' | sort",
            ]
        )
        pre_md_files = set(pre.stdout.splitlines())

        print(f"Found {len(pre_md_files)} .md files before pipeline")

        # Run FULL orchestrator pipeline with default profile
        cmd = [
            "docker",
            "exec",
            CONTAINER_NAME,
            "bash",
            "-lc",
            "PYTHONPATH=/workspace/.github/gitbook_worker /venv/bin/python3 -m tools.workflow_orchestrator "
            "--root /workspace/.github/gitbook_worker/tests/data/workspace "
            "--profile default "
            "--dry-run",  # Use dry-run to be safe
        ]
        print("Running FULL orchestrator pipeline in container...")
        res = run(cmd, check=False)
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)

        # Get post-run file list
        post = run(
            [
                "docker",
                "exec",
                CONTAINER_NAME,
                "bash",
                "-lc",
                f"cd /workspace && find {workspace_rel} -type f -name '*.md' | sort",
            ]
        )
        post_md_files = set(post.stdout.splitlines())

        print(f"Found {len(post_md_files)} .md files after pipeline")

        deleted_md = pre_md_files - post_md_files
        added_md = post_md_files - pre_md_files

        if deleted_md:
            print(f"DELETED FILES ({len(deleted_md)}):")
            for f in sorted(deleted_md):
                print(f"  - {f}")

        if added_md:
            print(f"ADDED FILES ({len(added_md)}):")
            for f in sorted(added_md):
                print(f"  + {f}")

        # CRITICAL ASSERTION: No markdown files should be deleted
        assert not deleted_md, (
            f"{len(deleted_md)} markdown files were deleted during full pipeline:\n"
            + "\n".join(f"  - {f}" for f in sorted(deleted_md))
        )

    finally:
        run(["docker", "rm", "-f", CONTAINER_NAME], check=False)
