#!/bin/bash
# Wrapper script for gitbook_worker.tools.docker CLI
# Automatically sets PYTHONPATH and invokes the CLI module
#
# Usage:
#   ./docker-names.sh get-name --type image --context test
#   ./docker-names.sh get-all-names --context docker-test --publish-name space-tests
#   ./docker-names.sh dump-config

# Get the repository root (script is in .github/gitbook_worker/scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITBOOK_WORKER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GITHUB_DIR="$(cd "$GITBOOK_WORKER_DIR/.." && pwd)"
PYTHONPATH_DIR="${GITHUB_DIR}"

# Set PYTHONPATH temporarily for this invocation
export PYTHONPATH="${PYTHONPATH_DIR}"

# Forward all arguments to the CLI module
python -m gitbook_worker.tools.docker.cli "$@"
