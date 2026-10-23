# Builds MEDHA.msix from source on Windows (used by .github/workflows/windows-msix.yml,
# also runnable on Kanak's Windows desktop):  pwsh packaging\windows\build_msix.ps1
# FLOW: icons → PyInstaller one-folder → --selftest (real compile with bundled GCC)
#       → layout + AppxManifest (version from medha/__init__.py) → makeappx pack → zip
$ErrorActionPreference = "Stop"
# CI visibility: any failure becomes a GitHub annotation (readable on the run page
# without signing in), including the last lines of output collected in $global:Tail.
$global:Tail = New-Object System.Collections.Generic.List[string]
function Run($step, [scriptblock]$cmd) {
  Write-Host "::group::$step"
  & $cmd 2>&1 | ForEach-Object { $l = "$_"; Write-Host $l; $global:Tail.Add($l); if ($global:Tail.Count -gt 25) { $global:Tail.RemoveAt(0) } }
  $code = $LASTEXITCODE
  Write-Host "::endgroup::"
  if ($code -ne 0) { throw "STEP FAILED: $step (exit $code)" }
}
trap {
  $msg = ($_ | Out-String) + "`n--- last output ---`n" + ($global:Tail -join "`n")
  Write-Host ("::error title=MSIX build failed::" + ($msg -replace "`r?`n", "%0A"))
  exit 1
}
# Identity values are in AppxManifest.xml (copied from Partner Center → Product identity).
$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root
$ver = (python -c "import medha;print(medha.__version__)").Trim()
$msixVer = "$ver.0"                                      # MSIX needs 4 parts: 2.0.0.0
$layout = Join-Path $root "dist\msix-layout"
Remove-Item -Recurse -Force $layout -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$layout\Assets" | Out-Null
Run "icons" { python packaging\windows\make_icons.py docs\assets\logo-mark.svg "$layout\Assets" }
Run "PyInstaller build" { python -m PyInstaller --noconfirm --distpath dist packaging\windows\medha_windows.spec }
Run "MEDHA.exe --selftest" { & dist\MEDHA\MEDHA.exe --selftest }
Copy-Item -Recurse dist\MEDHA "$layout\MEDHA"
(Get-Content packaging\windows\AppxManifest.xml -Raw).Replace("__VERSION__", $msixVer) | Set-Content "$layout\AppxManifest.xml" -Encoding utf8
# MSIX rejects some file names (makeappx error 0x8007007b). Drop NSIS/7z leftovers
# whose names start with '$', then report any remaining name outside the safe set.
Get-ChildItem $layout -Recurse -Force | Where-Object { $_.Name -like '$*' } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
$bad = Get-ChildItem $layout -Recurse -Force | Where-Object { $_.Name -notmatch '^[A-Za-z0-9_.\- ()+~@,=\[\]]+$' -or $_.Name -match '[. ]$' -or $_.Name -match '^(CON|PRN|AUX|NUL|COM\d|LPT\d)(\..*)?$' }
if ($bad) { Write-Host ("::warning title=Unusual file names in package::" + (($bad | ForEach-Object { $_.FullName.Substring($layout.Length) }) -join "%0A")) }
$makeappx = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\makeappx.exe" | Sort-Object FullName -Descending | Select-Object -First 1
Run "makeappx pack" { & $makeappx.FullName pack /v /d $layout /p "dist\MEDHA-$ver.msix" /o }
Compress-Archive -Path dist\MEDHA -DestinationPath "dist\MEDHA-$ver-portable.zip" -Force
Get-ChildItem dist\*.msix, dist\*.zip | ForEach-Object { "{0}  {1:N1} MB" -f $_.Name, ($_.Length / 1MB) }
