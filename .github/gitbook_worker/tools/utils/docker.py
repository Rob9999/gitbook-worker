"""High-level Docker helpers that wrap :mod:`tools.utils.docker_runner`."""

from __future__ import annotations

from pathlib import Path

from tools.logging_config import get_logger

from .docker_runner import (
    build_image,
    docker_cli_available,
    docker_daemon_ready,
    image_exists,
    try_start_docker_daemon,
)

LOGGER = get_logger(__name__)


class DockerError(RuntimeError):
    """Raised when Docker prerequisites are not met."""


def ensure_daemon_ready(*, wait_seconds: int = 120) -> None:
    """Ensure the Docker daemon is reachable."""
    if not docker_cli_available():
        raise DockerError("Docker CLI not found on PATH.")
    if docker_daemon_ready(timeout_sec=0):
        LOGGER.debug("Docker daemon already available")
        return
    LOGGER.info("Attempting to start Docker daemon")
    if not try_start_docker_daemon(wait_timeout=wait_seconds):
        raise DockerError("Docker daemon is not ready; please start Docker and retry.")


def ensure_image(
    tag: str,
    dockerfile: Path,
    *,
    context: Path | None = None,
    wait_seconds: int = 120,
    build_missing: bool = True,
) -> None:
    """Ensure that *tag* exists, optionally building it from *dockerfile*."""
    ensure_daemon_ready(wait_seconds=wait_seconds)
    if image_exists(tag):
        LOGGER.debug("Docker image '%s' already present", tag)
        return
    if not build_missing:
        raise DockerError(f"Docker image '{tag}' not found and building is disabled.")
    dockerfile = dockerfile.resolve()
    ctx = (context or dockerfile.parent).resolve()
    if not dockerfile.exists():
        raise FileNotFoundError(f"Dockerfile not found: {dockerfile}")
    if not ctx.exists():
        raise FileNotFoundError(f"Docker build context not found: {ctx}")
    LOGGER.info("Building Docker image '%s' from %s", tag, dockerfile)
    rc = build_image(tag, dockerfile, ctx)
    if rc != 0:
        raise DockerError(f"docker build failed for '{tag}' with exit code {rc}")


__all__ = [
    "DockerError",
    "ensure_daemon_ready",
    "ensure_image",
]
