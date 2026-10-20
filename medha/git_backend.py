import os
import subprocess
from pathlib import Path

class GitBackend:
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)

    def _run_git(self, args: list[str]) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        local_bin = os.path.expanduser("~/.local/bin")
        env["PATH"] = f"{local_bin}:{env.get('PATH', '')}"
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            env=env
        )

    def init(self) -> None:
        self._run_git(["init"])

    def status(self) -> list[str]:
        res = self._run_git(["status", "--porcelain"])
        files = []
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if len(line) > 3:
                    files.append(line[3:].strip())
        return files

    def stage(self, paths: list[str]) -> None:
        if paths:
            self._run_git(["add"] + paths)

    def commit(self, message: str) -> str:
        res = self._run_git(["commit", "-m", message])
        if res.returncode == 0:
            rev = self._run_git(["rev-parse", "HEAD"])
            return rev.stdout.strip()
        return ""

    def log(self, n: int = 10) -> list[str]:
        res = self._run_git(["log", f"-n{n}", "--oneline"])
        if res.returncode == 0:
            return res.stdout.splitlines()
        return []

    def diff(self, path: str) -> str:
        res = self._run_git(["diff", path])
        return res.stdout
