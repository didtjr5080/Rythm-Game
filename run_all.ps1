$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"

Write-Host "Starting backend and frontend..."
Start-Process powershell -WorkingDirectory $backendPath -ArgumentList "-NoExit", "-Command", "python -m venv .venv; if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }; pip install -r requirements.txt; uvicorn main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -WorkingDirectory $frontendPath -ArgumentList "-NoExit", "-Command", "npm install; npm run dev"

Write-Host "Done. Backend on http://127.0.0.1:8000, Frontend on http://localhost:5173"
