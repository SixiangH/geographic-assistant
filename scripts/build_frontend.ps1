# Build the shadcn frontend / 构建 shadcn 前端。
$ErrorActionPreference = 'Stop'
$atlasFrontend = Join-Path (Split-Path $PSScriptRoot -Parent) 'frontend'
$atlasNodeCommand = Get-Command node -ErrorAction SilentlyContinue
$atlasNode = if ($atlasNodeCommand) { $atlasNodeCommand.Source } else {
    Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
}
if (-not (Test-Path -LiteralPath $atlasNode)) { throw 'Install Node.js 22.12+ before building the frontend.' }
if (-not (Test-Path -LiteralPath (Join-Path $atlasFrontend 'node_modules\vite\bin\vite.js'))) {
    throw 'Install frontend dependencies first: cd frontend; pnpm install --frozen-lockfile'
}
Push-Location -LiteralPath $atlasFrontend
try {
    & $atlasNode node_modules/vite/bin/vite.js build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    & $atlasNode scripts/sync-entry.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Could not update the frontend entry.' }
} finally { Pop-Location }
