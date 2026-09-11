import os
import tempfile
import subprocess
import pytest
from pathlib import Path
from medha.git_backend import GitBackend

def test_git_backend_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        git = GitBackend(tmpdir)
        git.init()
        assert os.path.exists(os.path.join(tmpdir, ".git"))

        # Configure test author
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)

        # Status on empty repo
        assert git.status() == []

        # Create a file and check status
        test_file = os.path.join(tmpdir, "sample.txt")
        Path(test_file).write_text("initial content\n")
        assert "sample.txt" in git.status()

        # Stage and commit
        git.stage(["sample.txt"])
        sha = git.commit("Initial commit")
        assert len(sha) == 40
        assert git.status() == []

        # Log
        log_entries = git.log(5)
        assert len(log_entries) == 1
        assert "Initial commit" in log_entries[0]

        # Diff
        Path(test_file).write_text("modified content\n")
        diff_output = git.diff("sample.txt")
        assert "+modified content" in diff_output
        assert "-initial content" in diff_output
