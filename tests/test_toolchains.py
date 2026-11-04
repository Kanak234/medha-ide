"""
Unit tests for medha/toolchains.py — Tool detection and version reporting.

Tests cover:
- Tool dataclass and found property
- find() cache behavior
- Version probing (success, failure, JAVA_TOOL_OPTIONS noise)
- Priority order: settings → bundled → PATH → common locations
- require() raises ToolMissing with helpful hints
- Language standard detection based on GCC version
- report() returns all known tools
"""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from medha.toolchains import (
    Tool,
    ToolMissing,
    TOOLS,
    WINDOWS_COMMON,
    COMMON_GROUP,
    _cache,
    _probe_version,
    clear_cache,
    find,
    require,
    gcc_major,
    supported_c_standards,
    supported_cpp_standards,
    report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_cache():
    """Clear the toolchains cache before each test."""
    clear_cache()
    yield
    clear_cache()


# ---------------------------------------------------------------------------
# Tool dataclass tests
# ---------------------------------------------------------------------------

class TestToolDataclass:
    def test_tool_found_property(self):
        """Tool.found is True when path is set, False otherwise."""
        tool_with_path = Tool("gcc", path="/usr/bin/gcc", version="12.2.0", source="PATH")
        tool_without_path = Tool("gcc")
        assert tool_with_path.found is True
        assert tool_without_path.found is False

    def test_tool_repr(self):
        """Tool has readable representation."""
        tool = Tool("gcc", path="/usr/bin/gcc", version="12.2.0", source="PATH")
        repr_str = repr(tool)
        assert "gcc" in repr_str
        assert "/usr/bin/gcc" in repr_str
        assert "12.2.0" in repr_str


# ---------------------------------------------------------------------------
# Version probing tests
# ---------------------------------------------------------------------------

class TestProbeVersion:
    @patch("subprocess.run")
    def test_probe_version_success(self, mock_run):
        """_probe_version returns first non-empty line of output."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="gcc (Ubuntu 12.2.0) 12.2.0\nCopyright (C) 2022...\n",
            stderr=""
        )
        version = _probe_version("/usr/bin/gcc", ["--version"])
        assert version == "gcc (Ubuntu 12.2.0) 12.2.0"

    @patch("subprocess.run")
    def test_probe_version_stderr_fallback(self, mock_run):
        """_probe_version reads stderr when stdout is empty (java/javac)."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="javac 17.0.5\n"
        )
        version = _probe_version("/usr/bin/javac", ["-version"])
        assert version == "javac 17.0.5"

    @patch("subprocess.run")
    def test_probe_version_skips_java_tool_options(self, mock_run):
        """_probe_version skips 'Picked up JAVA_TOOL_OPTIONS' lines."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="Picked up JAVA_TOOL_OPTIONS: -Xmx512m\njava 17.0.5\n"
        )
        version = _probe_version("/usr/bin/java", ["-version"])
        assert version == "java 17.0.5"

    @patch("subprocess.run")
    def test_probe_version_failure_returns_none(self, mock_run):
        """_probe_version returns None when command fails or not found."""
        mock_run.side_effect = FileNotFoundError()
        version = _probe_version("/nonexistent/gcc", ["--version"])
        assert version is None

    @patch("subprocess.run")
    def test_probe_version_empty_output_returns_none(self, mock_run):
        """_probe_version returns None when output is empty and returncode != 0."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        version = _probe_version("/usr/bin/gcc", ["--version"])
        assert version is None


# ---------------------------------------------------------------------------
# find() cache tests
# ---------------------------------------------------------------------------

class TestFindCache:
    def test_find_caches_result(self):
        """find() caches results in _cache."""
        with patch("medha.toolchains._probe_version", return_value="12.2.0"):
            with patch("shutil.which", return_value="/usr/bin/gcc"):
                tool1 = find("gcc")
                tool2 = find("gcc")
                assert tool1 is tool2  # Same object from cache
                assert "gcc" in _cache

    def test_clear_cache_empties_cache(self):
        """clear_cache() removes all cached entries."""
        with patch("medha.toolchains._probe_version", return_value="12.2.0"):
            with patch("shutil.which", return_value="/usr/bin/gcc"):
                find("gcc")
                assert "gcc" in _cache
        clear_cache()
        assert "gcc" not in _cache

    def test_find_refresh_bypasses_cache(self):
        """find(refresh=True) bypasses cache and re-probes."""
        with patch("medha.toolchains._probe_version") as mock_probe:
            mock_probe.side_effect = ["12.2.0", "13.1.0"]
            with patch("shutil.which", return_value="/usr/bin/gcc"):
                tool1 = find("gcc")
                tool2 = find("gcc", refresh=True)
                assert tool1.version == "12.2.0"
                assert tool2.version == "13.1.0"
                assert mock_probe.call_count == 2


# ---------------------------------------------------------------------------
# Priority order tests
# ---------------------------------------------------------------------------

class TestFindPriority:
    @patch("medha.toolchains.settings.get")
    @patch("medha.toolchains._probe_version", return_value="12.2.0")
    def test_settings_path_wins(self, mock_probe, mock_settings_get):
        """Explicit user path from settings takes priority."""
        mock_settings_get.return_value = {"gcc": "/custom/gcc"}
        with patch("os.path.isfile", return_value=True):
            tool = find("gcc")
            assert tool.path == "/custom/gcc"
            assert tool.source == "settings"

    @patch("medha.toolchains.settings.get", return_value={})
    @patch("medha.toolchains.bundled_toolchains_dir")
    @patch("medha.toolchains._probe_version", return_value="12.2.0")
    def test_bundled_before_path(self, mock_probe, mock_bundled_dir, mock_settings):
        """Bundled toolchain is preferred over system PATH."""
        from pathlib import Path
        mock_bundled_dir.return_value = Path("/app/toolchains")
        # Mock EXE suffix for the platform (imported at module level in toolchains)
        with patch("medha.toolchains.EXE", ".exe"):
            with patch("os.path.isfile") as mock_isfile:
                # Path() gives native separators, so build the expectation the same way (Windows uses "\\").
                expected = str(Path("/app/toolchains") / "mingw64" / "bin" / "gcc.exe")
                mock_isfile.side_effect = lambda p: str(p) == expected
                with patch("shutil.which", return_value="/usr/bin/gcc"):
                    tool = find("gcc")
                    assert str(tool.path) == expected
                    assert tool.source == "bundled"

    @patch("medha.toolchains.settings.get", return_value={})
    @patch("medha.toolchains.bundled_toolchains_dir")
    @patch("medha.toolchains._probe_version", return_value="12.2.0")
    def test_path_before_common(self, mock_probe, mock_bundled_dir, mock_settings):
        """System PATH is preferred over common install locations."""
        from pathlib import Path
        mock_bundled_dir.return_value = Path("/app/toolchains")
        with patch("os.path.isfile", return_value=False):
            with patch("shutil.which", return_value="/usr/bin/gcc"):
                with patch("glob.glob", return_value=["C:/mingw64/bin"]):
                    tool = find("gcc")
                    assert tool.path == "/usr/bin/gcc"
                    assert tool.source == "PATH"


# ---------------------------------------------------------------------------
# require() tests
# ---------------------------------------------------------------------------

class TestRequire:
    def test_require_raises_toolmissing_when_not_found(self):
        """require() raises ToolMissing with hint when tool not found."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc")  # Not found
            with pytest.raises(ToolMissing) as exc:
                require("gcc")
            assert "gcc" in str(exc.value)
            assert exc.value.tool == "gcc"
            assert exc.value.hint is not None

    def test_require_returns_path_when_found(self):
        """require() returns tool path when found."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc", path="/usr/bin/gcc", version="12.2.0", source="PATH")
            path = require("gcc")
            assert path == "/usr/bin/gcc"


# ---------------------------------------------------------------------------
# GCC version and language standards tests
# ---------------------------------------------------------------------------

class TestGccVersionAndStandards:
    def test_gcc_major_parses_version(self):
        """gcc_major() extracts major version from version string."""
        tool = Tool("gcc", version="gcc (Ubuntu 12.2.0) 12.2.0")
        assert gcc_major(tool) == 12

        tool = Tool("gcc", version="gcc (GCC) 13.1.0")
        assert gcc_major(tool) == 13

        tool = Tool("gcc", version="")
        assert gcc_major(tool) is None

    def test_supported_c_standards_includes_basics(self):
        """supported_c_standards() always includes C89 through C17."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc", version="gcc 8.0.0")
            stds = supported_c_standards()
            assert "c89" in stds
            assert "c99" in stds
            assert "c11" in stds
            assert "c17" in stds
            assert "gnu17" in stds

    def test_supported_c_standards_c2x_for_gcc9(self):
        """GCC 9+ supports c2x."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc", version="gcc 9.0.0")
            stds = supported_c_standards()
            assert "c2x" in stds

    def test_supported_c_standards_c23_for_gcc14(self):
        """GCC 14+ supports c23."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc", version="gcc 14.0.0")
            stds = supported_c_standards()
            assert "c23" in stds

    def test_supported_cpp_standards_includes_basics(self):
        """supported_cpp_standards() always includes C++98 through C++17."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("g++", version="g++ 8.0.0")
            stds = supported_cpp_standards()
            assert "c++98" in stds
            assert "c++11" in stds
            assert "c++14" in stds
            assert "c++17" in stds

    def test_supported_cpp_standards_cpp20_for_gcc10(self):
        """GCC 10+ supports c++20."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("g++", version="g++ 10.0.0")
            stds = supported_cpp_standards()
            assert "c++20" in stds

    def test_supported_cpp_standards_cpp23_for_gcc14(self):
        """GCC 14+ supports c++23."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("g++", version="g++ 14.0.0")
            stds = supported_cpp_standards()
            assert "c++23" in stds


# ---------------------------------------------------------------------------
# report() tests
# ---------------------------------------------------------------------------

class TestReport:
    def test_report_returns_all_known_tools(self):
        """report() returns a list of (name, Tool) for every tool in TOOLS."""
        with patch("medha.toolchains.find") as mock_find:
            mock_find.return_value = Tool("gcc")
            result = report()
            assert len(result) == len(TOOLS)
            for name, tool in result:
                assert name in TOOLS
                assert isinstance(tool, Tool)


# ---------------------------------------------------------------------------
# Windows common paths tests
# ---------------------------------------------------------------------------

class TestWindowsCommonPaths:
    def test_windows_common_has_expected_groups(self):
        """WINDOWS_COMMON contains expected tool groups."""
        assert "mingw" in WINDOWS_COMMON
        assert "jdk" in WINDOWS_COMMON
        assert "python" in WINDOWS_COMMON
        assert "clangd" in WINDOWS_COMMON
        assert "git" in WINDOWS_COMMON
        assert "cppcheck" in WINDOWS_COMMON

    def test_common_group_maps_all_tools(self):
        """COMMON_GROUP maps every tool in TOOLS to a Windows common group."""
        for tool_name in TOOLS:
            assert tool_name in COMMON_GROUP