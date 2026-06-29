# Remove local artifacts that should not be uploaded to GitHub.
# Usage: .\scripts\cleanup-before-github.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$removeDirs = @(
    "monster_ai\monsterai",
    "data\training",
    "data\quality",
    "data\tmp",
    "terminals",
    "Discord版 Monster Ai",
    "apps\monstercallguard-android\.gradle",
    "apps\monstercallguard-android\app\build",
    "apps\monstercallguard-android\keystore"
)

$removeFiles = @(
    "data\monster-ai.lock",
    "apps\monstercallguard-android\local.properties",
    "tools\nssm\nssm.exe"
)

function Remove-GeneratedOutputs {
    param([string]$Dir)
    if (-not (Test-Path $Dir)) { return }
    Get-ChildItem $Dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne ".gitkeep" } |
        ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "Removed: $($_.FullName)"
        }
}

Write-Host "Cleaning runtime artifacts under $Root`n" -ForegroundColor Cyan

foreach ($dir in $removeDirs) {
    $path = Join-Path $Root $dir
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
        Write-Host "Removed dir: $dir"
    }
}

foreach ($file in $removeFiles) {
    $path = Join-Path $Root $file
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Removed file: $file"
    }
}

Remove-GeneratedOutputs (Join-Path $Root "data\outputs\images")
Remove-GeneratedOutputs (Join-Path $Root "data\outputs\videos")
Remove-GeneratedOutputs (Join-Path $Root "data\outputs\audio")

Get-ChildItem $Root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

if (Test-Path (Join-Path $Root ".pytest_cache")) {
    Remove-Item (Join-Path $Root ".pytest_cache") -Recurse -Force
}

Write-Host "`nUntracking ignored paths from git..." -ForegroundColor Cyan
if (Test-Path (Join-Path $Root ".git")) {
    $untrack = @(
        "monster_ai/monsterai",
        "data/training",
        "data/quality",
        "data/outputs",
        "data/characters",
        "data/crimeguard/network_lock_state.json",
        "data/crimeguard/vpn_exit_nodes.json",
        "data/monster-ai.lock",
        "tools/nssm",
        "apps/monstercallguard-android/local.properties",
        "apps/monstercallguard-android/app/build",
        "terminals",
        "Discord版 Monster Ai"
    )
    foreach ($path in $untrack) {
        git rm -r --cached --ignore-unmatch $path 2>$null | Out-Null
    }
    git add -A
    Write-Host "Git index updated. Run: git status" -ForegroundColor Green
} else {
    Write-Host "No .git folder — filesystem cleanup only." -ForegroundColor Yellow
}

Write-Host "`nKept locally (not deleted): discord.token.local, config.yaml" -ForegroundColor Yellow
Write-Host "Done." -ForegroundColor Green