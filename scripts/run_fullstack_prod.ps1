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

Push-Location $frontend
try {
    & $npm run build
} finally {
    Pop-Location
}

Write-Host "Frontend di-build. Menjalankan satu server di http://127.0.0.1:8000"
Push-Location $backend
try {
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
} finally {
    Pop-Location
}
