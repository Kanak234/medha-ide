"""
MEDHĀ IDE — turbo/panel.py — the 640×480 Turbo C screen inside MEDHĀ
=====================================================================

WHAT:  A dock panel that shows the graphics.h / conio.h screen of the running
       program, sends keyboard keys to it exactly like Turbo C expects
       (arrows → 0 + scan code, Enter → "\\r\\n"), and can save a screenshot PNG.
WHY:   C-Lite draws graphics in a separate Windows-only GDI window. MEDHĀ shows the
       same output on Windows AND Linux, docked next to the code, from the same
       framebuffer the program really wrote (no fake rendering): every pixel here
       comes from turbo/protocol.py decoding the program's own output.
USED BY: app.py (dock "Turbo C Screen"); runner.py feeds frames via turbo_frame.
FLOW:  runner.turbo_frame(decoder) → show_frame() → QImage(Indexed8) → paint
       keyPressEvent → key_bytes() → runner.write_stdin(bytes) → program's getch()
"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, qRgb
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)

# Turbo C extended keys: getch() returns 0, then this scan code (Borland convention).
SCAN = {
    Qt.Key.Key_Up: 72, Qt.Key.Key_Left: 75, Qt.Key.Key_Right: 77, Qt.Key.Key_Down: 80,
    Qt.Key.Key_Home: 71, Qt.Key.Key_End: 79, Qt.Key.Key_PageUp: 73, Qt.Key.Key_PageDown: 81,
    Qt.Key.Key_Insert: 82, Qt.Key.Key_Delete: 83,
    Qt.Key.Key_F1: 59, Qt.Key.Key_F2: 60, Qt.Key.Key_F3: 61, Qt.Key.Key_F4: 62, Qt.Key.Key_F5: 63,
    Qt.Key.Key_F6: 64, Qt.Key.Key_F7: 65, Qt.Key.Key_F8: 66, Qt.Key.Key_F9: 67, Qt.Key.Key_F10: 68,
}


def key_bytes(key, text):
    """Bytes a Turbo C program receives for one key press (None = ignore)."""
    if key in SCAN:
        return bytes([0, SCAN[key]])
    if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
        return b"\r\n"            # getch() sees 13, scanf/fgets see a full line
    if key == Qt.Key.Key_Backspace:
        return b"\x08"
    if key == Qt.Key.Key_Escape:
        return b"\x1b"
    if key == Qt.Key.Key_Tab:
        return b"\t"
    if text:
        return text.encode("utf-8")
    return None


class TurboScreen(QWidget):
    """Paints the framebuffer scaled to fit, keeping the 4:3 Turbo aspect ratio."""

    key_pressed = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage(640, 480, QImage.Format.Format_Indexed8)
        self.image.fill(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)   # so it receives key presses
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_frame(self, decoder):
        w, h = decoder.width, decoder.height
        # Indexed8: one byte per pixel + a 16-entry colour table — exactly the
        # Turbo C model, so no per-pixel Python conversion is needed (fast).
        img = QImage(bytes(decoder.framebuffer), w, h, w, QImage.Format.Format_Indexed8)
        img.setColorTable([qRgb(*c) for c in decoder.palette] + [qRgb(0, 0, 0)] * (256 - 16))
        self.image = img.copy()          # own the memory (the bytes object is temporary)
        self.update()

    def target_rect(self):
        w, h = self.width(), self.height()
        scale = min(w / self.image.width(), h / self.image.height())
        tw, th = int(self.image.width() * scale), int(self.image.height() * scale)
        return (w - tw) // 2, (h - th) // 2, tw, th

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#000000"))
        x, y, w, h = self.target_rect()
        # nearest-neighbour scaling keeps the crisp pixel look of a VGA screen
        p.drawImage(x, y, self.image.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.FastTransformation))
        if self.hasFocus():
            p.setPen(QColor("#1f6feb"))
            p.drawRect(x, y, w - 1, h - 1)

    def keyPressEvent(self, e):
        data = key_bytes(e.key(), e.text())
        if data:
            self.key_pressed.emit(data)
        else:
            super().keyPressEvent(e)


class TurboPanel(QWidget):
    """Toolbar (status · screenshot · stop) + the screen."""

    stop_requested = Signal()
    key_for_program = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        self.status = QLabel("Turbo C screen (640×480) — run a graphics.h / conio.h program")
        self.status.setStyleSheet("color:#8b949e; padding:4px;")
        bar.addWidget(self.status, 1)
        self.btn_shot = QPushButton("Save PNG")
        self.btn_shot.setToolTip("Save the current screen as an image (for lab records)")
        self.btn_shot.clicked.connect(self.save_png)
        bar.addWidget(self.btn_shot)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        bar.addWidget(self.btn_stop)
        lay.addLayout(bar)
        self.screen = TurboScreen(self)
        self.screen.key_pressed.connect(self.key_for_program.emit)
        lay.addWidget(self.screen, 1)
        self.last_dir = os.path.expanduser("~")

    # called by app.py
    def on_started(self, uses_panel):
        self.status.setText("Running — click the screen and use the keyboard" if uses_panel
                            else "Running (console Turbo program)")
        self.screen.setFocus()

    def on_frame(self, decoder):
        self.screen.set_frame(decoder)

    def on_message(self, msg):
        t = msg.get("t")
        if t == "input":
            self.status.setText("Waiting for a key… (click the screen, then press any key)")
            self.screen.setFocus()
        elif t == "sound":
            hz = msg.get("hz", 0)
            self.status.setText(f"sound({hz} Hz)" if hz else "nosound()")

    def on_finished(self, code):
        self.status.setText(f"Program finished (return value {code}) — screen kept for review")

    def save_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Turbo C screen", os.path.join(self.last_dir, "output.png"),
                                              "PNG image (*.png)")
        if path:
            self.screen.image.convertToFormat(QImage.Format.Format_RGB32).save(path, "PNG")
            self.last_dir = os.path.dirname(path)
            self.status.setText(f"Saved {os.path.basename(path)}")
