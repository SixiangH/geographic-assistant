# Run from a terminal with network access / 从允许联网的终端运行。
$ErrorActionPreference = 'Stop'
$atlasProject = Split-Path $PSScriptRoot -Parent
$atlasPython = Join-Path $env:USERPROFILE 'miniconda3\envs\aai\python.exe'
if (-not (Test-Path -LiteralPath $atlasPython)) {
    throw 'The aai Python environment was not found. Activate aai and run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000.'
}
Push-Location -LiteralPath $atlasProject
try { & $atlasPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000 }
finally { Pop-Location }
