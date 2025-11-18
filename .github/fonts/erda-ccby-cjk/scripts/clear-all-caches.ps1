#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Comprehensive Windows Font Cache Clearer
    
.DESCRIPTION
    Clears all Windows font caches and restarts relevant services.
    Must be run as Administrator for full functionality.
    
.NOTES
    Author: ERDA Project
    License: MIT
    Version: 1.0
#>

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ERDA Font Cache Clearer (Requires Administrator)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$clearedCount = 0
$errorCount = 0

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠ ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "  Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Function to delete cache files
function Clear-CacheDirectory {
    param(
        [string]$Path,
        [string[]]$Patterns,
        [string]$Description
    )
    
    if (-not (Test-Path $Path)) {
        Write-Host "  ℹ Skipping (not found): $Description" -ForegroundColor Gray
        return
    }
    
    Write-Host "📁 $Description" -ForegroundColor Cyan
    Write-Host "   Path: $Path" -ForegroundColor Gray
    
    $deletedInDir = 0
    foreach ($pattern in $Patterns) {
        $files = Get-ChildItem -Path $Path -Filter $pattern -File -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            try {
                Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                Write-Host "  ✓ Deleted: $($file.Name)" -ForegroundColor Green
                $script:clearedCount++
                $deletedInDir++
            }
            catch {
                Write-Host "  ✗ Failed to delete $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
                $script:errorCount++
            }
        }
    }
    
    if ($deletedInDir -eq 0) {
        Write-Host "  ℹ No cache files found (already clean)" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Stop FontCache service before clearing caches
Write-Host "🔧 Stopping Windows FontCache service..." -ForegroundColor Yellow
try {
    Stop-Service -Name "FontCache" -Force -ErrorAction Stop
    Write-Host "  ✓ FontCache service stopped" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
catch {
    Write-Host "  ⚠ Could not stop FontCache service: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Clear System Font Cache (FNTCACHE.DAT)
Clear-CacheDirectory `
    -Path "$env:WINDIR\System32" `
    -Patterns @("FNTCACHE.DAT") `
    -Description "System Font Cache (System32)"

# Clear User Font Cache
Clear-CacheDirectory `
    -Path "$env:LOCALAPPDATA\Microsoft\Windows\Fonts" `
    -Patterns @("*.fot", "*.dat", "*.tmp") `
    -Description "User Font Cache"

# Clear Windows Caches folder
Clear-CacheDirectory `
    -Path "$env:LOCALAPPDATA\Microsoft\Windows\Caches" `
    -Patterns @("*.dat", "*.tmp") `
    -Description "Windows Caches Folder"

# Clear LocalService Font Cache
Clear-CacheDirectory `
    -Path "$env:WINDIR\ServiceProfiles\LocalService\AppData\Local\FontCache" `
    -Patterns @("*.dat", "*.tmp", "*.fot") `
    -Description "LocalService Font Cache"

# Clear LocalService Font Cache (S-1-5-21)
$fontCacheS121 = Get-ChildItem -Path "$env:WINDIR\ServiceProfiles\LocalService\AppData\Local" -Filter "FontCache-S-1-5-21*" -Directory -ErrorAction SilentlyContinue
foreach ($dir in $fontCacheS121) {
    Clear-CacheDirectory `
        -Path $dir.FullName `
        -Patterns @("*.dat", "*.tmp") `
        -Description "FontCache S-1-5-21 ($($dir.Name))"
}

# Clear Temp Font Caches
Clear-CacheDirectory `
    -Path "$env:TEMP" `
    -Patterns @("font*.tmp", "*.fot") `
    -Description "Temp Font Cache"

# Clear Internet Explorer Cache (legacy)
if (Test-Path "$env:LOCALAPPDATA\Microsoft\Windows\INetCache") {
    Clear-CacheDirectory `
        -Path "$env:LOCALAPPDATA\Microsoft\Windows\INetCache" `
        -Patterns @("*.dat", "*.tmp") `
        -Description "Internet Explorer Cache"
}

# Start FontCache service
Write-Host "🔧 Starting Windows FontCache service..." -ForegroundColor Yellow
try {
    Start-Service -Name "FontCache" -ErrorAction Stop
    Write-Host "  ✓ FontCache service started" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Could not start FontCache service: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Run fc-cache if available (for apps using fontconfig)
Write-Host "🔧 Checking for fc-cache (fontconfig)..." -ForegroundColor Yellow
$fcCache = Get-Command "fc-cache" -ErrorAction SilentlyContinue
if ($fcCache) {
    try {
        & fc-cache -f -v 2>&1 | Out-Null
        Write-Host "  ✓ fc-cache executed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ fc-cache failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  ℹ fc-cache not found (normal on Windows)" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Files deleted: $clearedCount" -ForegroundColor $(if ($clearedCount -gt 0) { "Green" } else { "Gray" })
Write-Host "  Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($clearedCount -gt 0 -or $errorCount -eq 0) {
    Write-Host "✓ Font cache refresh completed successfully" -ForegroundColor Green
}
else {
    Write-Host "⚠ Font cache refresh completed with issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚠ IMPORTANT: Next steps to see changes:" -ForegroundColor Yellow
Write-Host "  1. Close ALL applications (browsers, Office, PDF readers, etc.)" -ForegroundColor White
Write-Host "  2. Clear browser caches (Ctrl+Shift+Delete in browsers)" -ForegroundColor White
Write-Host "  3. Consider restarting Windows for system-wide font refresh" -ForegroundColor White
Write-Host ""

pause
