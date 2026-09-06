from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from medha.ai import AiAssistant

class AiStreamWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()

    def __init__(self, ai_assistant: AiAssistant, prompt: str, context: str = ""):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.prompt = prompt
        self.context = context

    def run(self):
        for chunk in self.ai_assistant.complete_stream(self.prompt, self.context):
            self.chunk_received.emit(chunk)
        self.finished.emit()


class AiAssistantPanelWidget(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.ai = AiAssistant()
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        # Header Status
        self.lbl_status = QLabel("Local AI Assistant (Ollama)")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #58a6ff;")
        layout.addWidget(self.lbl_status)

        # Model Selector
        hdr_layout = QHBoxLayout()
        hdr_layout.addWidget(QLabel("Model:"))
        self.combo_models = QComboBox()
        hdr_layout.addWidget(self.combo_models, 1)
        layout.addLayout(hdr_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_explain = QPushButton("Explain Code")
        self.btn_bug = QPushButton("Find Bug")
        btn_layout.addWidget(self.btn_explain)
        btn_layout.addWidget(self.btn_bug)
        layout.addLayout(btn_layout)

        # Response Output
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("AI streaming response will appear here...")
        layout.addWidget(self.txt_output, 1)

        # Free Chat Input
        chat_layout = QHBoxLayout()
        self.input_prompt = QLineEdit()
        self.input_prompt.setPlaceholderText("Ask local AI...")
        self.btn_send = QPushButton("Send")
        chat_layout.addWidget(self.input_prompt, 1)
        chat_layout.addWidget(self.btn_send)
        layout.addLayout(chat_layout)

        # Connect actions
        self.btn_explain.clicked.connect(self.action_explain_code)
        self.btn_bug.clicked.connect(self.action_find_bug)
        self.btn_send.clicked.connect(self.action_free_chat)
        self.input_prompt.returnPressed.connect(self.action_free_chat)

        self.refresh_availability()

    def refresh_availability(self):
        if self.ai.available():
            models = self.ai.models()
            self.combo_models.clear()
            self.combo_models.addItems(models)
            self.lbl_status.setText("Local AI Assistant — Ollama Connected (127.0.0.1:11434)")
            self.lbl_status.setStyleSheet("font-weight: bold; color: #3fb950;")
        else:
            self.combo_models.clear()
            self.lbl_status.setText("Ollama local service unavailable on http://127.0.0.1:11434")
            self.lbl_status.setStyleSheet("font-weight: bold; color: #f85149;")
            self.txt_output.setPlainText("Local AI service (Ollama) is not running on http://127.0.0.1:11434.")

    def get_editor_context(self) -> str:
        editor = self.main_window.get_current_editor() if hasattr(self.main_window, 'get_current_editor') else None
        if editor:
            return editor.toPlainText()
        return ""

    def start_stream(self, prompt: str):
        if not self.ai.available():
            self.refresh_availability()
            return

        selected_model = self.combo_models.currentText()
        if selected_model:
            self.ai.model = selected_model

        ctx = self.get_editor_context()
        self.txt_output.clear()

        self.worker = AiStreamWorker(self.ai, prompt, ctx)
        self.worker.chunk_received.connect(self.append_chunk)
        self.worker.start()

    def append_chunk(self, chunk: str):
        self.txt_output.moveCursor(self.txt_output.textCursor().MoveOperation.End)
        self.txt_output.insertPlainText(chunk)

    def action_explain_code(self):
        self.start_stream("Explain the given code clearly and concisely.")

    def action_find_bug(self):
        self.start_stream("Find potential bugs, logical errors, or edge cases in the given code.")

    def action_free_chat(self):
        text = self.input_prompt.text().strip()
        if text:
            self.input_prompt.clear()
            self.start_stream(text)
