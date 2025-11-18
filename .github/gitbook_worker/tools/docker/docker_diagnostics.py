#!/usr/bin/env python3
"""Diagnostics tool for tracking file changes during Docker orchestrator runs.

This tool helps identify why files are marked as 'to be removed/deleted' in Git
when running the orchestrator in Docker. It tracks file states before, during,
and after Docker execution.

Usage:
    python -m tools.docker.docker_diagnostics capture-before
    # Run Docker container
    python -m tools.docker.docker_diagnostics capture-after
    python -m tools.docker.docker_diagnostics analyze

License: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.logging_config import get_logger

LOGGER = get_logger(__name__)


@dataclass
class FileState:
    """State of a file at a given point in time."""

    path: str
    exists: bool
    size: int | None
    modified: float | None
    sha256: str | None
    git_status: str | None
    permissions: str | None
    owner: str | None


@dataclass
class DiagnosticSnapshot:
    """Snapshot of repository state."""

    timestamp: str
    git_branch: str | None
    git_commit: str | None
    files: dict[str, FileState]
    git_status_output: str | None


def get_git_info() -> tuple[str | None, str | None]:
    """Get current Git branch and commit."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        branch = None

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        commit = None

    return branch, commit


def get_git_status() -> str | None:
    """Get full Git status output."""
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None


def get_git_file_status(filepath: Path) -> str | None:
    """Get Git status for a specific file."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", str(filepath)],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.strip()
        if output:
            return output[:2]  # First two chars are the status
        return "tracked"
    except Exception:
        return None


def compute_file_hash(filepath: Path) -> str | None:
    """Compute SHA256 hash of file content."""
    if not filepath.exists() or not filepath.is_file():
        return None
    try:
        sha256 = hashlib.sha256()
        with filepath.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None


def get_file_permissions(filepath: Path) -> str | None:
    """Get file permissions as string."""
    if not filepath.exists():
        return None
    try:
        import stat

        mode = filepath.stat().st_mode
        return stat.filemode(mode)
    except Exception:
        return None


def get_file_owner(filepath: Path) -> str | None:
    """Get file owner (Unix only)."""
    if not filepath.exists():
        return None
    try:
        import pwd

        return pwd.getpwuid(filepath.stat().st_uid).pw_name
    except Exception:
        return None


def capture_file_state(filepath: Path) -> FileState:
    """Capture current state of a file."""
    exists = filepath.exists()

    if exists and filepath.is_file():
        stat = filepath.stat()
        size = stat.st_size
        modified = stat.st_mtime
        sha256 = compute_file_hash(filepath)
    else:
        size = None
        modified = None
        sha256 = None

    return FileState(
        path=str(filepath),
        exists=exists,
        size=size,
        modified=modified,
        sha256=sha256,
        git_status=get_git_file_status(filepath),
        permissions=get_file_permissions(filepath),
        owner=get_file_owner(filepath),
    )


def capture_snapshot(root: Path, patterns: list[str]) -> DiagnosticSnapshot:
    """Capture snapshot of repository state for given patterns."""
    LOGGER.info("Capturing diagnostic snapshot...")

    branch, commit = get_git_info()
    git_status = get_git_status()

    files: dict[str, FileState] = {}

    for pattern in patterns:
        for filepath in root.rglob(pattern):
            if filepath.is_file():
                rel_path = str(filepath.relative_to(root))
                files[rel_path] = capture_file_state(filepath)

    snapshot = DiagnosticSnapshot(
        timestamp=datetime.now().isoformat(),
        git_branch=branch,
        git_commit=commit,
        files=files,
        git_status_output=git_status,
    )

    LOGGER.info(f"Captured {len(files)} files")
    return snapshot


def save_snapshot(snapshot: DiagnosticSnapshot, output_file: Path) -> None:
    """Save snapshot to JSON file."""
    data = asdict(snapshot)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    LOGGER.info(f"Snapshot saved to {output_file}")


def load_snapshot(input_file: Path) -> DiagnosticSnapshot:
    """Load snapshot from JSON file."""
    with input_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    files = {
        path: FileState(**state_data) for path, state_data in data["files"].items()
    }

    return DiagnosticSnapshot(
        timestamp=data["timestamp"],
        git_branch=data["git_branch"],
        git_commit=data["git_commit"],
        files=files,
        git_status_output=data["git_status_output"],
    )


def analyze_snapshots(
    before: DiagnosticSnapshot, after: DiagnosticSnapshot
) -> dict[str, Any]:
    """Analyze differences between before and after snapshots."""
    LOGGER.info("Analyzing snapshots...")

    analysis: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "before_timestamp": before.timestamp,
        "after_timestamp": after.timestamp,
        "git_commit_changed": before.git_commit != after.git_commit,
        "changes": {
            "added": [],
            "removed": [],
            "modified": [],
            "git_status_changed": [],
            "permissions_changed": [],
            "owner_changed": [],
        },
    }

    all_paths = set(before.files.keys()) | set(after.files.keys())

    for path in all_paths:
        before_state = before.files.get(path)
        after_state = after.files.get(path)

        if before_state is None and after_state is not None:
            analysis["changes"]["added"].append(
                {
                    "path": path,
                    "git_status": after_state.git_status,
                }
            )
        elif before_state is not None and after_state is None:
            analysis["changes"]["removed"].append(
                {
                    "path": path,
                    "git_status": before_state.git_status,
                }
            )
        elif before_state is not None and after_state is not None:
            if before_state.sha256 != after_state.sha256:
                analysis["changes"]["modified"].append(
                    {
                        "path": path,
                        "before_git_status": before_state.git_status,
                        "after_git_status": after_state.git_status,
                        "size_changed": before_state.size != after_state.size,
                    }
                )

            if before_state.git_status != after_state.git_status:
                analysis["changes"]["git_status_changed"].append(
                    {
                        "path": path,
                        "before": before_state.git_status,
                        "after": after_state.git_status,
                    }
                )

            if before_state.permissions != after_state.permissions:
                analysis["changes"]["permissions_changed"].append(
                    {
                        "path": path,
                        "before": before_state.permissions,
                        "after": after_state.permissions,
                    }
                )

            if before_state.owner != after_state.owner:
                analysis["changes"]["owner_changed"].append(
                    {
                        "path": path,
                        "before": before_state.owner,
                        "after": after_state.owner,
                    }
                )

    return analysis


def print_analysis(analysis: dict[str, Any]) -> None:
    """Pretty print analysis results."""
    print("\n" + "=" * 80)
    print("DOCKER ORCHESTRATOR DIAGNOSTIC ANALYSIS")
    print("=" * 80)

    print(f"\nAnalysis timestamp: {analysis['timestamp']}")
    print(f"Before snapshot:    {analysis['before_timestamp']}")
    print(f"After snapshot:     {analysis['after_timestamp']}")
    print(f"Git commit changed: {analysis['git_commit_changed']}")

    changes = analysis["changes"]

    if changes["added"]:
        print(f"\n📁 Files ADDED: {len(changes['added'])}")
        for item in changes["added"]:
            print(f"  + {item['path']} (git: {item['git_status']})")

    if changes["removed"]:
        print(f"\n🗑️  Files REMOVED: {len(changes['removed'])}")
        for item in changes["removed"]:
            print(f"  - {item['path']} (git: {item['git_status']})")

    if changes["modified"]:
        print(f"\n✏️  Files MODIFIED: {len(changes['modified'])}")
        for item in changes["modified"]:
            print(f"  ~ {item['path']}")
            print(f"    Before git: {item['before_git_status']}")
            print(f"    After git:  {item['after_git_status']}")
            if item["size_changed"]:
                print(f"    Size changed: YES")

    if changes["git_status_changed"]:
        print(f"\n⚠️  Git STATUS CHANGED: {len(changes['git_status_changed'])}")
        for item in changes["git_status_changed"]:
            print(f"  ! {item['path']}")
            print(f"    Before: {item['before']}")
            print(f"    After:  {item['after']}")

    if changes["permissions_changed"]:
        print(f"\n🔒 PERMISSIONS CHANGED: {len(changes['permissions_changed'])}")
        for item in changes["permissions_changed"]:
            print(f"  ! {item['path']}")
            print(f"    Before: {item['before']}")
            print(f"    After:  {item['after']}")

    if changes["owner_changed"]:
        print(f"\n👤 OWNER CHANGED: {len(changes['owner_changed'])}")
        for item in changes["owner_changed"]:
            print(f"  ! {item['path']}")
            print(f"    Before: {item['before']}")
            print(f"    After:  {item['after']}")

    # Summary
    total_issues = (
        len(changes["added"])
        + len(changes["removed"])
        + len(changes["modified"])
        + len(changes["git_status_changed"])
        + len(changes["permissions_changed"])
        + len(changes["owner_changed"])
    )

    print("\n" + "=" * 80)
    print(f"TOTAL ISSUES DETECTED: {total_issues}")
    print("=" * 80 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Docker orchestrator diagnostics tool")

    parser.add_argument(
        "command",
        choices=["capture-before", "capture-after", "analyze"],
        help="Command to execute",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory",
    )

    parser.add_argument(
        "--patterns",
        nargs="+",
        default=["*.md", "*.yml", "*.yaml", "*.json"],
        help="File patterns to track",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".docker-logs"),
        help="Output directory for snapshots",
    )

    args = parser.parse_args()

    output_dir = args.root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    before_file = output_dir / "snapshot-before.json"
    after_file = output_dir / "snapshot-after.json"
    analysis_file = output_dir / "analysis.json"

    if args.command == "capture-before":
        snapshot = capture_snapshot(args.root, args.patterns)
        save_snapshot(snapshot, before_file)
        print(f"\n✅ Before snapshot captured: {before_file}")
        print("Now run your Docker orchestrator command.")
        print("Then run: python -m tools.docker.docker_diagnostics capture-after")
        return 0

    elif args.command == "capture-after":
        if not before_file.exists():
            LOGGER.error(f"Before snapshot not found: {before_file}")
            print("❌ Run 'capture-before' first!")
            return 1

        snapshot = capture_snapshot(args.root, args.patterns)
        save_snapshot(snapshot, after_file)
        print(f"\n✅ After snapshot captured: {after_file}")
        print("Now run: python -m tools.docker.docker_diagnostics analyze")
        return 0

    elif args.command == "analyze":
        if not before_file.exists():
            LOGGER.error(f"Before snapshot not found: {before_file}")
            print("❌ Run 'capture-before' first!")
            return 1

        if not after_file.exists():
            LOGGER.error(f"After snapshot not found: {after_file}")
            print("❌ Run 'capture-after' first!")
            return 1

        before = load_snapshot(before_file)
        after = load_snapshot(after_file)
        analysis = analyze_snapshots(before, after)

        # Save analysis
        with analysis_file.open("w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        # Print to console
        print_analysis(analysis)
        print(f"Detailed analysis saved to: {analysis_file}")

        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
