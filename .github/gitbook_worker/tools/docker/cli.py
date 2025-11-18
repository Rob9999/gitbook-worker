"""CLI for smart merge configuration tool.

Usage:
    python -m gitbook_worker.tools.docker.cli get-name --type image --context test
    python -m gitbook_worker.tools.docker.cli get-name --type container --context prod --publish-name main-book
    python -m gitbook_worker.tools.docker.cli dump-config --publish-name main-book
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from . import smart_merge


def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """Find repository root by looking for .git directory.

    Args:
        start_path: Starting path for search (default: current directory)

    Returns:
        Path to repository root
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # Fallback to current directory
    return Path.cwd()


def cmd_get_name(args):
    """Get specific docker name (image or container)."""
    repo_root = find_repo_root()

    # Build extra_vars from command line arguments
    extra_vars = {}
    if args.publish_name:
        extra_vars["publish_name"] = args.publish_name
    if args.branch:
        extra_vars["branch"] = args.branch
    if args.repo_name:
        extra_vars["repo_name"] = args.repo_name
    if args.var:
        for var in args.var:
            key, value = var.split("=", 1)
            extra_vars[key] = value

    try:
        config = smart_merge.merge_configs(repo_root, args.publish_name, extra_vars)
        name = smart_merge.get_docker_name(config, args.type, args.context, extra_vars)
        print(name)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_get_all_names(args):
    """Get all docker names (image and container) as JSON."""
    repo_root = find_repo_root()

    # Build extra_vars
    extra_vars = {}
    if args.publish_name:
        extra_vars["publish_name"] = args.publish_name
    if args.branch:
        extra_vars["branch"] = args.branch
    if args.repo_name:
        extra_vars["repo_name"] = args.repo_name
    if args.var:
        for var in args.var:
            key, value = var.split("=", 1)
            extra_vars[key] = value

    try:
        names = smart_merge.get_all_docker_names(
            repo_root, args.publish_name, args.context, extra_vars
        )
        print(json.dumps(names, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_dump_config(args):
    """Dump merged configuration as JSON."""
    repo_root = find_repo_root()

    extra_vars = {}
    if args.var:
        for var in args.var:
            key, value = var.split("=", 1)
            extra_vars[key] = value

    try:
        config = smart_merge.merge_configs(repo_root, args.publish_name, extra_vars)
        print(json.dumps(config, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart merge configuration tool for Docker naming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # get-name command
    get_name_parser = subparsers.add_parser(
        "get-name", help="Get specific docker name (image or container)"
    )
    get_name_parser.add_argument(
        "--type",
        required=True,
        choices=["image", "container"],
        help="Type of docker name to retrieve",
    )
    get_name_parser.add_argument(
        "--context",
        default="test",
        choices=["github-action", "prod", "test", "docker-test"],
        help="Execution context (default: test)",
    )
    get_name_parser.add_argument(
        "--publish-name", help="Name of publish entry from publish.yml"
    )
    get_name_parser.add_argument("--branch", help="Git branch name for templating")
    get_name_parser.add_argument("--repo-name", help="Repository name for templating")
    get_name_parser.add_argument(
        "--var",
        action="append",
        help="Extra variable in format KEY=VALUE (can be used multiple times)",
    )
    get_name_parser.set_defaults(func=cmd_get_name)

    # get-all-names command
    get_all_parser = subparsers.add_parser(
        "get-all-names", help="Get all docker names (image and container) as JSON"
    )
    get_all_parser.add_argument(
        "--context",
        default="test",
        choices=["github-action", "prod", "test", "docker-test"],
        help="Execution context (default: test)",
    )
    get_all_parser.add_argument(
        "--publish-name", help="Name of publish entry from publish.yml"
    )
    get_all_parser.add_argument("--branch", help="Git branch name for templating")
    get_all_parser.add_argument("--repo-name", help="Repository name for templating")
    get_all_parser.add_argument(
        "--var",
        action="append",
        help="Extra variable in format KEY=VALUE (can be used multiple times)",
    )
    get_all_parser.set_defaults(func=cmd_get_all_names)

    # dump-config command
    dump_parser = subparsers.add_parser(
        "dump-config", help="Dump merged configuration as JSON"
    )
    dump_parser.add_argument(
        "--publish-name", help="Name of publish entry from publish.yml"
    )
    dump_parser.add_argument(
        "--var",
        action="append",
        help="Extra variable in format KEY=VALUE (can be used multiple times)",
    )
    dump_parser.set_defaults(func=cmd_dump_config)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
