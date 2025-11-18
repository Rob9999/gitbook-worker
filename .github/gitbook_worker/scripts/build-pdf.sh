#!/usr/bin/env bash
#
# Build ERDA PDF with correct Python environment
#
# SYNOPSIS
#   build-pdf.sh [OPTIONS]
#
# DESCRIPTION
#   Sets correct PYTHONPATH and runs the workflow orchestrator to build the PDF.
#   Uses the modern workflow_orchestrator with explicit profile and manifest configuration.
#
# OPTIONS
#   -p, --profile PROFILE   Workflow profile to use (default: 'local')
#                           Available: default, local, publisher
#   -m, --manifest FILE     Path to publish.yml manifest (default: 'publish.yml')
#   -d, --dry-run          Perform a dry-run without actually building
#   -h, --help             Show this help message
#
# EXAMPLES
#   ./build-pdf.sh
#   Build PDF with local profile
#
#   ./build-pdf.sh --profile default
#   Build PDF with default profile (full pipeline)
#
#   ./build-pdf.sh --dry-run
#   Dry-run to see what would be executed
#

set -euo pipefail

# Colors for output
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_GRAY='\033[0;90m'
readonly COLOR_RESET='\033[0m'

# Default values
WORKFLOW_PROFILE="local"
MANIFEST="publish.yml"
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--profile)
            WORKFLOW_PROFILE="$2"
            shift 2
            ;;
        -m|--manifest)
            MANIFEST="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            sed -n '2,/^$/p' "$0" | sed 's/^# //; s/^#//'
            exit 0
            ;;
        *)
            echo -e "${COLOR_RED}Error: Unknown option: $1${COLOR_RESET}" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
done

# Validate profile
case "$WORKFLOW_PROFILE" in
    default|local|publisher)
        ;;
    *)
        echo -e "${COLOR_RED}Error: Invalid profile '$WORKFLOW_PROFILE'${COLOR_RESET}" >&2
        echo "Valid profiles: default, local, publisher" >&2
        exit 1
        ;;
esac

# Get repository root (three levels up from scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Set correct PYTHONPATH to avoid conflicts with other projects
export PYTHONPATH="${REPO_ROOT}/.github"

# Change to repository root
cd "$REPO_ROOT"

# Build command arguments
COMMAND_ARGS=(
    -m tools.workflow_orchestrator
    --root "$REPO_ROOT"
    --manifest "$MANIFEST"
    --profile "$WORKFLOW_PROFILE"
)

if [[ "$DRY_RUN" == "true" ]]; then
    COMMAND_ARGS+=(--dry-run)
fi

echo -e "${COLOR_CYAN}================================================================${COLOR_RESET}"
echo -e "${COLOR_CYAN}ERDA PDF Build${COLOR_RESET}"
echo -e "${COLOR_CYAN}================================================================${COLOR_RESET}"
echo -e "${COLOR_GREEN}Repository Root: ${REPO_ROOT}${COLOR_RESET}"
echo -e "${COLOR_GREEN}PYTHONPATH:      ${PYTHONPATH}${COLOR_RESET}"
echo -e "${COLOR_GREEN}Profile:         ${WORKFLOW_PROFILE}${COLOR_RESET}"
echo -e "${COLOR_GREEN}Manifest:        ${MANIFEST}${COLOR_RESET}"
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${COLOR_YELLOW}Mode:            DRY-RUN${COLOR_RESET}"
fi
echo ""

# Run workflow orchestrator
echo -e "${COLOR_GRAY}Executing: python ${COMMAND_ARGS[*]}${COLOR_RESET}"
echo ""

if python "${COMMAND_ARGS[@]}"; then
    EXIT_CODE=$?
    
    echo ""
    echo -e "${COLOR_GREEN}================================================================${COLOR_RESET}"
    echo -e "${COLOR_GREEN}SUCCESS: PDF Build erfolgreich!${COLOR_RESET}"
    echo -e "${COLOR_GREEN}================================================================${COLOR_RESET}"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        PDF_PATH="${REPO_ROOT}/publish/das-erda-buch.pdf"
        if [[ -f "$PDF_PATH" ]]; then
            # Get file size in MB
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                SIZE_BYTES=$(stat -f%z "$PDF_PATH")
            else
                # Linux
                SIZE_BYTES=$(stat -c%s "$PDF_PATH")
            fi
            SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $SIZE_BYTES/1048576}")
            
            # Get modification time
            if [[ "$OSTYPE" == "darwin"* ]]; then
                MTIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$PDF_PATH")
            else
                MTIME=$(stat -c "%y" "$PDF_PATH" | cut -d'.' -f1)
            fi
            
            echo -e "${COLOR_GREEN}PDF:     ${PDF_PATH}${COLOR_RESET}"
            echo -e "${COLOR_GREEN}Groesse: ${SIZE_MB} MB${COLOR_RESET}"
            echo -e "${COLOR_GREEN}Erstellt: ${MTIME}${COLOR_RESET}"
        fi
    fi
    
    exit 0
else
    EXIT_CODE=$?
    
    echo ""
    echo -e "${COLOR_RED}================================================================${COLOR_RESET}"
    echo -e "${COLOR_RED}FEHLER: PDF Build fehlgeschlagen (Exit Code: ${EXIT_CODE})${COLOR_RESET}"
    echo -e "${COLOR_RED}================================================================${COLOR_RESET}"
    echo -e "${COLOR_YELLOW}Pruefe die Logs in: .github/logs/${COLOR_RESET}"
    
    exit "$EXIT_CODE"
fi
