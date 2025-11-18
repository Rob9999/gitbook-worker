#!/usr/bin/env pwsh
# Wrapper script for gitbook_worker.tools.docker CLI
# Automatically sets PYTHONPATH and invokes the CLI module
#
# Usage:
#   .\docker-names.ps1 get-name --type image --context test
#   .\docker-names.ps1 get-all-names --context docker-test --publish-name space-tests
#   .\docker-names.ps1 dump-config

# Get the repository root (script is in .github/gitbook_worker/scripts)
$SCRIPT_DIR = Split-Path -Parent $PSCommandPath
$GITBOOK_WORKER_DIR = Split-Path -Parent $SCRIPT_DIR
$GITHUB_DIR = Split-Path -Parent $GITBOOK_WORKER_DIR
$PYTHONPATH_DIR = $GITHUB_DIR

# Set PYTHONPATH temporarily for this invocation
$env:PYTHONPATH = $PYTHONPATH_DIR

# Forward all arguments to the CLI module
python -m gitbook_worker.tools.docker.cli $args

# Exit with the same exit code as the Python script
exit $LASTEXITCODE
