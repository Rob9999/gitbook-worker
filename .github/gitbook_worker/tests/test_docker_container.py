import os
import pathlib
import shutil
import subprocess
import time
import datetime

import pytest

import sys

try:
    from gh_paths import GH_TOOLS_DIR, REPO_ROOT, GH_DOCKER_DIR
except ImportError:
    print(
        "Failed to gather directories from python tree. Falling back to manual resolution."
    )
    REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
    GH_TOOLS_DIR = REPO_ROOT / ".github" / "tools"
    GH_DOCKER_DIR = GH_TOOLS_DIR / "docker"
    print("REPO_ROOT :", REPO_ROOT)
    print("GH_TOOLS_DIR :", GH_TOOLS_DIR)
    print("GH_DOCKER_DIR :", GH_DOCKER_DIR)
from . import GH_TEST_LOGS_DIR

IMAGE_NAME = "erda-smart-worker-test"
CONTAINER_NAME = "erda-smart-worker-test-container"


def log_to_logger(logger, message, stdout=None, stderr=None):
    """Write a message and optional command output to the logger."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"[{timestamp}] {message}"]
    if stdout:
        parts.append("STDOUT:")
        parts.append(
            stdout
            if isinstance(stdout, str)
            else stdout.decode("utf-8", errors="replace")
        )
    if stderr:
        parts.append("STDERR:")
        parts.append(
            stderr
            if isinstance(stderr, str)
            else stderr.decode("utf-8", errors="replace")
        )
    parts.append("-" * 80)
    logger.info("\n".join(parts))


def run_docker_command(cmd, check=True, logger=None, **kwargs):
    """Run a docker command with proper error handling and logging."""
    if logger:
        log_to_logger(logger, f"Running command: {' '.join(cmd)}")

    # Set encoding for subprocess output
    if sys.platform == "win32":
        kwargs["encoding"] = "utf-8"
        os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(cmd, capture_output=True, **kwargs)

        # Handle output encoding
        stdout = (
            result.stdout.decode("utf-8", errors="replace")
            if isinstance(result.stdout, bytes)
            else result.stdout
        )
        stderr = (
            result.stderr.decode("utf-8", errors="replace")
            if isinstance(result.stderr, bytes)
            else result.stderr
        )

        if logger:
            log_to_logger(
                logger,
                f"Command completed with return code: {result.returncode}",
                stdout=stdout,
                stderr=stderr,
            )

        result.stdout = stdout
        result.stderr = stderr

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                stdout,
                stderr,
            )

        return result
    except subprocess.CalledProcessError as e:
        msg = f"Docker command failed: {' '.join(cmd)}"
        print(msg)
        error_output = (
            e.stderr
            if isinstance(e.stderr, str)
            else e.stderr.decode("utf-8", errors="replace")
        )
        print(f"Error output: {error_output}")
        if logger:
            log_to_logger(logger, msg, stderr=e.stderr)
        if check:
            raise
        return e


def test_run_github_tests_in_docker(output_dir, artifact_dir, logger, request):
    """Run the test suite inside the project's Docker container."""
    if os.getenv("INSIDE_DOCKER"):
        pytest.skip("running inside container")

    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")

    logger.info("Starting Docker container test")

    # Paths
    docker_dir = GH_DOCKER_DIR
    logger.info(f"Docker directory: {docker_dir}")
    req_dir = GH_TOOLS_DIR
    logger.info(f"Requirements directory: {req_dir}")

    assert docker_dir.exists(), f"Missing {docker_dir}"
    assert req_dir.exists(), f"Missing {req_dir}"

    # Check if Docker daemon is running
    result = run_docker_command(["docker", "info"], check=False, logger=logger)
    if result.returncode != 0:
        logger.info("Docker daemon is not running, skipping test")
        pytest.skip("docker daemon is not running")

    logger.info(f"Removing existing docker container {CONTAINER_NAME}...")
    # Cleanup any existing container
    run_docker_command(
        ["docker", "rm", "-f", CONTAINER_NAME], check=False, logger=logger
    )

    # Build fresh image using Dockerfile.dynamic (smart configuration)
    logger.info(
        f"Preparing to build Docker image {IMAGE_NAME} with Dockerfile.dynamic..."
    )

    # No need to copy requirements - Dockerfile.dynamic handles this automatically
    print("\nBuilding Docker image with smart configuration...")
    run_docker_command(
        [
            "docker",
            "build",
            "-f",
            ".github/gitbook_worker/tools/docker/Dockerfile.dynamic",
            "-t",
            IMAGE_NAME,
            str(REPO_ROOT),
        ],
        logger=logger,
    )

    print("\nStarting container...")
    run_docker_command(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-v",
            f"{REPO_ROOT}:/workspace",
            "-e",
            "PYTHONPATH=/workspace/.github/gitbook_worker",
            "-e",
            "GITHUB_TOOLS=/workspace/.github/gitbook_worker/tools",
            IMAGE_NAME,
            "sleep",
            "infinity",
        ],
        logger=logger,
    )

    # Give container a moment to start up
    time.sleep(2)
    logger.info("Container started, waiting 2 seconds before running tests")

    print("\nRunning tests in container...")
    result = run_docker_command(
        [
            "docker",
            "exec",
            "-e",
            "INSIDE_DOCKER=1",
            "-e",
            "PYTHONPATH=/workspace",
            "-e",
            "PYTHONIOENCODING=utf-8",
            "-e",
            "LC_ALL=C.UTF-8",
            "-e",
            "LANG=C.UTF-8",
            CONTAINER_NAME,
            "bash",
            "-c",
            (
                "PYTHONPATH=/workspace/.github/gitbook_worker "
                "pytest -v --tb=long --showlocals --no-header --capture=no "
                "/workspace/.github/gitbook_worker/tests/test_documents_publishing.py"
            ),
        ],
        logger=logger,
    )

    output_file = output_dir / "docker_exec_output.txt"
    output_file.write_text(result.stdout, encoding="utf-8")
    shutil.copy(output_file, artifact_dir / output_file.name)

    # Cleanup
    print("\nCleaning up container...")
    run_docker_command(
        ["docker", "rm", "-f", CONTAINER_NAME], check=False, logger=logger
    )

    logger.info("Test completed")

    log_path = GH_TEST_LOGS_DIR / f"{request.node.name}.log"
    shutil.copy(log_path, artifact_dir / log_path.name)
