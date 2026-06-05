param(
    [ValidateSet("mock", "live")]
    [string]$Mode = "mock",
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$tmpPath = Join-Path $projectRoot ".tmp"

if (-not (Test-Path -LiteralPath $tmpPath)) {
    New-Item -ItemType Directory -Path $tmpPath | Out-Null
}

# Avoid permission issues in system temp on this machine.
$env:TMP = $tmpPath
$env:TEMP = $tmpPath
$env:QXG_MODE = $Mode

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "[QXG] Creating virtual environment..."
    python -m venv $venvPath
}

Write-Host "[QXG] Installing dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")

Write-Host "[QXG] Starting API on http://$BindHost`:$Port (mode=$Mode)"
& $venvPython -m uvicorn app.main:app --host $BindHost --port $Port --reload