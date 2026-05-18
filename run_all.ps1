$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backendPath = Join-Path $root "app"
$frontendPath = Join-Path $root "legacy_web"

Write-Host "Starting backend and frontend..."

if (-not (Test-Path $backendPath)) {
    Write-Host "Backend folder not found: $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "Frontend folder not found: $frontendPath" -ForegroundColor Red
    exit 1
}

Start-Process powershell -WorkingDirectory $root -ArgumentList @(
    "-NoExit",
    "-Command",
    "python -m pip install -r requirements.txt; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Process powershell -WorkingDirectory $frontendPath -ArgumentList @(
    "-NoExit",
    "-Command",
    "python -m http.server 5173"
)

Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:5173"