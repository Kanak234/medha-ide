import os

if "/home/kanak/.local/bin" not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"/home/kanak/.local/bin:{os.environ.get('PATH', '')}"

__version__ = "1.0.0"
