# =============================================================================
# Docker Image Build Script with Dynamic Font Source Detection (PowerShell)
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
#   .\build-docker-dynamic.ps1 [-NoCache] [-Tag "TAG"]
#
# Examples:
#   .\build-docker-dynamic.ps1                              # Normal build
#   .\build-docker-dynamic.ps1 -NoCache                     # Clean rebuild
#   .\build-docker-dynamic.ps1 -Tag "myregistry/erda:v1"    # Custom tag
#
# =============================================================================

param(
    [switch]$NoCache,
    [string]$Tag = "erda-smart-worker:latest"
)

$ErrorActionPreference = "Stop"

# Configuration
$Dockerfile = "gitbook_worker/tools/docker/Dockerfile.dynamic"
$BuildArgs = @()

if ($NoCache) {
    $BuildArgs += "--no-cache"
}

Write-Host "========================================" -ForegroundColor Blue
Write-Host "ERDA GitBook Worker - Docker Build" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Step 1: Analyze fonts.yml for required source directories
Write-Host "Step 1: Analyzing fonts.yml for font source directories..." -ForegroundColor Yellow
Write-Host ""

try {
    # Run prepare_font_sources.py and capture output
    $FontSourcesOutput = & python gitbook_worker/tools/docker/prepare_font_sources.py `
        --fonts-yml gitbook_worker/defaults/fonts.yml 2>&1 | Out-String
    
    # Parse COPY commands and warnings
    $CopyCommands = $FontSourcesOutput -split "`n" | Where-Object { $_ -match "^COPY" }
    $Warnings = $FontSourcesOutput -split "`n" | Where-Object { $_ -match "^#" }
    
    if ($Warnings) {
        Write-Host "Warnings:" -ForegroundColor Yellow
        $Warnings | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        Write-Host ""
    }
    
    if ($CopyCommands) {
        Write-Host "✓ Found font source directories:" -ForegroundColor Green
        $CopyCommands | ForEach-Object {
            if ($_ -match "COPY ([^ ]+)") {
                Write-Host "  - $($matches[1])" -ForegroundColor White
            }
        }
        Write-Host ""
    }
    else {
        Write-Host "ℹ No local font directories - all fonts will use download_url" -ForegroundColor Yellow
        Write-Host ""
    }
}
catch {
    Write-Host "✗ Failed to analyze fonts.yml: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Validate Dockerfile exists
Write-Host "Step 2: Validating Dockerfile..." -ForegroundColor Yellow
if (-not (Test-Path $Dockerfile)) {
    Write-Host "✗ Dockerfile not found: $Dockerfile" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dockerfile found: $Dockerfile" -ForegroundColor Green
Write-Host ""

# Step 3: Build Docker image
Write-Host "Step 3: Building Docker image..." -ForegroundColor Yellow
Write-Host "  Tag: $Tag" -ForegroundColor Green
Write-Host "  Args: $($BuildArgs -join ' ')" -ForegroundColor Green
Write-Host ""

$StartTime = Get-Date

try {
    $BuildCommand = "docker build -f $Dockerfile -t $Tag $($BuildArgs -join ' ') ."
    Invoke-Expression $BuildCommand
}
catch {
    Write-Host ""
    Write-Host "✗ Docker build failed: $_" -ForegroundColor Red
    exit 1
}

$EndTime = Get-Date
$Duration = [math]::Round(($EndTime - $StartTime).TotalSeconds, 1)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Image: $Tag" -ForegroundColor Green
Write-Host "  Duration: ${Duration}s" -ForegroundColor Green
Write-Host ""

# Step 4: Validate font installation
Write-Host "Step 4: Validating font installation in image..." -ForegroundColor Yellow
Write-Host ""

try {
    $ValidationReport = docker run --rm $Tag cat /opt/gitbook_worker/reports/docker_validation_report.json 2>$null | ConvertFrom-Json
    
    if ($ValidationReport.validation_status -eq "success") {
        Write-Host "✓ Font validation passed" -ForegroundColor Green
        
        $FontCount = $ValidationReport.fonts_installed.Count
        Write-Host "  Fonts installed: $FontCount" -ForegroundColor Green
        
        $ValidationReport.fonts_installed | ForEach-Object {
            Write-Host "  - $($_.name) ($($_.license))" -ForegroundColor White
        }
    }
    else {
        Write-Host "⚠ Font validation did not pass" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Could not validate fonts (report not found or invalid)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Build complete! Run with:" -ForegroundColor Green
Write-Host "  docker run --rm -v `${PWD}:/workspace $Tag" -ForegroundColor Blue
Write-Host ""
