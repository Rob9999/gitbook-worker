#!/usr/bin/env pwsh
# =============================================================================
# Build ERDA Docker Image (Dockerfile.dynamic with Font URL Support)
# =============================================================================
# 
# This script builds the Docker image using Dockerfile.dynamic which:
# - Loads fonts dynamically from fonts.yml configuration
# - Downloads fonts via URL (e.g., Twemoji from GitHub)
# - Validates license compliance (AGENTS.md)
# - Generates build manifest and validation report
#
# Usage:
#   .\build-docker-image.ps1                    # Build with default tag
#   .\build-docker-image.ps1 -Tag custom:v1     # Build with custom tag
#   .\build-docker-image.ps1 -ShowInfo          # Show info about existing image
#
# =============================================================================

param(
    [string]$Tag = "erda-workflow-tools:latest",
    [switch]$ShowInfo = $false,
    [switch]$NoCachefonts = $false
)

$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

# Change to repository root
$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
Push-Location $RepoRoot

try {
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host "ERDA Docker Image Builder" -ForegroundColor Cyan
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Repository Root: $RepoRoot" -ForegroundColor Yellow
    Write-Host "Docker Context:  $RepoRoot" -ForegroundColor Yellow
    Write-Host "Dockerfile:      .github/gitbook_worker/tools/docker/Dockerfile.dynamic" -ForegroundColor Yellow
    Write-Host "Image Tag:       $Tag" -ForegroundColor Yellow
    Write-Host ""

    # Show info mode
    if ($ShowInfo) {
        Write-Host "Checking existing image info..." -ForegroundColor Green
        docker run --rm $Tag --info
        exit 0
    }

    # Build image
    Write-Host "Building Docker image..." -ForegroundColor Green
    Write-Host ""

    $BuildArgs = @(
        "build",
        "-f", ".github/gitbook_worker/tools/docker/Dockerfile.dynamic",
        "-t", $Tag
    )

    if ($NoCachefonts) {
        $BuildArgs += "--no-cache"
        Write-Host "Building with --no-cache (fresh build)" -ForegroundColor Yellow
    }

    $BuildArgs += "."

    # Run docker build
    & docker @BuildArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed with exit code $LASTEXITCODE"
    }

    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL" -ForegroundColor Green
    Write-Host "=============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image: $Tag" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Show build info:     docker run --rm $Tag --info" -ForegroundColor White
    Write-Host "  2. Test environment:    docker run --rm -v `"`${PWD}:/workspace`" $Tag bash" -ForegroundColor White
    Write-Host "  3. Run orchestrator:    .\run-in-docker.ps1" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor Red
    Write-Host "BUILD FAILED" -ForegroundColor Red
    Write-Host "=============================================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
} finally {
    Pop-Location
}
