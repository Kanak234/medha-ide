import os
import sys
import psutil
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QDockWidget, QFileDialog, QMessageBox, QLabel, QStatusBar,
    QMenuBar, QMenu, QSplitter, QGraphicsOpacityEffect
)
from PySide6.QtGui import QAction, QIcon, QKeySequence, QTextCursor
from PySide6.QtCore import Qt, QSize, QPropertyAnimation

from medha.editor import CodeEditorWidget
from medha.editor_widget import AdvancedCodeEditorWidget, CodeOutlineWidget
from medha.project_manager import ProjectExplorerWidget
from medha.terminal import IntegratedTerminalWidget
from medha.problems import ProblemsPanelWidget
from medha.runner import ProcessRunner
from medha.build_system import MultiTargetBuildEngine
from medha.debugger_engine import GdbDebuggerEngine, GdbDebuggerPanelWidget
from medha.analyzers.linter import StaticAnalyzerEngine, SafetyDiagnosticsPanelWidget
from medha.visualizers.memory_view import MemoryVisualizerWidget
from medha.compiler.disassembly import DisassemblyInspectorWidget
from medha.core.workspace import HybridWorkspaceController
from medha.dsa_visualizer.dsa_widget import DSAVisualizerWidget
from medha.dsa_visualizer.tracers.dsa_tracer import UniversalDSATracer


class MedhaMainWindow(QMainWindow):
    def __init__(self, workspace_path=None):
        super().__init__()
        if workspace_path is None:
            workspace_path = os.getcwd()
        self.workspace_path = workspace_path
        self.setWindowTitle("MEDHĀ IDE — Native PySide6 C/C++ Studio")
        self.resize(1440, 850)

        self.active_build_config = "Debug"
        self.workspace_ctrl = HybridWorkspaceController(workspace_path)

        # Main Central Tabbed Editor
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0d1117;
            }
            QTabBar::tab {
                background-color: #161b22;
                color: #8b949e;
                padding: 6px 14px;
                border-right: 1px solid #0d1117;
            }
            QTabBar::tab:selected {
                background-color: #0d1117;
                color: #58a6ff;
                border-top: 2px solid #1f6feb;
            }
        """)

        self.setCentralWidget(self.tab_widget)

        # Dock Widget 1 — Project Explorer (Left)
        self.explorer = ProjectExplorerWidget(workspace_path=self.workspace_path)
        self.explorer.file_selected.connect(self.open_file_path)
        self.explorer.config_changed.connect(self.on_project_config_changed)

        self.dock_explorer = QDockWidget("Project Explorer", self)
        self.dock_explorer.setWidget(self.explorer)
        self.dock_explorer.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_explorer)

        # Dock Widget 2 — Bottom Panel (Terminal, Problems, Safety Linter)
        self.bottom_tabs = QTabWidget()
        self.terminal = IntegratedTerminalWidget(workspace_path=self.workspace_path)
        self.problems = ProblemsPanelWidget()
        self.problems.problem_selected.connect(self.navigate_to_problem)

        self.safety_panel = SafetyDiagnosticsPanelWidget()
        self.safety_panel.diagnostic_selected.connect(self.navigate_to_problem)

        self.bottom_tabs.addTab(self.terminal, "Terminal")
        self.bottom_tabs.addTab(self.problems, "Compiler Output & Issues")
        self.bottom_tabs.addTab(self.safety_panel, "Safety Linter (cppcheck)")
        self.bottom_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #21262d;
                background-color: #090d16;
            }
            QTabBar::tab {
                background-color: #161b22;
                color: #8b949e;
                padding: 4px 12px;
            }
            QTabBar::tab:selected {
                background-color: #0d1117;
                color: #58a6ff;
            }
        """)

        self.dock_bottom = QDockWidget("Console & Safety Diagnostics", self)
        self.dock_bottom.setWidget(self.bottom_tabs)
        self.dock_bottom.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)

        # Dock Widget 3 — Universal DSA Visualizer (Right)
        self.dsa_tracer = UniversalDSATracer(self)
        self.dsa_widget = DSAVisualizerWidget(tracer=self.dsa_tracer, parent=self)
        self.dock_dsa = QDockWidget("DSA Visualizer Engine", self)
        self.dock_dsa.setWidget(self.dsa_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_dsa)

        # Dock Widget 4 — Visual Memory & Pointer Inspector (Right)
        self.memory_view = MemoryVisualizerWidget(self)
        self.dock_memory = QDockWidget("Live Memory & Pointers", self)
        self.dock_memory.setWidget(self.memory_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_memory)

        # Dock Widget 5 — Assembly Inspector (Right)
        self.asm_inspector = DisassemblyInspectorWidget(self)
        self.dock_asm = QDockWidget("Live Disassembly (gcc -S)", self)
        self.dock_asm.setWidget(self.asm_inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_asm)

        # Dock Widget 6 — GDB Debugger Engine & Panels (Right)
        self.gdb_engine = GdbDebuggerEngine(self)
        self.gdb_panel = QWidget()
        gdb_layout = QVBoxLayout(self.gdb_panel)
        gdb_layout.setContentsMargins(0, 0, 0, 0)
        self.real_gdb_panel = GdbDebuggerPanelWidget(self.gdb_engine, self)
        gdb_layout.addWidget(self.real_gdb_panel)

        self.gdb_engine.stopped_at.connect(self.on_gdb_stopped_at)
        self.gdb_engine.variables_updated.connect(self.on_gdb_variables_updated)

        self.dock_gdb = QDockWidget("GDB Interactive Debugger", self)
        self.dock_gdb.setWidget(self.gdb_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_gdb)

        # Dock Widget 7 — Symbol Outline (Right)
        self.outline_panel = CodeOutlineWidget(self)
        self.outline_panel.symbol_selected.connect(self.navigate_to_line)
        self.dock_outline = QDockWidget("Symbol Outline", self)
        self.dock_outline.setWidget(self.outline_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_outline)

        # AI Assistant Right Dock (P7)
        from medha.ai_panel import AiAssistantPanelWidget
        self.ai_panel = AiAssistantPanelWidget(self)
        self.dock_ai = QDockWidget("Offline AI Assistant", self)
        self.dock_ai.setWidget(self.ai_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_ai)

        # Tabify right dock widgets for clean UI
        self.tabifyDockWidget(self.dock_dsa, self.dock_memory)
        self.tabifyDockWidget(self.dock_memory, self.dock_asm)
        self.tabifyDockWidget(self.dock_asm, self.dock_gdb)
        self.tabifyDockWidget(self.dock_gdb, self.dock_outline)
        self.tabifyDockWidget(self.dock_outline, self.dock_ai)

        # Dock Fade-in Animations
        self.setup_dock_fade_in(self.dock_explorer)
        self.setup_dock_fade_in(self.dock_bottom)
        self.setup_dock_fade_in(self.dock_dsa)

        # Process Runner & Analyzer Engines
        self.runner = ProcessRunner(self)
        self.runner.output_received.connect(self.on_runner_output)
        self.runner.finished.connect(self.on_runner_finished)

        self.build_engine = MultiTargetBuildEngine(self)
        self.build_engine.output_stream.connect(self.on_runner_output)

        self.linter_engine = StaticAnalyzerEngine(self)
        self.linter_engine.analysis_finished.connect(self.safety_panel.set_diagnostics)

        # Setup MenuBar & StatusBar
        self.create_menu_bar()
        self.create_status_bar()
        self.apply_dark_theme()

        # Open initial welcome scratchpad file
        welcome_c_path = os.path.join(self.workspace_path, "main.c")
        if not os.path.exists(welcome_c_path):
            with open(welcome_c_path, 'w', encoding='utf-8') as f:
                f.write("// MEDHĀ IDE — Native C Scratchpad\n#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    int a = 42;\n    int *ptr = (int *)malloc(sizeof(int) * 10);\n    printf(\"Hello from Native MEDHĀ IDE!\\n\");\n    free(ptr);\n    return 0;\n}\n")
        self.open_file_path(welcome_c_path)

    def setup_dock_fade_in(self, dock):
        def on_vis(visible):
            if visible and dock.widget():
                effect = QGraphicsOpacityEffect(dock.widget())
                dock.widget().setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity", dock)
                anim.setDuration(120)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.start()
                dock._fade_anim = anim
        dock.visibilityChanged.connect(on_vis)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #161b22;
                color: #c9d1d9;
                padding: 2px;
            }
            QMenuBar::item:selected {
                background-color: #1f6feb;
                color: #ffffff;
            }
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
                color: #ffffff;
            }
        """)

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        act_new = QAction("&New Scratchpad File", self)
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(lambda: self.create_untitled_tab("untitled.c"))
        file_menu.addAction(act_new)

        act_open_file = QAction("&Open File...", self)
        act_open_file.setShortcut(QKeySequence.StandardKey.Open)
        act_open_file.triggered.connect(self.action_open_file)
        file_menu.addAction(act_open_file)

        act_open_folder = QAction("Open &Workspace Folder...", self)
        act_open_folder.triggered.connect(self.action_open_folder)
        file_menu.addAction(act_open_folder)

        file_menu.addSeparator()

        act_save = QAction("&Save File", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.action_save_file)
        file_menu.addAction(act_save)

        act_save_as = QAction("Save &As...", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self.action_save_as_file)
        file_menu.addAction(act_save_as)

        file_menu.addSeparator()

        act_exit = QAction("E&xit", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        act_undo = QAction("&Undo", self)
        act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        act_undo.triggered.connect(lambda: self.get_current_editor().undo() if self.get_current_editor() else None)
        edit_menu.addAction(act_undo)

        act_redo = QAction("&Redo", self)
        act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        act_redo.triggered.connect(lambda: self.get_current_editor().redo() if self.get_current_editor() else None)
        edit_menu.addAction(act_redo)

        # View Menu
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.dock_explorer.toggleViewAction())
        view_menu.addAction(self.dock_bottom.toggleViewAction())
        view_menu.addAction(self.dock_dsa.toggleViewAction())
        view_menu.addAction(self.dock_memory.toggleViewAction())
        view_menu.addAction(self.dock_asm.toggleViewAction())
        view_menu.addAction(self.dock_gdb.toggleViewAction())
        view_menu.addAction(self.dock_outline.toggleViewAction())

        # Run Menu
        run_menu = menu_bar.addMenu("&Run")
        act_run = QAction("&Run Active Scratchpad File", self)
        act_run.setShortcut(QKeySequence("Ctrl+F5"))
        act_run.triggered.connect(self.action_run_active_file)
        run_menu.addAction(act_run)

        # Analysis Menu
        analyze_menu = menu_bar.addMenu("&Analyze")
        act_lint = QAction("Run &Static Safety Linter (cppcheck)", self)
        act_lint.triggered.connect(self.action_run_linter)
        analyze_menu.addAction(act_lint)

        act_disasm = QAction("Inspect &Live Assembly (gcc -S)", self)
        act_disasm.triggered.connect(self.action_run_disassembly)
        analyze_menu.addAction(act_disasm)

        # Debug Menu (P4 + GDB)
        debug_menu = menu_bar.addMenu("&Debug")
        act_dbg_start = QAction("Start &Debugging (F5)", self)
        act_dbg_start.setShortcut(QKeySequence("F5"))
        act_dbg_start.triggered.connect(self.action_start_debug)
        debug_menu.addAction(act_dbg_start)

        act_dbg_next = QAction("Step &Over (F10)", self)
        act_dbg_next.setShortcut(QKeySequence("F10"))
        act_dbg_next.triggered.connect(lambda: self.gdb_engine.step_over())
        debug_menu.addAction(act_dbg_next)

        act_dbg_step = QAction("Step &Into (F11)", self)
        act_dbg_step.setShortcut(QKeySequence("F11"))
        act_dbg_step.triggered.connect(lambda: self.gdb_engine.step_into())
        debug_menu.addAction(act_dbg_step)

        act_dbg_out = QAction("Step &Out (Shift+F11)", self)
        act_dbg_out.setShortcut(QKeySequence("Shift+F11"))
        act_dbg_out.triggered.connect(lambda: self.gdb_engine.step_out())
        debug_menu.addAction(act_dbg_out)

        act_dbg_stop = QAction("&Stop Debugging", self)
        act_dbg_stop.triggered.connect(lambda: self.gdb_engine.stop_debug())
        debug_menu.addAction(act_dbg_stop)

        # LSP Menu (P3)
        lsp_menu = menu_bar.addMenu("&LSP")
        act_lsp_def = QAction("&Go to Definition (F12)", self)
        act_lsp_def.setShortcut(QKeySequence("F12"))
        act_lsp_def.triggered.connect(self.action_lsp_definition)
        lsp_menu.addAction(act_lsp_def)

        act_lsp_comp = QAction("Trigger &Completion (Ctrl+Space)", self)
        act_lsp_comp.setShortcut(QKeySequence("Ctrl+Space"))
        act_lsp_comp.triggered.connect(self.action_lsp_completion)
        lsp_menu.addAction(act_lsp_comp)

        # Git Menu (P5)
        git_menu = menu_bar.addMenu("&Git")
        act_git_status = QAction("Git &Status", self)
        act_git_status.triggered.connect(self.action_git_status)
        git_menu.addAction(act_git_status)

        act_git_commit = QAction("Git Stage & Commit...", self)
        act_git_commit.triggered.connect(self.action_git_commit)
        git_menu.addAction(act_git_commit)

        # Build Menu (P6 + Multi-Target)
        build_menu = menu_bar.addMenu("&Build")

        act_cfg_debug = QAction("Target: &Debug (-g -O0)", self)
        act_cfg_debug.triggered.connect(lambda: self.set_active_build_target("Debug"))
        build_menu.addAction(act_cfg_debug)

        act_cfg_release = QAction("Target: &Release (-O2 -s)", self)
        act_cfg_release.triggered.connect(lambda: self.set_active_build_target("Release"))
        build_menu.addAction(act_cfg_release)

        build_menu.addSeparator()

        act_build_cfg = QAction("&Configure CMake", self)
        act_build_cfg.triggered.connect(self.action_build_configure)
        build_menu.addAction(act_build_cfg)

        act_build_proj = QAction("&Build Project (Ctrl+Shift+B)", self)
        act_build_proj.setShortcut(QKeySequence("Ctrl+Shift+B"))
        act_build_proj.triggered.connect(self.action_build_project)
        build_menu.addAction(act_build_proj)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        act_about = QAction("&About MEDHĀ IDE", self)
        act_about.triggered.connect(self.show_about_dialog)
        help_menu.addAction(act_about)

    def set_active_build_target(self, target):
        self.active_build_config = target
        self.lbl_status.setText(f"Active Build Target: {target}")

    def create_status_bar(self):
        status = QStatusBar()
        status.setStyleSheet("background-color: #2b2d30; color: #bcbec4; border-top: 1px solid #393b40;")
        self.setStatusBar(status)

        cores = os.cpu_count() or "Unavailable"
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

        self.lbl_status = QLabel(f"Ready [{self.active_build_config}]")
        self.lbl_cursor_pos = QLabel("Ln 1, Col 1 | C")
        self.lbl_cursor_pos.setStyleSheet("color: #a1a3ab; margin-right: 15px;")
        self.lbl_sys_info = QLabel(f" CPU: {cores} Cores | RAM: {ram_gb} GB (Live OS) ")
        self.lbl_sys_info.setStyleSheet("color: #58a6ff; font-weight: bold;")

        status.addWidget(self.lbl_status, 1)
        status.addPermanentWidget(self.lbl_cursor_pos)
        status.addPermanentWidget(self.lbl_sys_info)

    def close_tab(self, index):
        if index >= 0 and self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.create_untitled_tab()

    def on_tab_changed(self, index):
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'get_symbol_outline'):
            symbols = editor.get_symbol_outline()
            self.outline_panel.update_outline(symbols)
            if editor.file_path:
                self.asm_inspector.set_active_file(editor.file_path)

    def update_tab_title(self, editor):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == editor:
                base = os.path.basename(editor.file_path) if editor.file_path else "untitled.c"
                if getattr(editor, 'is_modified', False):
                    base += " •"
                self.tab_widget.setTabText(i, base)
                break

    def update_cursor_status(self):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            lang = getattr(editor, 'lang', 'cpp').upper()
            self.lbl_cursor_pos.setText(f"Ln {line}, Col {col} | {lang}")

    def apply_dark_theme(self):
        from PySide6.QtWidgets import QApplication
        from medha.theme import DARK_QSS
        app_inst = QApplication.instance()
        if app_inst:
            app_inst.setStyleSheet(DARK_QSS)

    def get_current_editor(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, (CodeEditorWidget, AdvancedCodeEditorWidget)):
            return widget
        return None

    def create_untitled_tab(self, title="untitled.c", content=""):
        editor = AdvancedCodeEditorWidget(file_path=None, parent=self)
        editor.setPlainText(content)
        editor.is_modified = False
        editor.cursorPositionChanged.connect(self.update_cursor_status)
        editor.textChanged.connect(lambda e=editor: self.update_tab_title(e))
        editor.breakpoint_toggled.connect(self.on_breakpoint_toggled)
        idx = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(idx)
        self.update_cursor_status()

    def open_file_path(self, path):
        if not os.path.exists(path):
            return

        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, (CodeEditorWidget, AdvancedCodeEditorWidget)) and widget.file_path == path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            filename = os.path.basename(path)
            editor = AdvancedCodeEditorWidget(file_path=path, parent=self)
            editor.setPlainText(content)
            editor.is_modified = False
            editor.cursorPositionChanged.connect(self.update_cursor_status)
            editor.textChanged.connect(lambda e=editor: self.update_tab_title(e))
            editor.breakpoint_toggled.connect(self.on_breakpoint_toggled)
            idx = self.tab_widget.addTab(editor, filename)
            self.tab_widget.setCurrentIndex(idx)
            self.lbl_status.setText(f"Opened file: {path}")
            self.update_cursor_status()

            symbols = editor.get_symbol_outline()
            self.outline_panel.update_outline(symbols)
            self.asm_inspector.set_active_file(path)

        except Exception as e:
            QMessageBox.critical(self, "Error Opening File", str(e))

    def on_breakpoint_toggled(self, file_path, line, is_set):
        self.gdb_engine.toggle_breakpoint(file_path, line)
        self.real_gdb_panel.refresh_breakpoints()

    def on_project_config_changed(self, proj_name, cfg_name):
        self.set_active_build_target(cfg_name)

    def action_open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", self.workspace_path, "All Files (*)")
        if path:
            self.open_file_path(path)

    def action_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace Folder", self.workspace_path)
        if folder:
            self.workspace_path = folder
            self.explorer.set_workspace(folder)
            self.terminal.process.setWorkingDirectory(folder)
            self.lbl_status.setText(f"Opened workspace: {folder}")

    def action_save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        if not editor.file_path:
            self.action_save_as_file()
        else:
            try:
                with open(editor.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.is_modified = False
                self.update_tab_title(editor)
                self.lbl_status.setText(f"Saved: {editor.file_path}")
                self.linter_engine.analyze_file(editor.file_path)
                self.asm_inspector.set_active_file(editor.file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error Saving File", str(e))

    def action_save_as_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save File As", self.workspace_path, "All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.file_path = path
                editor.is_modified = False
                self.update_tab_title(editor)
                self.lbl_status.setText(f"Saved: {path}")
                self.linter_engine.analyze_file(path)
                self.asm_inspector.set_active_file(path)
            except Exception as e:
                QMessageBox.critical(self, "Error Saving File", str(e))

    def action_run_active_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        self.action_save_file()

        if not editor.file_path or not os.path.exists(editor.file_path):
            QMessageBox.warning(self, "Run Error", "Please save scratchpad file to disk before compilation.")
            return

        self.bottom_tabs.setCurrentWidget(self.terminal)
        self.lbl_status.setText(f"Scratchpad Running ({self.active_build_config}) {os.path.basename(editor.file_path)}...")
        self.runner.run_file(editor.file_path)

    def action_run_linter(self):
        editor = self.get_current_editor()
        if editor and editor.file_path:
            self.bottom_tabs.setCurrentWidget(self.safety_panel)
            self.linter_engine.analyze_file(editor.file_path)

    def action_run_disassembly(self):
        editor = self.get_current_editor()
        if editor and editor.file_path:
            self.dock_asm.show()
            self.asm_inspector.set_active_file(editor.file_path)

    # --- LSP Action Handlers ---
    def action_lsp_definition(self):
        editor = self.get_current_editor()
        if not editor or not editor.file_path:
            return
        ext = os.path.splitext(editor.file_path)[1].lower()
        lang = "c" if ext in ['.c', '.cpp', '.h', '.hpp'] else "python"
        from medha.lsp import LspClient
        client = LspClient(lang, self.workspace_path)
        client.start()
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        res = client.definition(editor.file_path, line, col)
        client.shutdown()
        if res:
            fpath, fline, fcol = res
            self.navigate_to_problem(fpath, fline, fcol)
        else:
            self.lbl_status.setText("LSP: Definition not found")

    def action_lsp_completion(self):
        editor = self.get_current_editor()
        if not editor or not editor.file_path:
            return
        ext = os.path.splitext(editor.file_path)[1].lower()
        lang = "c" if ext in ['.c', '.cpp', '.h', '.hpp'] else "python"
        from medha.lsp import LspClient
        client = LspClient(lang, self.workspace_path)
        client.start()
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        items = client.completions(editor.file_path, line, col)
        client.shutdown()
        if items:
            self.lbl_status.setText(f"LSP Completions: {', '.join(items[:5])}")

    # --- Debugger Action Handlers ---
    def action_start_debug(self):
        editor = self.get_current_editor()
        if not editor or not editor.file_path:
            return
        self.action_save_file()
        ext = os.path.splitext(editor.file_path)[1].lower()
        from medha.debugger import DebugSession
        if ext in ['.c', '.cpp']:
            bin_path = os.path.splitext(editor.file_path)[0]
            cmd = f"gcc -g {editor.file_path} -o {bin_path}"
            os.system(cmd)
            s = DebugSession(bin_path, kind="gdb")
            self.gdb_engine.start_debug(bin_path, kind="gdb")
        else:
            s = DebugSession(editor.file_path, kind="debugpy")
            self.gdb_engine.start_debug(editor.file_path, kind="debugpy")

        s.start()
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        s.set_breakpoint(editor.file_path, line)
        s.run()
        if s.wait_for_stop(timeout=5.0):
            self.lbl_status.setText(f"Debugger: Stopped at line {line}")
            if hasattr(editor, 'set_execution_line'):
                editor.set_execution_line(line)
        s.terminate()

    def on_gdb_stopped_at(self, file_path, line):
        self.open_file_path(file_path)
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'set_execution_line'):
            editor.set_execution_line(line)

    def on_gdb_variables_updated(self, variables):
        stack_vars = []
        heap_allocs = []
        for name, val in variables:
            stack_vars.append((name, val, "0x7fffffff"))
            if "0x5555" in val or "0x6000" in val:
                heap_allocs.append((name, val, "64"))
        if stack_vars:
            self.memory_view.update_memory_map(stack_vars, heap_allocs)
        self.dsa_tracer.parse_gdb_variables(variables)

    # --- Git Action Handlers ---
    def action_git_status(self):
        from medha.git_backend import GitBackend
        git = GitBackend(self.workspace_path)
        status_files = git.status()
        self.bottom_tabs.setCurrentWidget(self.terminal)
        self.terminal.append_output(f"[Git Status] Modified files: {status_files}\n", color="#79c0ff")

    def action_git_commit(self):
        from medha.git_backend import GitBackend
        git = GitBackend(self.workspace_path)
        status_files = git.status()
        if status_files:
            git.stage(status_files)
            sha = git.commit("Updated from MEDHĀ IDE")
            self.lbl_status.setText(f"Git Commit SHA: {sha[:7]}")

    # --- Build System Action Handlers ---
    def action_build_configure(self):
        from medha.build import BuildSystem
        bs = BuildSystem(self.workspace_path)
        code, out = bs.configure()
        self.bottom_tabs.setCurrentWidget(self.terminal)
        self.terminal.append_output(f"[CMake Configure Exit {code}]\n{out}\n", color="#79c0ff")

    def action_build_project(self):
        from medha.build import BuildSystem
        bs = BuildSystem(self.workspace_path)
        code, out, artifact = bs.build()
        self.bottom_tabs.setCurrentWidget(self.terminal)
        self.terminal.append_output(f"[Build Exit {code}] Artifact: {artifact}\n{out}\n", color="#79c0ff")

    def on_runner_output(self, text, stream_type):
        color = "#f85149" if stream_type == 'stderr' else None
        self.terminal.append_output(text, color=color)

    def on_runner_finished(self, exit_code, diagnostics):
        self.problems.set_diagnostics(diagnostics)
        if diagnostics:
            self.bottom_tabs.setCurrentWidget(self.problems)
            self.lbl_status.setText(f"Build Finished with {len(diagnostics)} diagnostic error(s).")
        else:
            self.lbl_status.setText(f"Process Finished with exit code {exit_code}.")

    def navigate_to_problem(self, fpath, line, col=1):
        self.open_file_path(fpath)
        editor = self.get_current_editor()
        if editor:
            block = editor.document().findBlockByLineNumber(max(0, line - 1))
            cursor = editor.textCursor()
            cursor.setPosition(block.position() + max(0, col - 1))
            editor.setTextCursor(cursor)
            editor.setFocus()

    def navigate_to_line(self, line):
        editor = self.get_current_editor()
        if editor:
            block = editor.document().findBlockByLineNumber(max(0, line - 1))
            cursor = editor.textCursor()
            cursor.setPosition(block.position())
            editor.setTextCursor(cursor)
            editor.setFocus()

    def closeEvent(self, event):
        if hasattr(self, 'terminal') and self.terminal:
            self.terminal.close()
        if hasattr(self, 'runner') and self.runner and hasattr(self.runner, 'process'):
            if self.runner.process.state() != 0:
                self.runner.process.terminate()
                if not self.runner.process.waitForFinished(500):
                    self.runner.process.kill()
        if hasattr(self, 'gdb_engine') and self.gdb_engine:
            self.gdb_engine.stop_debug()
        super().closeEvent(event)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About MEDHĀ IDE",
            "<h3>MEDHĀ IDE v1.0.0</h3>"
            "<p>Created by Kanak Prabhakar</p>"
            "<p>Autonomous Native Desktop Development Suite (PySide6 / Qt 6)</p>"
            "<p>Universal DSA Visualizer & Educational Engine Architecture</p>"
        )
