"""
MEDHĀ IDE — Project & Workspace Manager Module
Supports .medhaproj (JSON-based project file like Code::Blocks .cbp)
Provides QTreeView + QStandardItemModel with logical virtual folders
(Sources, Headers, Resources, Build Targets).
"""

import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLabel, QPushButton,
    QHeaderView, QMenu, QInputDialog, QFileDialog, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor, QFont
from PySide6.QtCore import Qt, Signal, QObject


class MedhaProject:
    """Represents a .medhaproj project configuration file."""

    def __init__(self, name="UntitledProject", project_dir=""):
        self.name = name
        self.project_dir = project_dir
        self.project_file_path = os.path.join(project_dir, f"{name}.medhaproj") if project_dir else ""
        self.target_type = "executable"  # "executable" | "static_lib" | "shared_lib"
        self.sources = []
        self.headers = []
        self.resources = []
        self.include_paths = ["."]
        self.active_config = "Debug"
        self.build_configs = {
            "Debug": {
                "compiler_flags": ["-g", "-O0", "-DDEBUG", "-Wall"],
                "linker_flags": [],
                "output_dir": "bin/Debug",
                "binary_name": name
            },
            "Release": {
                "compiler_flags": ["-O2", "-s", "-DNDEBUG", "-Wall"],
                "linker_flags": [],
                "output_dir": "bin/Release",
                "binary_name": name
            }
        }

    def to_dict(self):
        return {
            "name": self.name,
            "version": "1.0",
            "target_type": self.target_type,
            "active_config": self.active_config,
            "sources": self.sources,
            "headers": self.headers,
            "resources": self.resources,
            "include_paths": self.include_paths,
            "build_configs": self.build_configs
        }

    @classmethod
    def from_dict(cls, data, project_file_path):
        pdir = os.path.dirname(project_file_path)
        proj = cls(name=data.get("name", "Project"), project_dir=pdir)
        proj.project_file_path = project_file_path
        proj.target_type = data.get("target_type", "executable")
        proj.active_config = data.get("active_config", "Debug")
        proj.sources = data.get("sources", [])
        proj.headers = data.get("headers", [])
        proj.resources = data.get("resources", [])
        proj.include_paths = data.get("include_paths", ["."])
        if "build_configs" in data:
            proj.build_configs = data["build_configs"]
        return proj

    def save(self):
        if not self.project_file_path:
            return False
        try:
            with open(self.project_file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[MedhaProject] Error saving project: {e}")
            return False

    @classmethod
    def load(cls, project_file_path):
        try:
            with open(project_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data, project_file_path)
        except Exception as e:
            print(f"[MedhaProject] Error loading project {project_file_path}: {e}")
            return None


class WorkspaceManager(QObject):
    """Manages workspace directory and multiple active .medhaproj projects."""

    project_added = Signal(MedhaProject)
    project_removed = Signal(str)

    def __init__(self, workspace_dir=None):
        if workspace_dir is None:
            workspace_dir = os.getcwd()
        super().__init__()
        self.workspace_dir = workspace_dir
        self.projects = []

    def load_workspace(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.projects.clear()
        # Scan for existing .medhaproj files in workspace
        for root, _, files in os.walk(workspace_dir):
            for file in files:
                if file.endswith(".medhaproj"):
                    full_path = os.path.join(root, file)
                    proj = MedhaProject.load(full_path)
                    if proj:
                        self.projects.append(proj)
                        self.project_added.emit(proj)

    def create_project(self, name, project_dir):
        os.makedirs(project_dir, exist_ok=True)
        proj = MedhaProject(name=name, project_dir=project_dir)

        # Create default main.c if directory is empty
        main_c = os.path.join(project_dir, "main.c")
        if not os.path.exists(main_c):
            with open(main_c, "w", encoding="utf-8") as f:
                f.write(f"// {name} — Native C Program\n#include <stdio.h>\n\nint main(void) {{\n    printf(\"Hello from {name}!\\n\");\n    return 0;\n}}\n")
            proj.sources.append("main.c")

        proj.save()
        self.projects.append(proj)
        self.project_added.emit(proj)
        return proj


class ProjectExplorerWidget(QWidget):
    """
    Multi-level Project Explorer UI using QTreeView + QStandardItemModel.
    Renders virtual logical categories (Sources, Headers, Resources, Build Configs).
    """

    file_selected = Signal(str)
    project_selected = Signal(MedhaProject)
    config_changed = Signal(str, str) # project_name, config_name

    def __init__(self, workspace_path=None, parent=None):
        if workspace_path is None:
            workspace_path = os.getcwd()
        super().__init__(parent)
        self.workspace_path = workspace_path
        self.workspace_manager = WorkspaceManager(workspace_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top Header Bar
        header = QLabel(" WORKSPACE PROJECTS")
        header.setStyleSheet("background-color: #161b22; color: #58a6ff; font-weight: bold; font-size: 11px; padding: 6px;")
        layout.addWidget(header)

        # Model & TreeView
        self.model = QStandardItemModel()
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.header().setVisible(False)
        self.tree.setAnimated(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.on_double_click)

        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                font-size: 12px;
            }
            QTreeView::item {
                padding: 3px;
            }
            QTreeView::item:hover {
                background-color: #161b22;
            }
            QTreeView::item:selected {
                background-color: #1f6feb;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.tree)

        self.refresh_tree()

    def set_workspace(self, path):
        self.workspace_path = path
        self.workspace_manager.load_workspace(path)
        self.refresh_tree()

    def refresh_tree(self):
        self.model.clear()
        root_item = self.model.invisibleRootItem()

        # Workspace Root Item
        ws_node = QStandardItem(f"Workspace: {os.path.basename(self.workspace_path)}")
        ws_node.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        ws_node.setEditable(False)
        root_item.appendRow(ws_node)

        # If no .medhaproj found, populate raw directory as fallback project
        if not self.workspace_manager.projects:
            proj = MedhaProject(name=os.path.basename(self.workspace_path), project_dir=self.workspace_path)
            for root_dir, _, files in os.walk(self.workspace_path):
                for f in files:
                    rel = os.path.relpath(os.path.join(root_dir, f), self.workspace_path)
                    if rel.startswith("."):
                        continue
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".c", ".cpp", ".cc", ".cxx"]:
                        proj.sources.append(rel)
                    elif ext in [".h", ".hpp", ".hh"]:
                        proj.headers.append(rel)
                    else:
                        proj.resources.append(rel)
            self.workspace_manager.projects.append(proj)

        for proj in self.workspace_manager.projects:
            proj_node = QStandardItem(f"📦 {proj.name} [{proj.active_config}]")
            proj_node.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
            proj_node.setEditable(False)
            proj_node.setData(proj, Qt.UserRole + 1)
            ws_node.appendRow(proj_node)

            # 1. Sources Folder
            sources_node = QStandardItem("📂 Sources")
            sources_node.setEditable(False)
            for src in proj.sources:
                file_node = QStandardItem(f"📄 {os.path.basename(src)}")
                file_node.setEditable(False)
                full_p = os.path.join(proj.project_dir, src) if not os.path.isabs(src) else src
                file_node.setData(full_p, Qt.UserRole)
                sources_node.appendRow(file_node)
            proj_node.appendRow(sources_node)

            # 2. Headers Folder
            headers_node = QStandardItem("📂 Headers")
            headers_node.setEditable(False)
            for hdr in proj.headers:
                file_node = QStandardItem(f"📑 {os.path.basename(hdr)}")
                file_node.setEditable(False)
                full_p = os.path.join(proj.project_dir, hdr) if not os.path.isabs(hdr) else hdr
                file_node.setData(full_p, Qt.UserRole)
                headers_node.appendRow(file_node)
            proj_node.appendRow(headers_node)

            # 3. Resources Folder
            res_node = QStandardItem("📂 Resources & Configuration")
            res_node.setEditable(False)
            for res in proj.resources:
                file_node = QStandardItem(f"⚙️ {os.path.basename(res)}")
                file_node.setEditable(False)
                full_p = os.path.join(proj.project_dir, res) if not os.path.isabs(res) else res
                file_node.setData(full_p, Qt.UserRole)
                res_node.appendRow(file_node)
            proj_node.appendRow(res_node)

            # 4. Build Targets
            target_node = QStandardItem("🎯 Build Configurations")
            target_node.setEditable(False)
            for cfg in proj.build_configs.keys():
                is_active = (cfg == proj.active_config)
                mark = "✓ " if is_active else "  "
                cfg_item = QStandardItem(f"{mark}{cfg}")
                cfg_item.setEditable(False)
                cfg_item.setData((proj, cfg), Qt.UserRole + 2)
                if is_active:
                    cfg_item.setForeground(QColor("#58a6ff"))
                target_node.appendRow(cfg_item)
            proj_node.appendRow(target_node)

        self.tree.expandAll()

    def on_double_click(self, index):
        item = self.model.itemFromIndex(index)
        if not item:
            return

        file_path = item.data(Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.file_selected.emit(file_path)
            return

        cfg_data = item.data(Qt.UserRole + 2)
        if cfg_data:
            proj, cfg_name = cfg_data
            proj.active_config = cfg_name
            proj.save()
            self.config_changed.emit(proj.name, cfg_name)
            self.refresh_tree()

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        menu = QMenu(self)

        act_new_proj = menu.addAction("New Project (.medhaproj)...")
        act_add_file = menu.addAction("Add File to Active Project...")
        menu.addSeparator()
        act_refresh = menu.addAction("Refresh Explorer")

        action = menu.exec_(self.tree.viewport().mapToGlobal(position))
        if action == act_new_proj:
            self.create_new_project_dialog()
        elif action == act_add_file:
            self.add_file_dialog(index)
        elif action == act_refresh:
            self.refresh_tree()

    def create_new_project_dialog(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project Name:")
        if ok and name.strip():
            pdir = os.path.join(self.workspace_path, name.strip())
            self.workspace_manager.create_project(name.strip(), pdir)
            self.refresh_tree()

    def add_file_dialog(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add File to Project", self.workspace_path)
        if file_path and self.workspace_manager.projects:
            proj = self.workspace_manager.projects[0]
            rel = os.path.relpath(file_path, proj.project_dir)
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".c", ".cpp", ".cc", ".cxx"]:
                if rel not in proj.sources: proj.sources.append(rel)
            elif ext in [".h", ".hpp", ".hh"]:
                if rel not in proj.headers: proj.headers.append(rel)
            else:
                if rel not in proj.resources: proj.resources.append(rel)
            proj.save()
            self.refresh_tree()
