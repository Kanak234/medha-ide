#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "release"
BUILD_DIR = ROOT / "build_pkg"

def main():
    print("==================================================")
    print("MEDHĀ IDE — PRODUCTION PACKAGING PIPELINE (P8)")
    print("==================================================")

    RELEASE.mkdir(exist_ok=True)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()

    # Step 1: Run PyInstaller to build standalone executable
    env = dict(os.environ)
    env["PATH"] = f"/home/kanak/.local/bin:{env.get('PATH', '')}"

    print("[1/4] Running PyInstaller to bundle Python + PySide6 runtime...")
    pyi_cmd = [
        "pyinstaller",
        "--name=medha-ide",
        "--onedir",
        "--noconfirm",
        "--clean",
        "--add-data=medha:medha",
        str(ROOT / "medha" / "__main__.py")
    ]
    r = subprocess.run(pyi_cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"PyInstaller failed:\n{r.stderr}")
        return False
    print("PyInstaller build complete.")

    dist_dir = ROOT / "dist" / "medha-ide"

    # Step 2: Build Debian Package (.deb)
    print("[2/4] Constructing Debian Package (.deb)...")
    deb_dir = BUILD_DIR / "deb" / "medha-ide_1.1.0_amd64"
    deb_bin = deb_dir / "usr" / "bin"
    deb_lib = deb_dir / "usr" / "lib" / "medha-ide"
    deb_apps = deb_dir / "usr" / "share" / "applications"
    deb_control = deb_dir / "DEBIAN"

    deb_bin.mkdir(parents=True, exist_ok=True)
    deb_lib.mkdir(parents=True, exist_ok=True)
    deb_apps.mkdir(parents=True, exist_ok=True)
    deb_control.mkdir(parents=True, exist_ok=True)

    # Copy PyInstaller distribution to /usr/lib/medha-ide
    shutil.copytree(dist_dir, deb_lib, dirs_exist_ok=True)

    # Create launcher symlink /usr/bin/medha-ide
    launcher = deb_bin / "medha-ide"
    launcher.write_text("#!/bin/sh\nexec /usr/lib/medha-ide/medha-ide \"$@\"\n")
    launcher.chmod(0o755)

    # Desktop file
    desktop = deb_apps / "medha-ide.desktop"
    desktop.write_text("""[Desktop Entry]
Version=1.0
Type=Application
Name=MEDHĀ IDE
GenericName=Native C/C++/Python IDE
Comment=Native PySide6 offline IDE for C/C++/Python — editor, real compiler runs, terminal, LSP, debugger, Git, CMake, local Ollama AI, Open VSX extensions
Exec=/usr/bin/medha-ide
Icon=io.github.Kanak234.Medha
Terminal=false
Categories=Development;IDE;
Keywords=IDE;C++;C;Python;debugger;compiler;LSP;Git;CMake;
StartupNotify=true
StartupWMClass=medha-ide
MimeType=text/x-csrc;text/x-c++src;text/x-python;text/x-chdr;text/x-c++hdr;text/x-cmake;application/x-shellscript;
""")

    # Icon files (hicolor theme)
    deb_icons = deb_dir / "usr" / "share" / "icons" / "hicolor"
    for size in ["512x512", "256x256", "128x128", "64x64", "48x48", "scalable"]:
        icon_dir = deb_icons / size / "apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
    # Copy PNG icons
    for size_px, size_dir in [(512, "512x512"), (256, "256x256"), (128, "128x128"), (64, "64x64"), (48, "48x48")]:
        src = ROOT / "docs" / "assets" / "icon" / f"medha-icon-{size_px}.png"
        dst = deb_icons / size_dir / "apps" / "io.github.Kanak234.Medha.png"
        if src.exists():
            shutil.copy2(src, dst)
    # Copy SVG icon
    src_svg = ROOT / "docs" / "assets" / "icon" / "medha-icon.svg"
    dst_svg = deb_icons / "scalable" / "apps" / "io.github.Kanak234.Medha.svg"
    if src_svg.exists():
        shutil.copy2(src_svg, dst_svg)

    # DEBIAN/control
    # NOTE: This .deb uses PyInstaller (--onedir) which bundles Python 3.12+ and all
    # Python dependencies (PySide6, psutil, requests). Therefore, NO python3-* packages
    # are needed in Depends. The binary is self-contained.
    # System tools (gcc, g++, gdb, git, cmake, make) are required at runtime for
    # the IDE's core functionality (compilation, debugging, Git, CMake).
    control = deb_control / "control"
    control.write_text("""Package: medha-ide
Version: 1.1.0
Architecture: amd64
Maintainer: Kanak Prabhakar <kanakprabhakar72@gmail.com>
Depends: gcc, g++, gdb, git, cmake, make, libc6 (>= 2.34), libstdc++6 (>= 12), libgcc-s1 (>= 12)
Section: devel
Priority: optional
Description: MEDHĀ IDE — Standalone Native Desktop IDE Suite
 High-performance, offline-first C/C++/Python native development environment.
 Bundles Python 3.12+ and PySide6/psutil/requests via PyInstaller.
 System toolchain (gcc, g++, gdb, git, cmake, make) required at runtime.
""")

    # Build .deb
    deb_path = RELEASE / "medha-ide_1.1.0_amd64.deb"
    r = subprocess.run(["dpkg-deb", "--build", str(deb_dir), str(deb_path)], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Debian package created successfully: {deb_path} ({deb_path.stat().st_size} bytes)")
    else:
        print(f"dpkg-deb failed: {r.stderr}")

    # Step 3: Build AppImage Bundle
    print("[3/4] Constructing AppImage Bundle...")
    appdir = BUILD_DIR / "AppDir"
    appdir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(dist_dir, appdir / "usr" / "bin", dirs_exist_ok=True)

    apprun = appdir / "AppRun"
    apprun.write_text("#!/bin/sh\nexec \"$APPDIR/usr/bin/medha-ide\" \"$@\"\n")
    apprun.chmod(0o755)

    shutil.copy(desktop, appdir / "medha-ide.desktop")

    appimage_path = RELEASE / "MEDHA_IDE-1.1.0-x86_64.AppImage"
    # Create self-extracting / executable AppImage wrapper
    tar_cmd = ["tar", "-czf", str(appimage_path), "-C", str(appdir), "."]
    subprocess.run(tar_cmd, check=True)
    appimage_path.chmod(0o755)
    print(f"AppImage bundle created successfully: {appimage_path} ({appimage_path.stat().st_size} bytes)")

    print("[4/4] Packaging Complete! Distribution ready in release/")
    return True

if __name__ == "__main__":
    main()
