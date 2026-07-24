# Build StartPlanner one-folder app for Windows (unsigned).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python -m pip install -e ".[packaging]"
pyinstaller --noconfirm --clean packaging/startplanner.spec
Write-Host "Built: $Root\dist\StartPlanner\"
