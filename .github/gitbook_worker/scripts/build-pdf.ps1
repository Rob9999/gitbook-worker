#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build ERDA PDF with correct Python environment
.DESCRIPTION
    Sets correct PYTHONPATH and runs the workflow orchestrator to build the PDF.
    Uses the modern workflow_orchestrator with explicit profile and manifest configuration.
.PARAMETER Profile
    Workflow profile to use (default: 'local')
    Available profiles: default, local, publisher
.PARAMETER Manifest
    Path to publish.yml manifest file (default: 'publish.yml')
.PARAMETER DryRun
    Perform a dry-run without actually building
.EXAMPLE
    .\build-pdf.ps1
    Build PDF with local profile
.EXAMPLE
    .\build-pdf.ps1 -Profile default
    Build PDF with default profile (full pipeline)
.EXAMPLE
    .\build-pdf.ps1 -DryRun
    Dry-run to see what would be executed
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('default', 'local', 'publisher')]
    [string]$WorkflowProfile = 'local',
    
    [Parameter()]
    [string]$Manifest = 'publish.yml',
    
    [Parameter()]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Get repository root (two levels up from scripts directory)
$ScriptDir = $PSScriptRoot
$RepoRoot = (Get-Item $ScriptDir).Parent.Parent.Parent.FullName

# Set correct PYTHONPATH to avoid conflicts with other projects
$env:PYTHONPATH = Join-Path $RepoRoot ".github"

# Change to repository root
Set-Location $RepoRoot

# Build command arguments
$CommandArgs = @(
    '-m', 'tools.workflow_orchestrator',
    '--root', $RepoRoot,
    '--manifest', $Manifest,
    '--profile', $WorkflowProfile
)

if ($DryRun) {
    $CommandArgs += '--dry-run'
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "ERDA PDF Build" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Repository Root: $RepoRoot" -ForegroundColor Green
Write-Host "PYTHONPATH:      $env:PYTHONPATH" -ForegroundColor Green
Write-Host "Profile:         $WorkflowProfile" -ForegroundColor Green
Write-Host "Manifest:        $Manifest" -ForegroundColor Green
if ($DryRun) {
    Write-Host "Mode:            DRY-RUN" -ForegroundColor Yellow
}
Write-Host ""

# Run workflow orchestrator
try {
    Write-Host "Executing: python $($CommandArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    & python $CommandArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "SUCCESS: PDF Build erfolgreich!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        
        if (-not $DryRun) {
            $pdfPath = Join-Path $RepoRoot "publish\das-erda-buch.pdf"
            if (Test-Path $pdfPath) {
                $pdfInfo = Get-Item $pdfPath
                $sizeInMB = [math]::Round($pdfInfo.Length / 1MB, 2)
                
                Write-Host "PDF:     $pdfPath" -ForegroundColor Green
                Write-Host "Groesse: $sizeInMB MB" -ForegroundColor Green
                Write-Host "Erstellt: $($pdfInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green
            }
        }
    }
    else {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "FEHLER: PDF Build fehlgeschlagen (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "Pruefe die Logs in: .github\logs\" -ForegroundColor Yellow
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "✗ Fehler beim PDF Build" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Stack Trace:" -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
