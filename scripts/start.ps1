param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectPath
$pythonPath = Join-Path $env:USERPROFILE 'miniconda3\envs\aai\python.exe'
if (Test-Path -LiteralPath $pythonPath) {
    & $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port $Port
} elseif (Get-Command conda -ErrorAction SilentlyContinue) {
    conda run --no-capture-output -n aai python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
} else {
    throw 'Activate your aai environment, then run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000'
}
