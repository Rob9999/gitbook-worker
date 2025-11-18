#!/usr/bin/env bash
#
# Wrapper for ERDA PDF build script
#
# This is a convenience wrapper that calls the actual build script in .github/gitbook_worker/scripts/
# Maintained for backward compatibility.
#
# The actual implementation is in: .github/gitbook_worker/scripts/build-pdf.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SCRIPT="${SCRIPT_DIR}/.github/gitbook_worker/scripts/build-pdf.sh"

if [[ ! -f "$BUILD_SCRIPT" ]]; then
    echo "Error: Build script not found: $BUILD_SCRIPT" >&2
    exit 1
fi

# Make script executable if needed
chmod +x "$BUILD_SCRIPT"

# Forward all arguments to the actual script
exec "$BUILD_SCRIPT" "$@"
