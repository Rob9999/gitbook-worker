#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Test admin cache refresh functionality
#>

Write-Host "Testing FontCache service restart with proper encoding..." -ForegroundColor Cyan
Write-Host ""

# Test service query
Write-Host "1. Checking FontCache service status..." -ForegroundColor Yellow
$checkResult = & sc.exe query FontCache 2>&1 | Out-String
Write-Host $checkResult

# Test Python script with admin privileges
Write-Host "2. Running font builder with cache refresh..." -ForegroundColor Yellow
python build_ccby_cjk_font.py --refresh-cache --verbose

Write-Host ""
Write-Host "✓ Test completed" -ForegroundColor Green
