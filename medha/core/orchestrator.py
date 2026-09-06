"""
MEDHĀ IDE — Anti-Gravity Core Event Bus & State Orchestrator
Decoupled central event bus managing application state, multi-language compiler jobs,
GDB debug sessions, DSA graph snapshots, and defensive process lifecycle cleanup.
"""

import os
import sys
import psutil
from PySide6.QtCore import QObject, Signal, Qt


class AntiGravityOrchestrator(QObject):
    """
    Central event bus and state orchestrator for MEDHĀ IDE.
    All UI panels, compiler threads, debugger engines, and visualizers
    communicate exclusively through thread-safe Qt Signals.
    """

    # --- Global Event Bus Signals ---
    active_file_changed = Signal(str)            # file_path
    build_config_changed = Signal(str)           # "Debug" | "Release"
    compiler_output_stream = Signal(str, str)    # text, stream_type ('stdout' | 'stderr')
    compiler_finished = Signal(int, list, str)   # exit_code, diagnostics, artifact_path
    dsa_snapshot_emitted = Signal(object)        # DSAGraphSnapshot object
    gdb_state_changed = Signal(str, dict)        # state_name, variables_dict
    status_message_emitted = Signal(str)         # status_text

    def __init__(self, parent=None):
        super().__init__(parent)

        # State Storage
        self.active_file = ""
        self.build_config = "Debug"
        self.workspace_path = os.getcwd()
        self.active_processes = []

        # Setup System Exception Hook Guardrail
        sys.excepthook = self._global_exception_handler

    def set_active_file(self, file_path):
        if file_path and os.path.exists(file_path):
            self.active_file = file_path
            self.active_file_changed.emit(file_path)
            self.status_message_emitted.emit(f"Active File: {file_path}")

    def set_build_config(self, config_name):
        if config_name in ["Debug", "Release"]:
            self.build_config = config_name
            self.build_config_changed.emit(config_name)
            self.status_message_emitted.emit(f"Target Config: {config_name}")

    def register_process(self, qprocess):
        """Tracks active QProcess instances to prevent zombie processes on exit."""
        if qprocess not in self.active_processes:
            self.active_processes.append(qprocess)

    def cleanup_all_processes(self):
        """Crash guardrail: Cleanly terminates and kills all background processes."""
        for proc in self.active_processes:
            try:
                if proc and proc.state() != 0: # NotRunning = 0
                    proc.terminate()
                    if not proc.waitForFinished(300):
                        proc.kill()
            except Exception:
                pass
        self.active_processes.clear()

    def _global_exception_handler(self, exctype, value, traceback_obj):
        """Global unhandled exception interceptor preventing silent GUI crashes."""
        print(f"[MEDHĀ Anti-Gravity Guardrail] Intercepted Exception: {exctype.__name__}: {value}", file=sys.stderr)
