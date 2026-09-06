import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language="cpp"):
        super().__init__(parent)
        self.language = language.lower()
        self.rules = []

        # Color Palette - Professional Dark Theme
        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setForeground(QColor("#c678dd"))
        self.fmt_keyword.setFontWeight(QFont.Weight.Bold)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(QColor("#98c379"))

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor("#5c6370"))
        self.fmt_comment.setFontItalic(True)

        self.fmt_number = QTextCharFormat()
        self.fmt_number.setForeground(QColor("#d19a66"))

        self.fmt_type = QTextCharFormat()
        self.fmt_type.setForeground(QColor("#e5c07b"))

        self.fmt_function = QTextCharFormat()
        self.fmt_function.setForeground(QColor("#61afef"))

        self.setup_rules()

    def setup_rules(self):
        keywords = []
        types = []

        if self.language in ["c", "cpp", "c++"]:
            keywords = ["auto", "break", "case", "catch", "class", "const", "continue", "default", "delete", "do", "else", "enum", "explicit", "export", "extern", "for", "friend", "goto", "if", "inline", "namespace", "new", "operator", "private", "protected", "public", "return", "sizeof", "static", "struct", "switch", "template", "this", "throw", "try", "typedef", "using", "virtual", "while", "#include", "#define", "#pragma", "#ifdef", "#ifndef", "#endif"]
            types = ["int", "char", "float", "double", "void", "bool", "long", "short", "unsigned", "signed", "std::string", "std::vector", "std::map", "size_t"]
        elif self.language in ["python", "py"]:
            keywords = ["and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield", "None", "True", "False"]
            types = ["int", "float", "str", "list", "dict", "set", "tuple", "bool", "bytes", "object", "self"]
        elif self.language in ["java"]:
            keywords = ["public", "private", "protected", "class", "interface", "extends", "implements", "static", "final", "void", "return", "if", "else", "for", "while", "do", "switch", "case", "new", "this", "super", "try", "catch", "finally", "throw", "throws", "import", "package"]
            types = ["int", "long", "short", "byte", "float", "double", "boolean", "char", "String", "System"]
        else:
            keywords = ["function", "var", "let", "const", "if", "else", "for", "while", "return", "import", "export", "from", "class", "extends", "super", "null", "undefined", "true", "false", "try", "catch", "async", "await"]
            types = ["number", "string", "boolean", "any", "void", "Promise"]

        for kw in keywords:
            pattern = QRegularExpression(rf"\b{re.escape(kw)}\b" if not kw.startswith("#") else rf"{re.escape(kw)}\b")
            self.rules.append((pattern, self.fmt_keyword))

        for t in types:
            pattern = QRegularExpression(rf"\b{re.escape(t)}\b")
            self.rules.append((pattern, self.fmt_type))

        # Numbers
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), self.fmt_number))

        # Strings ("..." or '...')
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.fmt_string))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.fmt_string))

        # Single line comments (// or #)
        self.rules.append((QRegularExpression(r"//.*"), self.fmt_comment))
        self.rules.append((QRegularExpression(r"#.*"), self.fmt_comment))

        # Function declarations
        self.rules.append((QRegularExpression(r"\b[A-Za-z_][A-Za-z0-9_]*(?=\s*\()"), self.fmt_function))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
