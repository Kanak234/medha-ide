"""
MEDHĀ IDE — Advanced Code Editor & Outline Widget
Features:
  1. C/C++/Python/Java syntax highlighting & auto-indentation.
  2. Margin line numbers, breakpoint toggle (red dots), current execution line highlight (yellow marker).
  3. Symbol Outline parser & quick navigation for functions, structs, and variables.
  4. Snippet expansion with tabstop navigation ($1, $2, ..., $0).
"""

import os
import re
from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QPlainTextEdit, QWidget, QTextEdit, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QSplitter
)
from PySide6.QtGui import QColor, QPainter, QTextFormat, QFont, QTextCursor
from PySide6.QtCore import Qt, QRect, QSize, Signal
from medha.highlighter import CodeHighlighter

if TYPE_CHECKING:
    from medha.extensions.models import VSCodeSnippet


class MarginArea(QWidget):
    """Line number and breakpoint margin area for CodeEditorWidget."""

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.margin_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.marginAreaPaintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            y = event.y()
            block = self.code_editor.firstVisibleBlock()
            top = round(self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top())
            bottom = top + round(self.code_editor.blockBoundingRect(block).height())

            while block.isValid() and top <= y:
                if top <= y <= bottom:
                    line_num = block.blockNumber() + 1
                    self.code_editor.toggle_breakpoint(line_num)
                    break
                block = block.next()
                top = bottom
                bottom = top + round(self.code_editor.blockBoundingRect(block).height())


class AdvancedCodeEditorWidget(QPlainTextEdit):
    """
    Production-ready C/C++ Code Editor with Margin Breakpoints,
    Execution Line Pointer, and Syntax Highlighting.
    """

    breakpoint_toggled = Signal(str, int, bool) # file_path, line, is_set

    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self.margin_area = MarginArea(self)
        self.breakpoints = set()
        self.execution_line = None
        self.snippet_tabstops = []  # List of (tabstop_num, start_pos, end_pos)

        # Highlighting
        self.lang = self.detect_language(file_path)
        self.highlighter = CodeHighlighter(self.document(), language=self.lang)

        # Font & Style
        font = QFont("Monospace", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                selection-background-color: #1f6feb;
                selection-color: #ffffff;
            }
        """)

        self.blockCountChanged.connect(self.update_margin_area_width)
        self.updateRequest.connect(self.update_margin_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self.on_text_changed)

        self.update_margin_area_width(0)
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
        if ext in [".js", ".ts"]: return "javascript"
        return "cpp"

    def margin_area_width(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        return 30 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_margin_area_width(self, _):
        self.setViewportMargins(self.margin_area_width(), 0, 0, 0)

    def update_margin_area(self, rect, dy):
        if dy:
            self.margin_area.scroll(0, dy)
        else:
            self.margin_area.update(0, rect.y(), self.margin_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_margin_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.margin_area.setGeometry(QRect(cr.left(), cr.top(), self.margin_area_width(), cr.height()))

    def toggle_breakpoint(self, line_num):
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)
            is_set = False
        else:
            self.breakpoints.add(line_num)
            is_set = True
        self.margin_area.update()
        if self.file_path:
            self.breakpoint_toggled.emit(self.file_path, line_num, is_set)

    def set_execution_line(self, line_num):
        self.execution_line = line_num
        self.highlight_current_line()
        self.margin_area.update()
        if line_num and line_num > 0:
            block = self.document().findBlockByLineNumber(line_num - 1)
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)

    def clear_execution_line(self):
        self.execution_line = None
        self.highlight_current_line()
        self.margin_area.update()

    def marginAreaPaintEvent(self, event):
        painter = QPainter(self.margin_area)
        painter.fillRect(event.rect(), QColor("#161b22"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        curr_block_num = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1
                # 1. Draw Breakpoint Red Dot
                if line_num in self.breakpoints:
                    painter.setBrush(QColor("#f85149"))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(4, top + 3, 10, 10)

                # 2. Draw Execution Pointer Yellow Arrow
                if self.execution_line == line_num:
                    painter.setPen(QColor("#e3b341"))
                    painter.drawText(16, top, 12, self.fontMetrics().height(), Qt.AlignLeft, "▶")

                # 3. Draw Line Number
                painter.setPen(QColor("#a1a3ab") if block_number == curr_block_num else QColor("#4b5059"))
                painter.setFont(self.font())
                painter.drawText(0, top, self.margin_area.width() - 5, self.fontMetrics().height(), Qt.AlignRight, str(line_num))

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            # Current cursor line (#21262d)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#161b22"))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

            # Execution Line Highlight (#3d3200)
            if self.execution_line and self.execution_line > 0:
                exec_block = self.document().findBlockByLineNumber(self.execution_line - 1)
                exec_sel = QTextEdit.ExtraSelection()
                exec_sel.format.setBackground(QColor("#3d3200"))
                exec_sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                c = QTextCursor(self.document())
                c.setPosition(exec_block.position())
                exec_sel.cursor = c
                extra_selections.append(exec_sel)

        self.setExtraSelections(extra_selections)
        self.margin_area.update()

    def get_symbol_outline(self):
        """Scans document text for functions, structs, and classes."""
        text = self.toPlainText()
        symbols = []

        # C/C++ Functions: int main(void), void foo_bar()
        func_regex = re.compile(r'^(?:[a-zA-Z_]\w*\s+)+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', re.MULTILINE)
        for match in func_regex.finditer(text):
            func_name = match.group(1)
            line = text[:match.start()].count('\n') + 1
            symbols.append((f"ƒ {func_name}()", "function", line))

        # C/C++ Structs/Classes: struct Foo, class Bar
        type_regex = re.compile(r'^(?:struct|class|enum)\s+([a-zA-Z_]\w*)', re.MULTILINE)
        for match in type_regex.finditer(text):
            t_name = match.group(1)
            line = text[:match.start()].count('\n') + 1
            symbols.append((f"📦 {t_name}", "struct", line))

        return symbols

    def keyPressEvent(self, event):
        key = event.key()
        # Auto-indentation on Return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line_text = cursor.block().text()
            leading = re.match(r'^\s*', line_text).group(0) if line_text else ""
            if line_text.strip().endswith('{') or line_text.strip().endswith(':'):
                leading += "    "
            super().keyPressEvent(event)
            self.insertPlainText(leading)
            return

        # Snippet tab-stop navigation (Tab/Shift+Tab)
        if key == Qt.Key.Key_Tab and self.snippet_tabstops:
            self._jump_to_next_tabstop()
            return
        if key == Qt.Key.Key_Backtab and self.snippet_tabstops:  # Shift+Tab
            self._jump_to_prev_tabstop()
            return

        super().keyPressEvent(event)

    def set_palette_colors(self, palette: dict) -> None:
        """
        Apply theme palette colors to the editor.

        Args:
            palette: Dict mapping MEDHA color keys -> hex color strings
        """
        style_parts = []

        # Editor background/foreground
        if "editor_bg" in palette:
            style_parts.append(f"background-color: {palette['editor_bg']};")
        if "editor_fg" in palette:
            style_parts.append(f"color: {palette['editor_fg']};")
        if "editor_selection" in palette:
            style_parts.append(f"selection-background-color: {palette['editor_selection']};")
        if "editor_cursor" in palette:
            style_parts.append(f"caret-color: {palette['editor_cursor']};")

        # Line numbers
        if "linenumber_fg" in palette:
            style_parts.append(f"QAbstractScrollArea {{ color: {palette['linenumber_fg']}; }}")

        # Apply stylesheet
        if style_parts:
            self.setStyleSheet(f"QPlainTextEdit {{ {' '.join(style_parts)} }}")

        # Update margin area background
        if "editor_bg" in palette:
            self.margin_area.setStyleSheet(f"background-color: {palette['editor_bg']};")

        # Trigger repaint
        self.viewport().update()
        self.margin_area.update()

    def set_snippet(self, snippet: 'VSCodeSnippet') -> None:
        """
        Insert a snippet at cursor position and set up tabstops.

        Args:
            snippet: VSCodeSnippet to insert
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()

        body_lines = snippet.body
        if isinstance(body_lines, str):
            body_lines = [body_lines]

        # Insert the snippet body
        for i, line in enumerate(body_lines):
            if i > 0:
                cursor.insertText("\n")
            cursor.insertText(line)

        # Find and store tabstop positions BEFORE removing markers
        self.snippet_tabstops = []
        import re
        text = self.toPlainText()
        for match in re.finditer(r'\$(\d+)', text):
            tabstop_num = int(match.group(1))
            pos = match.start()
            self.snippet_tabstops.append((tabstop_num, pos, pos + len(match.group(0))))

        # Sort by position (highest first) for removal
        tabstops_by_position = sorted(self.snippet_tabstops, key=lambda x: x[1], reverse=True)

        # Remove markers from highest position to lowest
        # Original positions are valid since earlier removals don't affect earlier positions
        for num, start, end in tabstops_by_position:
            cursor = self.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            # After removal, the tabstop position is at 'start' (where the marker was)
            # We'll update the stored positions after all removals

        # Update tabstops: positions are now at the original start positions
        # (since we removed the marker text, the cursor position is where the marker started)
        updated_tabstops = [(num, start, start) for num, start, end in self.snippet_tabstops]
        # Sort by tabstop number for navigation
        updated_tabstops.sort(key=lambda x: x[0])
        self.snippet_tabstops = updated_tabstops

        cursor.endEditBlock()

        # Move cursor to first tabstop ($1) or $0 if no $1
        self._jump_to_tabstop(1)  # Try $1 first

    def _jump_to_tabstop(self, tabstop_num: int) -> bool:
        """Jump to a specific tabstop number."""
        for num, start, end in self.snippet_tabstops:
            if num == tabstop_num:
                cursor = self.textCursor()
                cursor.setPosition(start)
                cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
                self.setTextCursor(cursor)
                return True
        return False

    def _jump_to_next_tabstop(self) -> None:
        """Jump to the next tabstop in sequence."""
        cursor = self.textCursor()
        current_pos = cursor.position()

        # Find current tabstop
        current_num = 0
        for num, start, end in self.snippet_tabstops:
            if start <= current_pos <= end:
                current_num = num
                break

        # Jump to next
        next_num = current_num + 1
        if not self._jump_to_tabstop(next_num):
            # Try $0 (final position)
            self._jump_to_tabstop(0)

    def _jump_to_prev_tabstop(self) -> None:
        """Jump to the previous tabstop in sequence."""
        cursor = self.textCursor()
        current_pos = cursor.position()

        # Find current tabstop
        current_num = 0
        for num, start, end in self.snippet_tabstops:
            if start <= current_pos <= end:
                current_num = num
                break

        if current_num > 1:
            self._jump_to_tabstop(current_num - 1)

    def get_snippet_tabstops(self) -> list:
        """Get list of tabstops for testing."""
        return getattr(self, 'snippet_tabstops', [])


class CodeOutlineWidget(QWidget):
    """Symbol Navigation Outline Panel."""

    symbol_selected = Signal(int) # line_number

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(" SYMBOL OUTLINE")
        header.setStyleSheet("background-color: #161b22; color: #8b949e; font-weight: bold; font-size: 11px; padding: 4px;")
        layout.addWidget(header)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
            }
            QListWidget::item:hover { background-color: #161b22; }
            QListWidget::item:selected { background-color: #1f6feb; color: white; }
        """)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

    def update_outline(self, symbols):
        self.list_widget.clear()
        for label, kind, line in symbols:
            item = QListWidgetItem(f"{label} (Ln {line})")
            item.setData(Qt.UserRole, line)
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        line = item.data(Qt.UserRole)
        if line:
            self.symbol_selected.emit(line)
