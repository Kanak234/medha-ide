# Builds MEDHA.msix from source on Windows (used by .github/workflows/windows-msix.yml,
# also runnable on Kanak's Windows desktop):  pwsh packaging\windows\build_msix.ps1
# FLOW: icons → PyInstaller one-folder → --selftest (real compile with bundled GCC)
#       → layout + AppxManifest (version from medha/__init__.py) → makeappx pack → zip
$ErrorActionPreference = "Stop"
# Identity values are in AppxManifest.xml (copied from Partner Center → Product identity).
$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root
$ver = (python -c "import medha;print(medha.__version__)").Trim()
$msixVer = "$ver.0"                                      # MSIX needs 4 parts: 2.0.0.0
$layout = Join-Path $root "dist\msix-layout"
Remove-Item -Recurse -Force $layout -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$layout\Assets" | Out-Null
python packaging\windows\make_icons.py docs\assets\logo-mark.svg "$layout\Assets"
python -m PyInstaller --noconfirm --distpath dist packaging\windows\medha_windows.spec
& dist\MEDHA\MEDHA.exe --selftest | Tee-Object -Variable st
if ($LASTEXITCODE -ne 0) { throw "MEDHA.exe --selftest failed" }
Copy-Item -Recurse dist\MEDHA "$layout\MEDHA"
(Get-Content packaging\windows\AppxManifest.xml -Raw).Replace("__VERSION__", $msixVer) | Set-Content "$layout\AppxManifest.xml" -Encoding utf8
$makeappx = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\makeappx.exe" | Sort-Object FullName -Descending | Select-Object -First 1
& $makeappx.FullName pack /d $layout /p "dist\MEDHA-$ver.msix" /o
if ($LASTEXITCODE -ne 0) { throw "makeappx failed" }
Compress-Archive -Path dist\MEDHA -DestinationPath "dist\MEDHA-$ver-portable.zip" -Force
Get-ChildItem dist\*.msix, dist\*.zip | ForEach-Object { "{0}  {1:N1} MB" -f $_.Name, ($_.Length / 1MB) }
