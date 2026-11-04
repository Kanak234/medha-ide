"""
Unit tests for medha/project_manager.py — Project & Workspace Manager.

Tests cover:
- MedhaProject serialization (to_dict/from_dict)
- MedhaProject save/load round-trip
- WorkspaceManager project discovery
- ProjectExplorerWidget tree population
- Virtual folder structure (Sources, Headers, Resources, Build Configs)
- Context menu actions
"""

import json
import os
import tempfile
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from medha.project_manager import MedhaProject, WorkspaceManager, ProjectExplorerWidget


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as d:
        yield d


# ---------------------------------------------------------------------------
# MedhaProject tests
# ---------------------------------------------------------------------------

class TestMedhaProject:
    def test_default_initialization(self):
        """MedhaProject initializes with sensible defaults."""
        proj = MedhaProject(name="TestProj", project_dir="/tmp/test")
        assert proj.name == "TestProj"
        assert proj.project_dir == "/tmp/test"
        assert proj.target_type == "executable"
        assert proj.active_config == "Debug"
        assert "Debug" in proj.build_configs
        assert "Release" in proj.build_configs
        assert proj.sources == []
        assert proj.headers == []
        assert proj.resources == []
        assert proj.include_paths == ["."]

    def test_to_dict_contains_all_fields(self):
        """to_dict() returns a dict with all project fields."""
        proj = MedhaProject(name="TestProj", project_dir="/tmp/test")
        proj.sources = ["main.c", "utils.c"]
        proj.headers = ["utils.h"]
        data = proj.to_dict()
        assert data["name"] == "TestProj"
        assert data["version"] == "1.0"
        assert data["target_type"] == "executable"
        assert data["active_config"] == "Debug"
        assert data["sources"] == ["main.c", "utils.c"]
        assert data["headers"] == ["utils.h"]
        assert "build_configs" in data

    def test_from_dict_restores_all_fields(self, temp_dir):
        """from_dict() restores all fields from saved data."""
        proj_file = os.path.join(temp_dir, "TestProj.medhaproj")
        data = {
            "name": "TestProj",
            "version": "1.0",
            "target_type": "static_lib",
            "active_config": "Release",
            "sources": ["main.c", "lib.c"],
            "headers": ["lib.h"],
            "resources": ["icon.png"],
            "include_paths": [".", "include"],
            "build_configs": {
                "Debug": {"compiler_flags": ["-g"], "linker_flags": [], "output_dir": "bin/Debug", "binary_name": "TestProj"},
                "Release": {"compiler_flags": ["-O2"], "linker_flags": [], "output_dir": "bin/Release", "binary_name": "TestProj"},
            }
        }
        proj = MedhaProject.from_dict(data, proj_file)
        assert proj.name == "TestProj"
        assert proj.target_type == "static_lib"
        assert proj.active_config == "Release"
        assert proj.sources == ["main.c", "lib.c"]
        assert proj.headers == ["lib.h"]
        assert proj.resources == ["icon.png"]
        assert proj.include_paths == [".", "include"]
        assert proj.build_configs["Debug"]["compiler_flags"] == ["-g"]

    def test_save_and_load_roundtrip(self, temp_dir):
        """save() followed by load() preserves all data."""
        proj_file = os.path.join(temp_dir, "TestProj.medhaproj")
        orig = MedhaProject(name="TestProj", project_dir=temp_dir)
        orig.sources = ["main.c", "utils.c"]
        orig.headers = ["utils.h"]
        orig.target_type = "shared_lib"
        orig.active_config = "Release"
        assert orig.save() is True

        loaded = MedhaProject.load(proj_file)
        assert loaded is not None
        assert loaded.name == "TestProj"
        assert loaded.target_type == "shared_lib"
        assert loaded.active_config == "Release"
        assert loaded.sources == ["main.c", "utils.c"]
        assert loaded.headers == ["utils.h"]

    def test_load_nonexistent_file_returns_none(self):
        """load() returns None for non-existent files."""
        assert MedhaProject.load("/nonexistent/path.medhaproj") is None

    def test_save_without_path_returns_false(self):
        """save() returns False when project_file_path is not set."""
        proj = MedhaProject(name="TestProj")  # No project_dir
        assert proj.save() is False


# ---------------------------------------------------------------------------
# WorkspaceManager tests
# ---------------------------------------------------------------------------

class TestWorkspaceManager:
    def test_load_workspace_discovers_projects(self, temp_dir):
        """load_workspace() finds .medhaproj files in subdirectories."""
        # Create a project file
        proj_dir = os.path.join(temp_dir, "MyProject")
        os.makedirs(proj_dir)
        proj_file = os.path.join(proj_dir, "MyProject.medhaproj")
        proj = MedhaProject(name="MyProject", project_dir=proj_dir)
        proj.sources = ["main.c"]
        proj.save()

        ws = WorkspaceManager()
        ws.load_workspace(temp_dir)
        assert len(ws.projects) == 1
        assert ws.projects[0].name == "MyProject"
        assert ws.projects[0].sources == ["main.c"]

    def test_create_project_creates_files(self, temp_dir):
        """create_project() creates directory, main.c, and .medhaproj file."""
        ws = WorkspaceManager(temp_dir)
        proj = ws.create_project("NewProj", os.path.join(temp_dir, "NewProj"))
        assert proj.name == "NewProj"
        assert os.path.exists(os.path.join(temp_dir, "NewProj", "main.c"))
        assert os.path.exists(os.path.join(temp_dir, "NewProj", "NewProj.medhaproj"))
        # main.c should have boilerplate
        with open(os.path.join(temp_dir, "NewProj", "main.c")) as f:
            content = f.read()
        assert "NewProj" in content
        assert "main" in content


# ---------------------------------------------------------------------------
# ProjectExplorerWidget tests
# ---------------------------------------------------------------------------

class TestProjectExplorerWidget:
    def test_widget_creation(self, qapp, temp_dir):
        """ProjectExplorerWidget can be instantiated."""
        widget = ProjectExplorerWidget(temp_dir)
        assert widget is not None
        assert widget.tree is not None
        assert widget.model is not None

    def test_refresh_tree_populates_model(self, qapp, temp_dir):
        """refresh_tree() populates the model with workspace and projects."""
        # Create a project
        proj_dir = os.path.join(temp_dir, "TestProj")
        os.makedirs(proj_dir)
        proj_file = os.path.join(proj_dir, "TestProj.medhaproj")
        proj = MedhaProject(name="TestProj", project_dir=proj_dir)
        proj.sources = ["main.c", "foo.c"]
        proj.headers = ["foo.h"]
        proj.resources = ["data.txt"]
        proj.save()

        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        # Check root item
        root = widget.model.invisibleRootItem()
        ws_node = root.child(0)
        assert "Workspace:" in ws_node.text()

        # Check project node
        proj_node = ws_node.child(0)
        assert "TestProj" in proj_node.text()
        assert "Debug" in proj_node.text()  # Active config shown

        # Check virtual folders
        sources_node = None
        headers_node = None
        resources_node = None
        targets_node = None
        for i in range(proj_node.rowCount()):
            child = proj_node.child(i)
            if "Sources" in child.text():
                sources_node = child
            elif "Headers" in child.text():
                headers_node = child
            elif "Resources" in child.text():
                resources_node = child
            elif "Build Configurations" in child.text():
                targets_node = child

        assert sources_node is not None
        assert headers_node is not None
        assert resources_node is not None
        assert targets_node is not None

        # Check sources
        assert sources_node.rowCount() == 2
        assert "main.c" in sources_node.child(0).text()
        assert "foo.c" in sources_node.child(1).text()

        # Check headers
        assert headers_node.rowCount() == 1
        assert "foo.h" in headers_node.child(0).text()

        # Check resources
        assert resources_node.rowCount() == 1
        assert "data.txt" in resources_node.child(0).text()

        # Check build configs
        assert targets_node.rowCount() == 2
        config_names = [targets_node.child(i).text().strip() for i in range(2)]
        # Config names have checkmark prefix for active config
        assert any("Debug" in name for name in config_names)
        assert any("Release" in name for name in config_names)

    def test_fallback_population_when_no_projects(self, qapp, temp_dir):
        """When no .medhaproj exists, raw directory is scanned as fallback."""
        # Create some source files directly
        with open(os.path.join(temp_dir, "main.c"), "w") as f:
            f.write("int main() { return 0; }")
        with open(os.path.join(temp_dir, "util.h"), "w") as f:
            f.write("#pragma once")
        with open(os.path.join(temp_dir, "readme.txt"), "w") as f:
            f.write("Hello")

        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        root = widget.model.invisibleRootItem()
        ws_node = root.child(0)
        proj_node = ws_node.child(0)

        # Should have created a fallback project
        assert os.path.basename(temp_dir) in proj_node.text()

        # Check sources/headers/resources populated from filesystem
        sources_node = proj_node.child(0)  # Sources
        headers_node = proj_node.child(1)  # Headers
        resources_node = proj_node.child(2)  # Resources

        assert sources_node.rowCount() == 1
        assert "main.c" in sources_node.child(0).text()

        assert headers_node.rowCount() == 1
        assert "util.h" in headers_node.child(0).text()

        assert resources_node.rowCount() == 1
        assert "readme.txt" in resources_node.child(0).text()

    def test_double_click_emits_file_selected(self, qapp, temp_dir):
        """Double-clicking a file emits file_selected signal."""
        proj_dir = os.path.join(temp_dir, "TestProj")
        os.makedirs(proj_dir)
        # Create the actual source file
        main_c_path = os.path.join(proj_dir, "main.c")
        with open(main_c_path, "w") as f:
            f.write("int main() { return 0; }")
        proj_file = os.path.join(proj_dir, "TestProj.medhaproj")
        proj = MedhaProject(name="TestProj", project_dir=proj_dir)
        proj.sources = ["main.c"]
        proj.save()

        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        # Find the main.c item
        root = widget.model.invisibleRootItem()
        ws_node = root.child(0)
        proj_node = ws_node.child(0)
        sources_node = proj_node.child(0)
        file_node = sources_node.child(0)

        # Mock signal
        with patch.object(widget, "file_selected") as mock_signal:
            widget.on_double_click(widget.model.indexFromItem(file_node))
            mock_signal.emit.assert_called_once()
            called_path = mock_signal.emit.call_args[0][0]
            assert called_path.endswith("main.c")

    def test_double_click_config_changes_active(self, qapp, temp_dir):
        """Double-clicking a build config changes active config and saves."""
        proj_dir = os.path.join(temp_dir, "TestProj")
        os.makedirs(proj_dir)
        proj_file = os.path.join(proj_dir, "TestProj.medhaproj")
        proj = MedhaProject(name="TestProj", project_dir=proj_dir)
        proj.save()

        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        # Find the Release config item
        root = widget.model.invisibleRootItem()
        ws_node = root.child(0)
        proj_node = ws_node.child(0)
        targets_node = proj_node.child(3)  # Build Configurations
        release_node = None
        for i in range(targets_node.rowCount()):
            if "Release" in targets_node.child(i).text():
                release_node = targets_node.child(i)
                break

        assert release_node is not None

        # Get the project from the widget's workspace manager (it loads from file)
        loaded_proj = widget.workspace_manager.projects[0]

        with patch.object(widget, "config_changed") as mock_signal:
            widget.on_double_click(widget.model.indexFromItem(release_node))
            assert loaded_proj.active_config == "Release"
            mock_signal.emit.assert_called_once_with("TestProj", "Release")

    def test_context_menu_actions_exist(self, qapp, temp_dir):
        """Context menu has expected actions."""
        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        # The custom context menu is built in show_context_menu
        # We can't easily test the full menu without a real event,
        # but we can verify the method exists and creates actions
        assert hasattr(widget, "show_context_menu")
        assert hasattr(widget, "create_new_project_dialog")
        assert hasattr(widget, "add_file_dialog")
        
        # Test that create_new_project_dialog can be called without error
        # (it will prompt for input, so we mock the dialog)
        with patch("medha.project_manager.QInputDialog.getText", return_value=("TestProj", True)):
            widget.create_new_project_dialog()
            # Should have added a project
            assert len(widget.workspace_manager.projects) >= 1


# ---------------------------------------------------------------------------
# Virtual folder structure tests
# ---------------------------------------------------------------------------

class TestVirtualFolders:
    def test_four_virtual_folders_always_present(self, qapp, temp_dir):
        """Sources, Headers, Resources, Build Configs always appear."""
        proj_dir = os.path.join(temp_dir, "TestProj")
        os.makedirs(proj_dir)
        proj_file = os.path.join(proj_dir, "TestProj.medhaproj")
        proj = MedhaProject(name="TestProj", project_dir=proj_dir)
        proj.save()

        widget = ProjectExplorerWidget(temp_dir)
        widget.refresh_tree()

        root = widget.model.invisibleRootItem()
        ws_node = root.child(0)
        proj_node = ws_node.child(0)

        folder_names = [proj_node.child(i).text() for i in range(proj_node.rowCount())]
        assert any("Sources" in name for name in folder_names)
        assert any("Headers" in name for name in folder_names)
        assert any("Resources" in name for name in folder_names)
        assert any("Build Configurations" in name for name in folder_names)