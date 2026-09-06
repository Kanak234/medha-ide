import os
import re
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtGui import QColor, QPainter, QTextFormat, QFont, QTextCursor
from PySide6.QtCore import Qt, QRect, QSize
from medha.highlighter import CodeHighlighter

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class CodeEditorWidget(QPlainTextEdit):
    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self.line_number_area = LineNumberArea(self)

        # Highlighting
        self.lang = self.detect_language(file_path)
        self.highlighter = CodeHighlighter(self.document(), language=self.lang)

        # Styling
        font = QFont("JetBrains Mono", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1f22;
                color: #bcbec4;
                border: none;
                selection-background-color: #214283;
                selection-color: #ffffff;
            }
        """)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self.on_text_changed)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def on_text_changed(self):
        self.is_modified = True

    def detect_language(self, path):
        if not path:
            return "cpp"
        ext = os.path.splitext(path)[1].lower()
        if ext in [".c", ".h"]: return "c"
        if ext in [".cpp", ".hpp", ".cc", ".cxx"]: return "cpp"
        if ext in [".py"]: return "python"
        if ext in [".java"]: return "java"
        if ext in [".js", ".ts", ".jsx", ".tsx"]: return "javascript"
        return "cpp"

    def line_number_area_width(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1f22"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        curr_block_num = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == curr_block_num:
                    painter.setPen(QColor("#a1a3ab"))
                else:
                    painter.setPen(QColor("#4b5059"))
                font = self.font()
                painter.setFont(font)
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def find_matching_bracket(self, cursor):
        doc = self.document()
        pos = cursor.position()
        text = doc.toPlainText()
        if not text:
            return None, None

        pairs = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
        char_at = text[pos] if pos < len(text) else ''
        char_before = text[pos - 1] if pos > 0 else ''

        bracket_pos = None
        bracket_char = None

        if char_at in pairs:
            bracket_pos = pos
            bracket_char = char_at
        elif char_before in pairs:
            bracket_pos = pos - 1
            bracket_char = char_before

        if bracket_pos is None:
            return None, None

        target = pairs[bracket_char]
        forward = bracket_char in '([{`'
        step = 1 if forward else -1
        depth = 0

        curr = bracket_pos
        while 0 <= curr < len(text):
            ch = text[curr]
            if ch == bracket_char:
                depth += 1
            elif ch == target:
                depth -= 1
                if depth == 0:
                    return bracket_pos, curr
            curr += step

        return None, None

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            # 1. Current-line highlight (#26282e)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#26282e"))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

            # 3. Bracket match highlight (#3a3d41)
            pos1, pos2 = self.find_matching_bracket(self.textCursor())
            if pos1 is not None and pos2 is not None:
                for p in (pos1, pos2):
                    bracket_sel = QTextEdit.ExtraSelection()
                    bracket_sel.format.setBackground(QColor("#3a3d41"))
                    bracket_sel.format.setForeground(QColor("#ffffff"))
                    c = QTextCursor(self.document())
                    c.setPosition(p)
                    c.setPosition(p + 1, QTextCursor.MoveMode.KeepAnchor)
                    bracket_sel.cursor = c
                    extra_selections.append(bracket_sel)

        self.setExtraSelections(extra_selections)
        self.line_number_area.update()

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        # 4. Auto-indent on Enter
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line_text = cursor.block().text()
            leading = re.match(r'^\s*', line_text).group(0) if line_text else ""
            stripped = line_text.strip()
            if stripped.endswith('{') or stripped.endswith(':'):
                leading += "    "
            super().keyPressEvent(event)
            self.insertPlainText(leading)
            return

        # 5. Auto-close brackets and quotes
        pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        closing = (')', ']', '}', '"', "'")

        if text in closing and not self.textCursor().hasSelection():
            cursor = self.textCursor()
            pos = cursor.position()
            doc_text = self.toPlainText()
            if pos < len(doc_text) and doc_text[pos] == text:
                cursor.movePosition(QTextCursor.MoveOperation.Next)
                self.setTextCursor(cursor)
                return

        if text in pairs and not self.textCursor().hasSelection():
            cursor = self.textCursor()
            cursor.insertText(text + pairs[text])
            cursor.movePosition(QTextCursor.MoveOperation.Previous)
            self.setTextCursor(cursor)
            return

        super().keyPressEvent(event)
