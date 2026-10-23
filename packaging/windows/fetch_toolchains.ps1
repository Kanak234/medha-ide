# Downloads the OFFLINE toolchains bundled inside the MSIX, verifies checksums,
# and writes toolchains/MANIFEST.json with exact versions + SHA256 of every file.
# WHAT: WinLibs MinGW-w64 GCC (UCRT, 64-bit, gcc/g++/gdb/make)  → toolchains/mingw64
#       Eclipse Temurin JDK 25 LTS (x64)                         → toolchains/jdk
#       Python embeddable (runs students' .py files)             → toolchains/python
# WHY: a fresh lab PC has no compiler; C-Lite ships GCC 6.3 (2016, 32-bit). MEDHĀ
#      ships current 64-bit GCC + Java + Python, all offline after install.
# LICENSES: GCC/GDB GPLv3 (runtime exception), MinGW-w64 ZPL/MIT, Temurin GPLv2+CPE,
#      Python PSF — all allow free redistribution; listed in THIRD_PARTY_LICENSES.md.
$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\..\.."
$tc = Join-Path $root "toolchains"; New-Item -ItemType Directory -Force $tc | Out-Null
$dl = Join-Path $env:RUNNER_TEMP "medha-dl"; New-Item -ItemType Directory -Force $dl | Out-Null
$manifest = @()
function Add-Entry($name, $version, $url, $file, $expected) {
  $sha = (Get-FileHash $file -Algorithm SHA256).Hash.ToLower()
  if ($expected -and ($sha -ne $expected.ToLower())) { throw "$name checksum mismatch: $sha != $expected" }
  $script:manifest += [ordered]@{ name=$name; version=$version; url=$url; sha256=$sha; verified_against_publisher=[bool]$expected }
}
$gh = @{ "User-Agent"="medha-ci"; "Authorization"="Bearer $env:GITHUB_TOKEN" }

# 1) WinLibs (GitHub release asset; GitHub publishes a sha256 digest per asset)
$rel = Invoke-RestMethod "https://api.github.com/repos/brechtsanders/winlibs_mingw/releases/latest" -Headers $gh
$asset = $rel.assets | Where-Object { $_.name -match '^winlibs-x86_64-posix-seh-gcc-.*-mingw-w64ucrt-.*\.zip$' -and $_.name -notmatch 'llvm' } | Select-Object -First 1
$zip = Join-Path $dl $asset.name
Invoke-WebRequest $asset.browser_download_url -OutFile $zip
$digest = if ($asset.digest) { $asset.digest -replace '^sha256:','' } else { $null }
Add-Entry "winlibs-mingw-w64-ucrt" $rel.tag_name $asset.browser_download_url $zip $digest
Expand-Archive $zip -DestinationPath $tc -Force          # → toolchains/mingw64/bin/gcc.exe

# 2) Temurin JDK 25 (Adoptium API returns the official checksum)
$jdk = (Invoke-RestMethod "https://api.adoptium.net/v3/assets/latest/25/hotspot?os=windows&architecture=x64&image_type=jdk")[0]
$jzip = Join-Path $dl $jdk.binary.package.name
Invoke-WebRequest $jdk.binary.package.link -OutFile $jzip
Add-Entry "temurin-jdk" $jdk.version.semver $jdk.binary.package.link $jzip $jdk.binary.package.checksum
Expand-Archive $jzip -DestinationPath $dl -Force
Move-Item (Get-ChildItem $dl -Directory | Where-Object Name -like "jdk-25*" | Select-Object -First 1).FullName (Join-Path $tc "jdk")

# 3) Python embeddable — same minor version the CI used to build MEDHĀ
$pyv = (python -c "import platform;print(platform.python_version())").Trim()
$purl = "https://www.python.org/ftp/python/$pyv/python-$pyv-embed-amd64.zip"
$pzip = Join-Path $dl "python-embed.zip"
Invoke-WebRequest $purl -OutFile $pzip
Add-Entry "python-embeddable" $pyv $purl $pzip $null
Expand-Archive $pzip -DestinationPath (Join-Path $tc "python") -Force

$manifest | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $tc "MANIFEST.json") -Encoding utf8
Get-Content (Join-Path $tc "MANIFEST.json")
