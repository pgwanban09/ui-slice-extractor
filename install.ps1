param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$sourcePath = (Resolve-Path (Join-Path $PSScriptRoot "skills\ui-slice-extractor")).Path
$codexSkillsRoot = Join-Path $env:USERPROFILE ".codex\skills"
$targetPath = Join-Path $codexSkillsRoot "ui-slice-extractor"

if (-not (Test-Path (Join-Path $sourcePath "SKILL.md"))) {
    throw "skills\ui-slice-extractor\SKILL.md was not found. Run this script from the cloned repository."
}

if ((Test-Path $targetPath) -and -not $Force) {
    throw "Target already exists: $targetPath. Re-run with -Force to update it."
}

New-Item -ItemType Directory -Force -Path $codexSkillsRoot | Out-Null
New-Item -ItemType Directory -Force -Path $targetPath | Out-Null

Get-ChildItem -Force $sourcePath |
    Where-Object { $_.Name -ne ".git" } |
    Copy-Item -Destination $targetPath -Recurse -Force

Write-Host "Installed ui-slice-extractor to $targetPath"
Write-Host "Restart Codex to refresh the available skills."
