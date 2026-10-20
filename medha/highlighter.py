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

    def set_theme_formats(self, token_colors: dict) -> None:
        """
        Apply theme token colors to the highlighter formats.

        Args:
            token_colors: Dict mapping token type -> format dict with
                          'foreground', 'background', 'fontStyle' keys
        """
        # Map MEDHA token types to internal format attributes
        token_format_map = {
            "keyword": "fmt_keyword",
            "keyword_operator": "fmt_keyword",
            "string": "fmt_string",
            "string_regex": "fmt_string",
            "comment": "fmt_comment",
            "number": "fmt_number",
            "type": "fmt_type",
            "function": "fmt_function",
            "function_call": "fmt_function",
            "constant": "fmt_constant",
            "constant_char": "fmt_constant",
            "constant_lang": "fmt_constant",
            "entity": "fmt_entity",
            "entity_name": "fmt_entity",
            "class_name": "fmt_type",
            "tag": "fmt_tag",
            "variable": "fmt_variable",
            "variable_lang": "fmt_variable",
            "parameter": "fmt_parameter",
            "storage": "fmt_storage",
            "storage_modifier": "fmt_storage",
            "support": "fmt_support",
            "support_function": "fmt_support_function",
            "support_class": "fmt_support_class",
            "support_type": "fmt_support_type",
            "support_constant": "fmt_support_constant",
            "support_variable": "fmt_support_variable",
            "markup": "fmt_markup",
            "heading": "fmt_heading",
            "bold": "fmt_bold",
            "italic": "fmt_italic",
            "underline": "fmt_underline",
            "link": "fmt_link",
            "quote": "fmt_quote",
            "list": "fmt_list",
            "meta": "fmt_meta",
            "meta_brace": "fmt_meta",
            "meta_tag": "fmt_meta",
            "invalid": "fmt_invalid",
            "deprecated": "fmt_deprecated",
        }

        for token_type, format_dict in token_colors.items():
            if token_type not in token_format_map:
                continue
            fmt_attr = token_format_map[token_type]
            if not hasattr(self, fmt_attr):
                # Create format if it doesn't exist
                setattr(self, fmt_attr, QTextCharFormat())
            fmt = getattr(self, fmt_attr)

            if "foreground" in format_dict and format_dict["foreground"]:
                fmt.setForeground(QColor(format_dict["foreground"]))
            if "background" in format_dict and format_dict["background"]:
                fmt.setBackground(QColor(format_dict["background"]))
            if "fontStyle" in format_dict:
                style = format_dict["fontStyle"]
                if "italic" in style:
                    fmt.setFontItalic(True)
                if "bold" in style:
                    fmt.setFontWeight(QFont.Weight.Bold)
                if "underline" in style:
                    fmt.setFontUnderline(True)

        # Re-highlight the entire document
        self.rehighlight()
