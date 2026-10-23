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


def get_app_icon_path() -> str:
    """
    Return the path to the application icon (medha-icon-256.png).
    Works both from the source repo and from inside the Snap ($SNAP/app).
    The snapcraft.yaml dump part ships docs/assets/icon/ to $SNAP/app/docs/assets/icon/.
    """
    # Try 1: Relative to this module (medha/app.py -> project root -> docs/assets/icon/)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    repo_icon = os.path.join(module_dir, "..", "..", "docs", "assets", "icon", "medha-icon-256.png")
    repo_icon = os.path.normpath(repo_icon)
    if os.path.exists(repo_icon):
        return repo_icon

    # Try 2: Snap environment ($SNAP/app/docs/assets/icon/medha-icon-256.png)
    snap_root = os.environ.get("SNAP")
    if snap_root:
        snap_icon = os.path.join(snap_root, "app", "docs", "assets", "icon", "medha-icon-256.png")
        if os.path.exists(snap_icon):
            return snap_icon

    # Try 3: Installed system location (/usr/share/icons/hicolor/256x256/apps/io.github.Kanak234.Medha.png)
    # This is where the snap desktop integration would place it
    system_icon = "/usr/share/icons/hicolor/256x256/apps/io.github.Kanak234.Medha.png"
    if os.path.exists(system_icon):
        return system_icon

    # Fallback: return the repo path anyway (Qt will handle missing gracefully)
    return repo_icon


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
from medha.extensions.ui.panel import ExtensionsPanel
# --- MEDHĀ v2 additions -----------------------------------------------------
# turbo/panel.py   : 640×480 graphics.h / conio.h screen (PRABHA runtime)
# security.py      : offline beginner security scan (PyraSec rules for code)
# settings / platform_info : cross-platform paths + user choices (Windows/Linux)
from medha.turbo.panel import TurboPanel
from medha.analyzers.security import SecurityPanel, scan_file
from medha import settings
from medha import platform_info


def default_workspace(path):
    """Return a folder the student can write to.

    WHY: an MSIX/Store install starts MEDHĀ with the read-only install folder (or
    C:\\Windows\\System32) as the current directory; writing main.c there crashed v1.
    FLOW: MedhaMainWindow.__init__ → this → ~/Documents/MEDHA Projects if needed.
    """
    try:
        if path and os.path.isdir(path) and os.access(path, os.W_OK) and \
                os.path.abspath(path) != os.path.abspath(str(platform_info.app_root())):
            return path
    except OSError:
        pass
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    target = os.path.join(docs if os.path.isdir(docs) else os.path.expanduser("~"), "MEDHA Projects")
    os.makedirs(target, exist_ok=True)
    return target


class MedhaMainWindow(QMainWindow):
    def __init__(self, workspace_path=None):
        super().__init__()
        workspace_path = default_workspace(workspace_path or os.getcwd())
        self.workspace_path = workspace_path
        from medha import __version__
        self.setWindowTitle(f"MEDHĀ IDE {__version__} — C · C++ · Java · Python · Turbo C")
        self.resize(1440, 850)

        # Set application window icon (works in repo and in snap)
        icon_path = get_app_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

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
        # v2: offline security scan of the student's own code (CWE + explanation)
        self.security_panel = SecurityPanel()
        self.security_panel.finding_selected.connect(self.navigate_to_problem)
        self.bottom_tabs.addTab(self.security_panel, "Security")
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

        # Extensions Panel (Right Dock) - P8 Extensions
        self.extensions_panel = ExtensionsPanel(self)
        self.extensions_panel.theme_apply_requested.connect(self._on_theme_apply_requested)
        self.dock_extensions = QDockWidget("Extensions", self)
        self.dock_extensions.setWidget(self.extensions_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_extensions)

        # v2: Turbo C screen — graphics.h / conio.h output drawn from the real framebuffer
        self.turbo_panel = TurboPanel(self)
        self.dock_turbo = QDockWidget("Turbo C Screen (640×480)", self)
        self.dock_turbo.setWidget(self.turbo_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_turbo)

        # Tabify right dock widgets for clean UI
        self.tabifyDockWidget(self.dock_dsa, self.dock_memory)
        self.tabifyDockWidget(self.dock_memory, self.dock_asm)
        self.tabifyDockWidget(self.dock_asm, self.dock_gdb)
        self.tabifyDockWidget(self.dock_gdb, self.dock_outline)
        self.tabifyDockWidget(self.dock_outline, self.dock_ai)
        self.tabifyDockWidget(self.dock_ai, self.dock_extensions)
        self.tabifyDockWidget(self.dock_extensions, self.dock_turbo)

        # Dock Fade-in Animations
        self.setup_dock_fade_in(self.dock_explorer)
        self.setup_dock_fade_in(self.dock_bottom)
        self.setup_dock_fade_in(self.dock_dsa)

        # Process Runner & Analyzer Engines
        self.runner = ProcessRunner(self)
        self.runner.output_received.connect(self.on_runner_output)
        self.runner.finished.connect(self.on_runner_finished)
        # Turbo mode: frames → screen panel, keys from the panel → program stdin
        self.runner.turbo_started.connect(self.on_turbo_started)
        self.runner.turbo_frame.connect(self.turbo_panel.on_frame)
        self.runner.turbo_message.connect(self.turbo_panel.on_message)
        self.turbo_panel.key_for_program.connect(self.runner.write_stdin)
        self.turbo_panel.stop_requested.connect(self.runner.stop)
        # typed terminal lines go to the RUNNING program first (scanf / cin / input())
        self.terminal.input_override = self.runner.write_stdin

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

        # v2: Lab Programs — copies a ready example into the workspace and opens it
        lab_menu = file_menu.addMenu("Open &Lab Program")
        self.build_lab_menu(lab_menu)

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
        view_menu.addAction(self.dock_ai.toggleViewAction())
        view_menu.addAction(self.dock_extensions.toggleViewAction())
        view_menu.addAction(self.dock_turbo.toggleViewAction())

        # Extensions shortcut
        act_extensions = QAction("Extensions", self)
        act_extensions.setShortcut(QKeySequence("Ctrl+Shift+X"))
        act_extensions.triggered.connect(self.dock_extensions.toggleViewAction().trigger)
        self.addAction(act_extensions)

        # Run Menu
        run_menu = menu_bar.addMenu("&Run")
        act_run = QAction("&Run Active Scratchpad File", self)
        act_run.setShortcut(QKeySequence("Ctrl+F5"))
        act_run.triggered.connect(self.action_run_active_file)
        run_menu.addAction(act_run)

        act_stop = QAction("&Stop Program", self)
        act_stop.setShortcut(QKeySequence("Shift+F5"))
        act_stop.triggered.connect(self.runner_stop)
        run_menu.addAction(act_stop)

        # Analysis Menu
        analyze_menu = menu_bar.addMenu("&Analyze")
        act_lint = QAction("Run &Static Safety Linter (cppcheck)", self)
        act_lint.triggered.connect(self.action_run_linter)
        analyze_menu.addAction(act_lint)

        act_sec = QAction("&Security Scan (offline, CWE)", self)
        act_sec.setShortcut(QKeySequence("Ctrl+Alt+S"))
        act_sec.triggered.connect(self.action_security_scan)
        analyze_menu.addAction(act_sec)

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

        # Tools Menu (v2)
        tools_menu = menu_bar.addMenu("&Tools")
        act_tc = QAction("&Toolchains && Run Settings…", self)
        act_tc.triggered.connect(self.action_toolchains)
        tools_menu.addAction(act_tc)

        act_mod = QAction("&Modernize this code (Turbo → C11/C++17)…", self)
        act_mod.setShortcut(QKeySequence("Ctrl+Alt+M"))
        act_mod.triggered.connect(self.action_modernize)
        tools_menu.addAction(act_mod)

        self.act_turbo = QAction("T&urbo mode (graphics.h / conio.h / iostream.h)", self)
        self.act_turbo.setCheckable(True)
        self.act_turbo.setChecked(bool(settings.get("turbo_mode", True)))
        self.act_turbo.toggled.connect(lambda on: settings.set("turbo_mode", on))
        tools_menu.addAction(self.act_turbo)

        self.act_hinglish = QAction("Explain errors in &Hinglish", self)
        self.act_hinglish.setCheckable(True)
        self.act_hinglish.setChecked(settings.get("explain_lang", "en") == "hi")
        self.act_hinglish.toggled.connect(lambda on: settings.set("explain_lang", "hi" if on else "en"))
        tools_menu.addAction(self.act_hinglish)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        act_palette = QAction("&Command Palette…", self)
        act_palette.setShortcut(QKeySequence("Ctrl+Shift+P"))
        act_palette.triggered.connect(self.show_command_palette)
        help_menu.addAction(act_palette)
        act_keys = QAction("&Keyboard Shortcuts", self)
        act_keys.triggered.connect(self.show_shortcuts)
        help_menu.addAction(act_keys)
        help_menu.addSeparator()
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
            self.terminal.set_working_directory(folder)
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
        try:
            client.start()
        except OSError:
            self.lbl_status.setText("Go to Definition needs clangd (C/C++) or pylsp (Python) — see Tools → Toolchains")
            return
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
        try:
            client.start()
        except OSError:
            self.lbl_status.setText("Completion needs clangd (C/C++) or pylsp (Python) — see Tools → Toolchains")
            return
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
        if ext in ['.c', '.cpp', '.cc', '.cxx']:
            # v2: compile with the detected toolchain (bundled MinGW on Windows) into
            # .medha_build/, with -g -O0 so every line can be stepped. v1 used
            # os.system("gcc …"), which breaks on paths with spaces and on Windows.
            import subprocess
            from medha import toolchains
            try:
                cc = toolchains.require("g++" if ext != ".c" else "gcc")
            except toolchains.ToolMissing as e:
                QMessageBox.warning(self, "Debugger", str(e))
                return
            out_dir = os.path.join(os.path.dirname(editor.file_path), ".medha_build")
            os.makedirs(out_dir, exist_ok=True)
            bin_path = os.path.join(out_dir, os.path.splitext(os.path.basename(editor.file_path))[0] + platform_info.EXE)
            r = subprocess.run([cc, "-g", "-O0", editor.file_path, "-o", bin_path] + (["-lm"] if ext == ".c" else []),
                               capture_output=True, text=True)
            if r.returncode != 0:
                self.terminal.append_output(r.stderr, color="#f85149")
                self.lbl_status.setText("Debug build failed — fix the errors first")
                return
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
            # v1 showed a made-up address "0x7fffffff" for every local and guessed heap
            # blocks from the value text. GDB's -stack-list-variables gives no address,
            # so we show "—" instead of inventing one; pointers (0x… values) are listed
            # as pointing to that address, size unknown.
            stack_vars.append((name, val, "—"))
            if val.strip().startswith("0x") and val.strip() != "0x0":
                heap_allocs.append((name, val.strip().split()[0], "?"))
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
        if self.runner.binary_to_run and getattr(self, "_turbo_active", False):
            self.turbo_panel.on_finished(exit_code)
            self._turbo_active = False
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

    # ------------------------------------------------------------------
    # MEDHĀ v2 actions
    # ------------------------------------------------------------------
    def build_lab_menu(self, menu):
        """File → Open Lab Program: one submenu per folder in examples/.

        WHY: students should be able to run a classic lab program in one click.
        FLOW: pick → copy into <workspace>/lab/ (the install folder may be read-only
        and the student should edit their own copy) → open it in a tab.
        """
        root = os.path.join(str(platform_info.app_root()), "examples")
        groups = [("Turbo C graphics / conio", os.path.join(root, "turboc"))]
        for lang in ("c", "cpp", "java", "python"):
            groups.append((lang.upper() if lang != "python" else "Python", os.path.join(root, "lab", lang)))
        for title, folder in groups:
            if not os.path.isdir(folder):
                continue
            sub = menu.addMenu(title)
            for name in sorted(os.listdir(folder)):
                act = QAction(name, self)
                act.triggered.connect(lambda _=False, f=os.path.join(folder, name): self.open_lab_program(f))
                sub.addAction(act)

    def open_lab_program(self, src):
        import shutil
        dest_dir = os.path.join(self.workspace_path, "lab")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, os.path.basename(src))
        if not os.path.exists(dest):          # never overwrite the student's edited copy
            shutil.copyfile(src, dest)
        self.open_file_path(dest)

    def runner_stop(self):
        self.runner.stop()
        self.lbl_status.setText("Program stopped")

    def on_turbo_started(self, uses_panel):
        self._turbo_active = True
        if uses_panel:
            self.dock_turbo.show()
            self.dock_turbo.raise_()
        self.turbo_panel.on_started(uses_panel)

    def action_security_scan(self):
        editor = self.get_current_editor()
        if not editor or not editor.file_path:
            self.lbl_status.setText("Save the file first, then run Security Scan")
            return
        self.action_save_file()
        findings = scan_file(editor.file_path, settings.get("explain_lang", "en"))
        self.security_panel.set_findings(findings, editor.file_path)
        self.bottom_tabs.setCurrentWidget(self.security_panel)

    def action_toolchains(self):
        from medha.toolchains_dialog import ToolchainsDialog
        if ToolchainsDialog(self).exec():
            self.act_turbo.setChecked(bool(settings.get("turbo_mode", True)))
            self.act_hinglish.setChecked(settings.get("explain_lang", "en") == "hi")
            self.lbl_status.setText("Toolchain settings saved")

    def action_modernize(self):
        editor = self.get_current_editor()
        if not editor:
            return
        from medha.modernize_dialog import ModernizeDialog
        name = os.path.basename(editor.file_path) if editor.file_path else "untitled.cpp"
        if os.path.splitext(name)[1].lower() not in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"):
            QMessageBox.information(self, "Modernize", "Modernize works on C and C++ files (Turbo C / Turbo C++ code).")
            return
        dlg = ModernizeDialog(editor.toPlainText(), name, settings.get("explain_lang", "en"), self)
        if dlg.exec() and dlg.result_code is not None:
            if dlg.mode == "replace":
                cursor = editor.textCursor()
                cursor.beginEditBlock()        # one Ctrl+Z restores the Turbo version
                cursor.select(QTextCursor.SelectionType.Document)
                cursor.insertText(dlg.result_code)
                cursor.endEditBlock()
            else:
                base, ext = os.path.splitext(name)
                self.create_untitled_tab(f"{base}_modern{ext}", dlg.result_code)

    def show_command_palette(self):
        from medha.command_palette import CommandPalette, collect_actions
        dlg = CommandPalette(collect_actions(self.menuBar()), self)
        geo = self.geometry()
        dlg.move(geo.x() + (geo.width() - dlg.width()) // 2, geo.y() + 80)
        dlg.exec()

    def show_shortcuts(self):
        from medha.command_palette import ShortcutsDialog, collect_actions
        ShortcutsDialog(collect_actions(self.menuBar()), self).exec()

    def closeEvent(self, event):
        if hasattr(self, 'terminal') and self.terminal:
            self.terminal.shutdown()
        if hasattr(self, 'runner') and self.runner and hasattr(self.runner, 'process'):
            if self.runner.process.state() != 0:
                self.runner.process.terminate()
                if not self.runner.process.waitForFinished(500):
                    self.runner.process.kill()
        if hasattr(self, 'gdb_engine') and self.gdb_engine:
            self.gdb_engine.stop_debug()
        super().closeEvent(event)

    def show_about_dialog(self):
        from medha import __version__
        from medha import toolchains
        box = QMessageBox(self)
        box.setWindowTitle("About MEDHĀ IDE")
        # Kanak's KP orbit logo (docs/assets/logo-mark.svg) is the watermark of every project
        logo = os.path.join(str(platform_info.app_root()), "docs", "assets", "logo-mark.svg")
        if os.path.exists(logo):
            from PySide6.QtGui import QPixmap
            box.setIconPixmap(QIcon(logo).pixmap(96, 96))
        gcc = toolchains.find("gcc")
        box.setText(
            f"<h3>MEDHĀ IDE {__version__}</h3>"
            "<p>Created by <b>Kanak Prabhakar</b> · Cooding with Kanak</p>"
            "<p>Offline IDE for C, C++, Java and Python with Turbo C graphics.h mode, "
            "debugger, beginner error explanations, security scan and visualizers.</p>"
            f"<p><small>Compiler: {gcc.version or 'not found'}<br>"
            f"Platform: {sys.platform} · Settings: {settings.settings_path()}</small></p>")
        box.exec()

    def _on_theme_apply_requested(self, colors: dict):
        """Handle theme apply request from Extensions panel."""
        from medha.extensions.contributions import map_vscode_theme_to_medha
        from medha.editor_widget import AdvancedCodeEditorWidget

        # Apply theme colors to all open editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, AdvancedCodeEditorWidget):
                # Apply palette colors
                if hasattr(editor, 'set_palette_colors'):
                    editor.set_palette_colors(colors.get("palette", {}))

                # Apply token colors to highlighter
                if hasattr(editor, 'highlighter') and editor.highlighter:
                    if hasattr(editor.highlighter, 'set_theme_formats'):
                        editor.highlighter.set_theme_formats(colors.get("token_colors", {}))

        # Apply to application stylesheet if supported
        palette_colors = colors.get("palette", {})
        if palette_colors:
            bg = palette_colors.get("editor_bg", "#0d1117")
            fg = palette_colors.get("editor_fg", "#c9d1d9")
            sel = palette_colors.get("editor_selection", "#1f6feb")
            self.apply_theme_stylesheet(bg, fg, sel)

        self.lbl_status.setText("Theme applied from extension")

    def apply_theme_stylesheet(self, bg: str, fg: str, selection: str):
        """Apply theme colors to application stylesheet."""
        # Update editor stylesheet
        style = f"""
            QPlainTextEdit, QTextEdit, QLineEdit {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {selection};
            }}
        """
        # Apply to all editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, AdvancedCodeEditorWidget):
                editor.setStyleSheet(style)
