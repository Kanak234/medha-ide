import os
import re
import shutil
import subprocess
from pathlib import Path

class BuildSystem:
    def __init__(self, project_dir: str):
        self.project_dir = os.path.abspath(project_dir)
        self.build_dir = os.path.join(self.project_dir, "build")

    def detect(self) -> str | None:
        if os.path.exists(os.path.join(self.project_dir, "CMakeLists.txt")):
            return "cmake"
        elif os.path.exists(os.path.join(self.project_dir, "Makefile")):
            return "make"
        return None

    def configure(self) -> tuple[int, str]:
        kind = self.detect()
        if kind == "cmake":
            cmake_path = shutil.which("cmake") or "/home/kanak/.local/bin/cmake"
            env = dict(os.environ)
            env["PATH"] = f"/home/kanak/.local/bin:{env.get('PATH', '')}"
            res = subprocess.run(
                [cmake_path, "-B", self.build_dir, "-S", self.project_dir],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                env=env
            )
            return (res.returncode, res.stdout + "\n" + res.stderr)
        elif kind == "make":
            return (0, "No configure step required for Makefile")
        return (1, "No build system detected")

    def build(self) -> tuple[int, str, str]:
        kind = self.detect()
        env = dict(os.environ)
        env["PATH"] = f"/home/kanak/.local/bin:{env.get('PATH', '')}"

        if kind == "cmake":
            cmake_path = shutil.which("cmake") or "/home/kanak/.local/bin/cmake"
            res = subprocess.run(
                [cmake_path, "--build", self.build_dir],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                env=env
            )

            # Find generated executable artifact inside build_dir
            artifact_path = ""
            if res.returncode == 0 and os.path.exists(self.build_dir):
                for root, _, files in os.walk(self.build_dir):
                    for f in files:
                        fpath = os.path.join(root, f)
                        if os.access(fpath, os.X_OK) and not f.endswith(".so") and not f.endswith(".a") and not f.startswith("CMake"):
                            artifact_path = fpath
                            break
                    if artifact_path:
                        break

            return (res.returncode, res.stdout + "\n" + res.stderr, artifact_path)

        elif kind == "make":
            make_path = shutil.which("make") or "/usr/bin/make"
            res = subprocess.run(
                [make_path],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                env=env
            )
            return (res.returncode, res.stdout + "\n" + res.stderr, "")

        return (1, "No build system detected", "")
