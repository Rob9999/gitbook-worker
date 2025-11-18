# PowerShell Wrapper für Docker-basierte Tests und Workflows
# Usage: .\run-in-docker.ps1 [test|orchestrator|shell]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("test", "test-slow", "orchestrator", "shell", "build-only")]
    [string]$Command,
    
    [string]$Profile = "local",
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$DOCKERFILE = ".github/gitbook_worker/tools/docker/Dockerfile"
$IMAGE_TAG = "erda-workflow-tools"
$CONTEXT = "."

# Stelle sicher, dass Docker läuft
Write-Host "Checking Docker daemon..." -ForegroundColor Cyan
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker daemon not running. Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Waiting for Docker to start..." -ForegroundColor Yellow
    $timeout = 120
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker is ready!" -ForegroundColor Green
            break
        }
    }
    if ($elapsed -ge $timeout) {
        Write-Error "Docker failed to start within $timeout seconds"
        exit 1
    }
}

# Prüfe, ob Image existiert oder gebaut werden muss
$imageExists = docker image inspect $IMAGE_TAG 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    if ($NoBuild) {
        Write-Error "Image '$IMAGE_TAG' not found and -NoBuild is set"
        exit 1
    }
    Write-Host "Building Docker image '$IMAGE_TAG'..." -ForegroundColor Cyan
    docker build -f $DOCKERFILE -t $IMAGE_TAG $CONTEXT
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker build failed"
        exit 1
    }
} else {
    Write-Host "Using existing Docker image '$IMAGE_TAG'" -ForegroundColor Green
}

if ($Command -eq "build-only") {
    Write-Host "Build complete!" -ForegroundColor Green
    exit 0
}

# Erstelle externes Log-Verzeichnis für Docker
$dockerLogDir = Join-Path $workDir ".docker-logs"
if (-not (Test-Path $dockerLogDir)) {
    New-Item -ItemType Directory -Force -Path $dockerLogDir | Out-Null
    Write-Host "Created external log directory: $dockerLogDir" -ForegroundColor Green
}

# Führe den gewünschten Befehl aus
$workDir = Get-Location
Write-Host "Running command in Docker container..." -ForegroundColor Cyan
Write-Host "Logs will be available in: $dockerLogDir" -ForegroundColor Cyan

switch ($Command) {
    "test" {
        docker run --rm `
            -v "${workDir}:/workspace" `
            -v "${dockerLogDir}:/docker-logs" `
            -w /workspace `
            -e PYTHONPATH=/workspace `
            -e DOCKER_LOG_DIR=/docker-logs `
            $IMAGE_TAG `
            bash -c "cd /workspace && python3 -m pytest .github/gitbook_worker/tests -v --tb=short"
    }
    "test-slow" {
        docker run --rm `
            -v "${workDir}:/workspace" `
            -v "${dockerLogDir}:/docker-logs" `
            -w /workspace `
            -e PYTHONPATH=/workspace `
            -e DOCKER_LOG_DIR=/docker-logs `
            $IMAGE_TAG `
            bash -c "cd /workspace && python3 -m pytest .github/gitbook_worker/tests -v -m slow --tb=short"
    }
    "orchestrator" {
        docker run --rm `
            -v "${workDir}:/workspace" `
            -v "${dockerLogDir}:/docker-logs" `
            -w /workspace `
            -e PYTHONPATH=/workspace `
            -e DOCKER_LOG_DIR=/docker-logs `
            $IMAGE_TAG `
            bash -c "cd /workspace && python3 -m tools.workflow_orchestrator --root /workspace --manifest publish.yml --profile $Profile"
    }
    "shell" {
        docker run --rm -it `
            -v "${workDir}:/workspace" `
            -v "${dockerLogDir}:/docker-logs" `
            -w /workspace `
            -e PYTHONPATH=/workspace `
            -e DOCKER_LOG_DIR=/docker-logs `
            $IMAGE_TAG `
            bash
    }
}

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "`nCommand completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nCommand failed with exit code: $exitCode" -ForegroundColor Red
}

exit $exitCode
