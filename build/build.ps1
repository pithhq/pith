$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "Building PITH binary..."
pyinstaller "$ScriptDir\pith.spec" --clean --distpath "$ProjectRoot\dist\"

$Binary = Join-Path $ProjectRoot "dist\pith.exe"
if (Test-Path $Binary) {
    Write-Host "Build complete: $Binary"
    # TODO: Sign with Sectigo certificate before distribution.
    # signtool sign /fd SHA256 /tr http://timestamp.sectigo.com /td SHA256 /a "$Binary"
    Write-Host "Reminder: sign the binary with Sectigo certificate before release."
} else {
    Write-Error "Build failed: binary not found at $Binary"
    exit 1
}
