# PowerShell Wrapper für Docker Diagnostics
# Vereinfachte Nutzung des Diagnostik-Tools

param(
    [Parameter(Mandatory=$false)]
    [string]$Profile = "local"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Docker Orchestrator Diagnostics Workflow" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Capture BEFORE
Write-Host "`n[1/4] Capturing BEFORE snapshot..." -ForegroundColor Yellow
python -m tools.docker.docker_diagnostics capture-before
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to capture before snapshot"
    exit 1
}

# 2. Run Docker Orchestrator
Write-Host "`n[2/4] Running Docker orchestrator (profile: $Profile)..." -ForegroundColor Yellow
& "$PSScriptRoot\run-in-docker.ps1" -Command orchestrator -Profile $Profile
$dockerExitCode = $LASTEXITCODE

# 3. Capture AFTER
Write-Host "`n[3/4] Capturing AFTER snapshot..." -ForegroundColor Yellow
python -m tools.docker.docker_diagnostics capture-after
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to capture after snapshot"
    exit 1
}

# 4. Analyze
Write-Host "`n[4/4] Analyzing differences..." -ForegroundColor Yellow
python -m tools.docker.docker_diagnostics analyze
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to analyze snapshots"
    exit 1
}

# Summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Diagnostics Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Docker orchestrator exit code: $dockerExitCode"
Write-Host "Results available in: .docker-logs/"
Write-Host "  - snapshot-before.json"
Write-Host "  - snapshot-after.json"
Write-Host "  - analysis.json"
Write-Host "  - workflow.log"

if ($dockerExitCode -ne 0) {
    Write-Host "`nDocker orchestrator failed with exit code: $dockerExitCode" -ForegroundColor Red
    exit $dockerExitCode
}

exit 0
