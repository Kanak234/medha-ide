"""
MEDHĀ IDE — settings.py
=======================

WHAT:  Tiny JSON-backed settings store (compiler paths, C/C++ standard, Turbo
       mode, error-explanation language, recent files).
WHY:   We need the same settings file on Linux and Windows without extra
       dependencies, and a file the student (or teacher) can read and fix by hand.
       QSettings would write to the Windows registry, which MSIX virtualises and
       which is hard to inspect — a JSON file in the user data folder is simpler.
USED BY: toolchains.py (custom compiler paths), runner.py (standards, Turbo mode),
       toolchains_dialog.py (the Settings → Toolchains page), app.py.
FLOW:  get("key") reads from an in-memory dict loaded once from settings.json;
       set("key", value) updates the dict and writes the file immediately so a
       power cut never loses a change.
"""

import json
import os
import threading

from medha.platform_info import user_data_dir

# Default values. Every key MEDHĀ reads must have a default here so a missing or
# corrupted settings.json can never crash the IDE.
DEFAULTS = {
    # Per-tool user override, e.g. {"gcc": "D:/mingw64/bin/gcc.exe"}. Empty = auto-detect.
    "tool_paths": {},
    # Language standards passed to gcc / g++ (-std=...).
    "c_std": "gnu17",
    "cpp_std": "gnu++17",
    # Turbo mode: programs that include graphics.h / conio.h / iostream.h are
    # compiled with the PRABHA runtime and adapted (void main → int main) in a temp
    # copy. The student's own file is never changed.
    "turbo_mode": True,
    # Language for beginner error explanations: "en" (English) or "hi" (Hinglish, Roman script).
    "explain_lang": "en",
    # Most-recently opened files (shown in File → Recent).
    "recent_files": [],
}

_lock = threading.Lock()
_cache = None


def settings_path():
    """Absolute path of settings.json (inside the per-user data folder)."""
    return os.path.join(str(user_data_dir()), "settings.json")


def _load():
    """Read settings.json once; fall back to defaults on any error (bad JSON etc.)."""
    global _cache
    if _cache is not None:
        return _cache
    data = {}
    try:
        with open(settings_path(), "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                data = loaded
    except (OSError, ValueError):
        data = {}
    _cache = data
    return _cache


def get(key, default=None):
    """Return a setting, or its DEFAULTS value, or the given default."""
    data = _load()
    if key in data:
        return data[key]
    if key in DEFAULTS:
        # copy mutable defaults so callers cannot modify DEFAULTS by accident
        value = DEFAULTS[key]
        return json.loads(json.dumps(value))
    return default


def set(key, value):  # noqa: A001 — mirrors dict-style API on purpose
    """Store a setting and write settings.json right away (atomic replace)."""
    with _lock:
        data = _load()
        data[key] = value
        path = settings_path()
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)   # atomic on Windows and Linux: no half-written file


def reset_cache_for_tests():
    """Forget the in-memory copy (tests point user_data_dir at a temp folder)."""
    global _cache
    _cache = None
