# PyInstaller spec — MEDHĀ IDE for Windows (one-folder build → MSIX).
# WHAT: bundles medha/ (incl. turbo/runtime), examples/, docs/assets and the
#       offline toolchains/ folder that fetch_toolchains.ps1 downloaded.
# WHY one-folder (not one-file): MSIX installs a folder anyway, and one-file
#       re-extracts ~1 GB of compilers to %TEMP% on every start.
# FLOW: build_msix.ps1 → pyinstaller medha_windows.spec → dist/MEDHA/MEDHA.exe
import os
ROOT = os.path.abspath(os.path.join(SPECPATH, "..", ".."))
datas = [(os.path.join(ROOT, "medha", "turbo", "runtime"), "medha/turbo/runtime"),
         (os.path.join(ROOT, "medha", "turbo", "modernize_explanations.json"), "medha/turbo"),
         (os.path.join(ROOT, "examples"), "examples"),
         (os.path.join(ROOT, "docs", "assets"), "docs/assets")]
if os.path.isdir(os.path.join(ROOT, "toolchains")):
    datas.append((os.path.join(ROOT, "toolchains"), "toolchains"))
a = Analysis([os.path.join(ROOT, "packaging", "windows", "medha_entry.py")], pathex=[ROOT], datas=datas,
             hiddenimports=["medha.app", "PySide6.QtSvg"], excludes=["tkinter"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="MEDHA", console=False,
          icon=os.path.join(ROOT, "packaging", "windows", "medha.ico") if os.path.exists(os.path.join(ROOT, "packaging", "windows", "medha.ico")) else None)
coll = COLLECT(exe, a.binaries, a.datas, name="MEDHA")
