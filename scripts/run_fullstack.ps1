$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "fullstack\backend"
$frontend = Join-Path $root "fullstack\frontend"
$npm = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
if (-not $npm) {
    $npm = (Get-Command npm -ErrorAction SilentlyContinue).Source
}
if (-not $npm) {
    throw "npm tidak ditemukan. Install Node.js 20+ lalu jalankan ulang script ini."
}

Write-Host "Menjalankan backend di http://127.0.0.1:8000"
Start-Process powershell -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
    "Set-Location '$backend'; python -m uvicorn app.main:app --reload --port 8000"
)

Write-Host "Menjalankan frontend di http://127.0.0.1:5173"
Start-Process powershell -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
    "Set-Location '$frontend'; & '$npm' run dev"
)

Write-Host ""
Write-Host "Buka http://127.0.0.1:5173"
Write-Host "API docs: http://127.0.0.1:8000/docs"
