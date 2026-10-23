"""
MEDHĀ IDE package.

WHAT:  Package marker + version + one PATH tweak.
WHY:   pip installs user tools (clangd, pylsp) into ~/.local/bin on Linux, which is
       often not on PATH for desktop launchers. v1 joined PATH with ':' — that broke
       PATH on Windows (drive letters contain ':'), so it now uses the OS separator
       via platform_info.extend_path, and only on Linux/macOS.
FLOW:  `import medha` (any module) → PATH fixed once → toolchains.py finds tools.
"""
import os

from medha.platform_info import IS_WINDOWS, extend_path

if not IS_WINDOWS:
    extend_path([os.path.expanduser("~/.local/bin")])

__version__ = "2.0.1"
