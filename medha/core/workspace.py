"""
MEDHĀ IDE — Hybrid Workspace Architecture
Supports:
 1. Scratchpad Mode: Instant compilation and execution of single .c/.cpp files without any project files.
 2. Project/Workspace Mode: Full .medhaproj JSON configuration with structured tree view.
"""

import os
import json
from PySide6.QtCore import QObject, Signal


class ScratchpadSession:
    """Manages standalone single file editing, compilation, and execution."""
    def __init__(self, file_path=None):
        self.file_path = file_path or ""
        self.is_dirty = False

    def is_standalone(self):
        return True


class ProjectWorkspace:
    """Manages .medhaproj structured project workspace."""
    def __init__(self, name="MedhaProject", project_dir=""):
        self.name = name
        self.project_dir = project_dir
        self.project_file = os.path.join(project_dir, f"{name}.medhaproj") if project_dir else ""
        self.sources = []
        self.headers = []
        self.active_config = "Debug"

    def save(self):
        if not self.project_file:
            return False
        data = {
            "name": self.name,
            "version": "1.0",
            "active_config": self.active_config,
            "sources": self.sources,
            "headers": self.headers
        }
        try:
            with open(self.project_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False


class HybridWorkspaceController(QObject):
    """Orchestrates seamless switching between Scratchpad Mode and Project Mode."""
    mode_changed = Signal(str) # "scratchpad" | "project"
    workspace_loaded = Signal(object)

    def __init__(self, default_dir=""):
        super().__init__()
        self.current_dir = default_dir or os.getcwd()
        self.active_mode = "scratchpad"
        self.active_project = None
        self.scratchpad = ScratchpadSession()

    def set_scratchpad_file(self, path):
        self.active_mode = "scratchpad"
        self.scratchpad.file_path = path
        self.mode_changed.emit("scratchpad")

    def open_project(self, project_file):
        if os.path.exists(project_file):
            pdir = os.path.dirname(project_file)
            name = os.path.splitext(os.path.basename(project_file))[0]
            self.active_project = ProjectWorkspace(name=name, project_dir=pdir)
            self.active_mode = "project"
            self.mode_changed.emit("project")
            self.workspace_loaded.emit(self.active_project)
            return True
        return False
