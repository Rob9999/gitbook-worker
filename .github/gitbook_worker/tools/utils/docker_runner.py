#!/usr/bin/env python3
"""
Convenience launcher for running commands inside a Docker image.

Features
- Detects Windows vs. Linux/macOS.
- Ensures the Docker daemon (or Docker Desktop) is running.
- Builds an image from a Dockerfile if the tag is missing.
- Runs a container with a bind mount to the working directory.
- Forwards a command (e.g., pytest) to be executed inside the container.

Example
-------
python docker_workflow_runner.py \
  --dockerfile .github/gitbook_worker/tools/docker/Dockerfile \
  --tag sphere-space-workflow-tools-tests \
  --context . \
  --workdir . \
  --env PYTHONPATH=/workspace \
  --it python3 -m pytest .github/gitbook_worker/tests/

Notes
-----
- Avoids fancy Unicode in logs to sidestep Windows cp1252 issues.
- On Windows, tries to start Docker Desktop if the Docker service is not ready.
- On Linux, attempts to start the docker service via systemd when possible.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Sequence


# ------------------------------
# Logging helpers (plain ASCII)
# ------------------------------


def log_info(msg: str) -> None:
    print(f"INFO: {msg}")


def log_warn(msg: str) -> None:
    print(f"WARN: {msg}")


def log_error(msg: str) -> None:
    print(f"ERROR: {msg}")


# ------------------------------
# OS detection
# ------------------------------


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def is_linux() -> bool:
    return platform.system().lower() == "linux"


# ------------------------------
# Subprocess helpers
# ------------------------------


def run(
    cmd: Sequence[str],
    check: bool = False,
    capture_output: bool = False,
    text: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    log_info("EXEC: " + " ".join(_quote_for_log(c) for c in cmd))
    return subprocess.run(
        cmd, check=check, capture_output=capture_output, text=text, env=env
    )


def _quote_for_log(token: str) -> str:
    if " " in token or "\t" in token:
        return f'"{token}"'
    return token


# ------------------------------
# Docker checks and starters
# ------------------------------


def docker_cli_available() -> bool:
    return shutil.which("docker") is not None


def docker_daemon_ready(timeout_sec: int = 0) -> bool:
    """Return True if `docker info` succeeds. Optionally wait up to timeout_sec."""
    deadline = time.monotonic() + max(0, timeout_sec)
    while True:
        try:
            cp = run(["docker", "info"], check=False, capture_output=True)
            if cp.returncode == 0:
                return True
            else:
                # Some systems return non-zero while starting
                time.sleep(1)
        except FileNotFoundError:
            return False
        if time.monotonic() > deadline:
            return False


def try_start_docker_daemon(wait_timeout: int = 120) -> bool:
    """Attempt to start the Docker daemon (best effort). Returns True if ready."""
    if docker_daemon_ready(timeout_sec=0):
        return True

    if is_windows():
        # Prefer starting the Windows service if available, else Docker Desktop app
        # 1) Try com.docker.service
        try:
            svc = run(["sc", "query", "com.docker.service"], capture_output=True)
            if "RUNNING" not in (svc.stdout or ""):
                log_info("Attempting to start Windows service com.docker.service")
                run(["sc", "start", "com.docker.service"], capture_output=True)
        except Exception as e:
            log_warn(f"Service check failed: {e}")

        # 2) Start Docker Desktop app (path may vary)
        docker_desktop_paths = [
            r"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
            r"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe".replace(" ", " "),
        ]
        for p in docker_desktop_paths:
            exe = Path(p)
            if exe.exists():
                try:
                    log_info(f"Launching Docker Desktop: {exe}")
                    subprocess.Popen(
                        [str(exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    break
                except Exception as e:
                    log_warn(f"Failed to start Docker Desktop: {e}")
                break
        # Wait for readiness
        if docker_daemon_ready(timeout_sec=wait_timeout):
            return True
        return False

    if is_linux():
        # Try systemd start (may require sudo)
        try:
            cp = run(["systemctl", "is-active", "docker"], capture_output=True)
            if cp.returncode != 0:
                log_info("Trying to start 'docker' service via systemctl")
                run(["sudo", "systemctl", "start", "docker"], capture_output=True)
        except FileNotFoundError:
            log_warn("systemctl not found; cannot auto-start docker service")
        except Exception as e:
            log_warn(f"Starting docker via systemctl failed: {e}")
        return docker_daemon_ready(timeout_sec=wait_timeout)

    if is_macos():
        # Start Docker.app
        try:
            log_info("Trying to start Docker.app")
            run(["open", "-g", "/Applications/Docker.app"], capture_output=True)
        except Exception as e:
            log_warn(f"Failed to open Docker.app: {e}")
        return docker_daemon_ready(timeout_sec=wait_timeout)

    return False


# ------------------------------
# Image ensure/build
# ------------------------------


def image_exists(tag: str) -> bool:
    cp = run(["docker", "image", "inspect", tag], capture_output=True)
    return cp.returncode == 0


def build_image(
    tag: str,
    dockerfile: Path,
    context: Path,
    *,
    pull: bool = True,
    no_cache: bool = False,
) -> int:
    cmd = [
        "docker",
        "build",
        "-f",
        str(dockerfile),
    ]

    if pull:
        cmd.append("--pull")

    if no_cache:
        cmd.append("--no-cache")

    cmd += [
        "-t",
        tag,
        str(context),
    ]
    cp = run(cmd)
    return cp.returncode


# ------------------------------
# Container run
# ------------------------------


def run_in_container(
    tag: str,
    workdir: Path,
    env_pairs: List[str],
    cmd_inside: List[str],
    extra_run_args: List[str] | None = None,
) -> int:
    if not workdir.exists():
        log_error(f"Workdir does not exist: {workdir}")
        return 2

    # Ensure absolute path for mount. Docker Desktop on Windows accepts native paths.
    host_dir = str(workdir.resolve())
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{host_dir}:/workspace",
        "-w",
        "/workspace",
    ]

    # Env vars
    for kv in env_pairs:
        docker_cmd += ["-e", kv]

    if extra_run_args:
        docker_cmd += list(extra_run_args)

    docker_cmd.append(tag)
    docker_cmd += cmd_inside

    cp = run(docker_cmd)
    return cp.returncode


# ------------------------------
# CLI
# ------------------------------


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run a command inside a Docker image, building it if needed."
    )
    p.add_argument("--dockerfile", required=True, help="Path to the Dockerfile")
    p.add_argument("--tag", required=True, help="Docker image tag to use")
    p.add_argument("--context", default=".", help="Docker build context (default: .)")
    p.add_argument(
        "--workdir",
        default=".",
        help="Host directory to mount at /workspace (default: .)",
    )
    p.add_argument(
        "--env",
        action="append",
        default=[],
        help="Environment variable KEY=VALUE to pass (repeatable)",
    )
    p.add_argument(
        "--run-arg",
        action="append",
        default=[],
        help="Extra docker run args, e.g. --run-arg=--network=host",
    )
    p.add_argument(
        "--no-build",
        action="store_true",
        help="Do not attempt to build image if missing",
    )
    p.add_argument(
        "--rebuild",
        action="store_true",
        help="Build image even if it already exists",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable Docker layer cache during build",
    )
    p.add_argument(
        "--wait",
        type=int,
        default=120,
        help="Seconds to wait for Docker daemon to become ready (default: 120)",
    )
    p.add_argument(
        "--print-only",
        action="store_true",
        help="Print the docker run command and exit",
    )
    p.add_argument("--verbose", action="store_true", help="More logging")
    p.add_argument(
        "--it",
        dest="--",
        nargs=argparse.REMAINDER,
        help="Command to run inside the container",
    )
    args = p.parse_args(argv)
    # argparse puts the command after "--it" into args.-- as list; strip leading "--" if present.
    if args.__dict__.get("--"):
        if args.__dict__["--"] and args.__dict__["--"][0] == "--":
            args.__dict__["--"] = args.__dict__["--"][1:]
    return args


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    if args.verbose:
        log_info(f"Detected OS: {platform.system()} {platform.release()}")

    if not docker_cli_available():
        log_error(
            "Docker CLI not found. Please install Docker Desktop or Docker Engine and ensure 'docker' is on PATH."
        )
        return 1

    if not docker_daemon_ready(timeout_sec=0):
        log_info("Docker daemon not ready; attempting to start it.")
        if not try_start_docker_daemon(wait_timeout=args.wait):
            log_error("Docker daemon is not ready. Please start Docker and try again.")
            return 1

    tag = args.tag
    dockerfile = Path(args.dockerfile)
    context = Path(args.context)
    workdir = Path(args.workdir)

    needs_build = args.rebuild or not image_exists(tag)

    if needs_build:
        if args.no_build and not args.rebuild:
            log_error(f"Image '{tag}' not found and --no-build is set.")
            return 1
        if not dockerfile.exists():
            log_error(f"Dockerfile not found: {dockerfile}")
            return 1
        if not context.exists():
            log_error(f"Build context not found: {context}")
            return 1
        log_info(
            f"Building image '{tag}' from {dockerfile} with context {context}"
            + (" (no cache)" if args.no_cache else "")
        )
        rc = build_image(
            tag,
            dockerfile,
            context,
            pull=True,
            no_cache=args.no_cache,
        )
        if rc != 0:
            log_error(f"docker build failed with code {rc}")
            return rc

    cmd_inside: List[str] = args.__dict__.get("--") or []
    if not cmd_inside:
        log_warn(
            "No inner command provided; defaulting to 'python3 -m pytest .github/tests/'"
        )
        cmd_inside = ["python3", "-m", "pytest", ".github/tests/"]

    if args.print_only:
        # Show the run command and exit without executing.
        host_dir = str(Path(args.workdir).resolve())
        assembled = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{host_dir}:/workspace",
            "-w",
            "/workspace",
        ]
        for kv in args.env:
            assembled += ["-e", kv]
        for ra in args.run_arg:
            assembled.append(ra)
        assembled.append(tag)
        assembled += cmd_inside
        log_info("Dry-run command:")
        print(" ".join(_quote_for_log(x) for x in assembled))
        return 0

    # Ensure default env PYTHONPATH=/workspace if not set explicitly
    env_pairs = list(args.env)
    if not any(kv.startswith("PYTHONPATH=") for kv in env_pairs):
        env_pairs.append("PYTHONPATH=/workspace")

    log_info(f"Running in container '{tag}' with workdir {workdir.resolve()}")
    rc = run_in_container(
        tag, workdir, env_pairs, cmd_inside, extra_run_args=args.run_arg
    )
    if rc != 0:
        log_error(f"docker run exited with code {rc}")
    return rc


if __name__ == "__main__":
    main()
