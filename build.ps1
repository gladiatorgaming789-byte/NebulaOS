# Run from PowerShell in the repository root.
# Requires WSL 2 with Ubuntu and the dependencies listed in README.md.
$ErrorActionPreference = "Stop"
$RepoPath = (Get-Location).Path
$WslPath = (wsl wslpath -a "$RepoPath").Trim()
if (-not $WslPath) {
    throw "Could not translate repository path to WSL. Is WSL installed?"
}
wsl bash -lc "cd '$WslPath' && chmod +x build.sh && ./build.sh"
if ($LASTEXITCODE -ne 0) {
    throw "NebulaOS build failed with exit code $LASTEXITCODE"
}
Write-Host "ISO created at: $RepoPath\build\NebulaOS.iso"
