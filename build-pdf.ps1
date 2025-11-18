#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wrapper for ERDA PDF build script
.DESCRIPTION
    This is a convenience wrapper that calls the actual build script in .github/gitbook_worker/scripts/
    Maintained for backward compatibility.
.NOTES
    The actual implementation is in: .github/gitbook_worker/scripts/build-pdf.ps1
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

$ScriptPath = Join-Path $PSScriptRoot ".github\gitbook_worker\scripts\build-pdf.ps1"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Build script not found: $ScriptPath"
    exit 1
}

$params = @{
    WorkflowProfile = $WorkflowProfile
    Manifest        = $Manifest
}

if ($DryRun) {
    $params['DryRun'] = $true
}

& $ScriptPath @params
exit $LASTEXITCODE
