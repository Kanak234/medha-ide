# PyInstaller spec — MEDHĀ IDE for Windows (one-folder build → MSIX).
# WHAT: bundles medha/ (incl. turbo/runtime), examples/, docs/assets and the
#       offline toolchains/ folder that fetch_toolchains.ps1 downloaded.
# WHY one-folder (not one-file): MSIX installs a folder anyway, and one-file
#       re-extracts ~1 GB of compilers to %TEMP% on every start.
# FLOW: build_msix.ps1 → pyinstaller medha_windows.spec → dist/MEDHA/MEDHA.exe
import ast
import os
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct
ROOT = os.path.abspath(os.path.join(SPECPATH, "..", ".."))
# Read the package version without importing GUI code during the Windows build.
with open(os.path.join(ROOT, "medha", "__init__.py"), encoding="utf-8") as source:
    version_tree = ast.parse(source.read())
VERSION = next(ast.literal_eval(node.value) for node in version_tree.body
               if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
               and target.id == "__version__" for target in node.targets))
version_tuple = tuple(int(part) for part in VERSION.split(".")) + (0,)
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_tuple, prodvers=version_tuple, mask=0x3f,
                     flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[StringFileInfo([StringTable('040904B0', [
        StringStruct('CompanyName', 'Kanak Prabhakar'),
        StringStruct('FileDescription', 'MEDHĀ IDE'),
        StringStruct('FileVersion', VERSION),
        StringStruct('ProductName', 'MEDHĀ IDE'),
        StringStruct('ProductVersion', VERSION),
        StringStruct('OriginalFilename', 'MEDHA.exe'),
    ])]), VarFileInfo([VarStruct('Translation', [1033, 1200])])])
# Explorer's Details tab and MSIX now agree with About on the release version.
datas = [(os.path.join(ROOT, "medha", "workbench.qss"), "medha"),
         (os.path.join(ROOT, "medha", "turbo", "runtime"), "medha/turbo/runtime"),
         (os.path.join(ROOT, "medha", "turbo", "modernize_explanations.json"), "medha/turbo"),
         (os.path.join(ROOT, "examples"), "examples"),
         (os.path.join(ROOT, "docs", "assets"), "docs/assets")]
if os.path.isdir(os.path.join(ROOT, "toolchains")):
    datas.append((os.path.join(ROOT, "toolchains"), "toolchains"))
a = Analysis([os.path.join(ROOT, "packaging", "windows", "medha_entry.py")], pathex=[ROOT], datas=datas,
             hiddenimports=["medha.app", "PySide6.QtSvg", "winpty", "psutil"], excludes=["tkinter"])
pyz = PYZ(a.pure)
# ConPTY survives in console-hosted Python but exited in the windowed frozen
# build. Keep a console host for process semantics, hidden before the GUI opens.
# PyInstaller hides only consoles it owns, preserving an existing user console.
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="MEDHA", console=True, hide_console="hide-early", version=version_info,
          icon=os.path.join(ROOT, "packaging", "windows", "medha.ico") if os.path.exists(os.path.join(ROOT, "packaging", "windows", "medha.ico")) else None)
coll = COLLECT(exe, a.binaries, a.datas, name="MEDHA")
