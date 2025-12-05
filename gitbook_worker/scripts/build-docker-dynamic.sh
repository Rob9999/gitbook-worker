#!/bin/bash
# =============================================================================
# Docker Image Build Script with Dynamic Font Source Detection
# =============================================================================
# 
# This script builds the ERDA GitBook Worker Docker image with automatic
# font source directory detection based on fonts.yml configuration.
#
# Features:
# - Analyzes fonts.yml to determine required local directories
# - Generates appropriate COPY commands for Dockerfile
# - Validates font sources before build
# - Provides clear feedback about missing directories (will use download_url)
# - Supports both local development and CI/GitHub environments
#
# Usage:
#   ./build-docker-dynamic.sh [--no-cache] [--tag TAG]
#
# Examples:
#   ./build-docker-dynamic.sh                          # Normal build
#   ./build-docker-dynamic.sh --no-cache               # Clean rebuild
#   ./build-docker-dynamic.sh --tag myregistry/erda:v1 # Custom tag
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DOCKERFILE="gitbook_worker/tools/docker/Dockerfile.dynamic"
TAG="erda-smart-worker:latest"
BUILD_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            BUILD_ARGS="$BUILD_ARGS --no-cache"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--no-cache] [--tag TAG]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ERDA GitBook Worker - Docker Build${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Analyze fonts.yml for required source directories
echo -e "${YELLOW}Step 1: Analyzing fonts.yml for font source directories...${NC}"
echo ""

FONT_SOURCES=$(python3 gitbook_worker/tools/docker/prepare_font_sources.py \
    --fonts-yml gitbook_worker/defaults/fonts.yml 2>&1)

# Capture stdout (COPY commands) and stderr (warnings)
COPY_COMMANDS=$(echo "$FONT_SOURCES" | grep "^COPY" || true)
WARNINGS=$(echo "$FONT_SOURCES" | grep "^#" || true)

if [ -n "$WARNINGS" ]; then
    echo -e "${YELLOW}Warnings:${NC}"
    echo "$WARNINGS"
    echo ""
fi

if [ -n "$COPY_COMMANDS" ]; then
    echo -e "${GREEN}✓ Found font source directories:${NC}"
    echo "$COPY_COMMANDS" | sed 's/COPY \([^ ]*\).*/  - \1/'
    echo ""
else
    echo -e "${YELLOW}ℹ No local font directories - all fonts will use download_url${NC}"
    echo ""
fi

# Step 2: Validate Dockerfile exists
echo -e "${YELLOW}Step 2: Validating Dockerfile...${NC}"
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}✗ Dockerfile not found: $DOCKERFILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dockerfile found: $DOCKERFILE${NC}"
echo ""

# Step 3: Build Docker image
echo -e "${YELLOW}Step 3: Building Docker image...${NC}"
echo -e "  Tag: ${GREEN}$TAG${NC}"
echo -e "  Args: ${GREEN}$BUILD_ARGS${NC}"
echo ""

START_TIME=$(date +%s)

docker build -f "$DOCKERFILE" -t "$TAG" $BUILD_ARGS .

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Docker image built successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "  Image: ${GREEN}$TAG${NC}"
echo -e "  Duration: ${GREEN}${DURATION}s${NC}"
echo ""

# Step 4: Validate font installation
echo -e "${YELLOW}Step 4: Validating font installation in image...${NC}"
echo ""

VALIDATION_REPORT=$(docker run --rm "$TAG" cat /opt/gitbook_worker/reports/docker_validation_report.json 2>/dev/null || echo "{}")

if echo "$VALIDATION_REPORT" | jq -e '.validation_status == "success"' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Font validation passed${NC}"
    
    # Show installed fonts
    FONT_COUNT=$(echo "$VALIDATION_REPORT" | jq -r '.fonts_installed | length' 2>/dev/null || echo "0")
    echo -e "  Fonts installed: ${GREEN}$FONT_COUNT${NC}"
    
    echo "$VALIDATION_REPORT" | jq -r '.fonts_installed[]? | "  - \(.name) (\(.license))"' 2>/dev/null || true
    
else
    echo -e "${YELLOW}⚠ Could not validate fonts (report not found or invalid)${NC}"
fi

echo ""
echo -e "${GREEN}Build complete! Run with:${NC}"
echo -e "  ${BLUE}docker run --rm -v \$(pwd):/workspace $TAG${NC}"
echo ""
