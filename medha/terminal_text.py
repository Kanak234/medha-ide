"""Remove terminal protocol controls from the line-oriented output widget.

State survives read boundaries: ConPTY can split CSI and window-title OSC
sequences between chunks. Printable text, tabs and newlines remain visible.
This is a text transcript, not a full-screen terminal emulator.
"""


class TerminalText:
    def __init__(self):
        self.state = 'text'

    def feed(self, text):
        visible = []
        for char in text:
            if self.state == 'text':
                if char == '\x1b':
                    self.state = 'escape'
                elif char in '\n\r\t' or ord(char) >= 32:
                    visible.append(char)
            elif self.state == 'escape':
                if char == '[':
                    self.state = 'csi'
                elif char == ']':
                    self.state = 'osc'
                elif char in 'PX^_':
                    self.state = 'string'
                elif char in '()*+':
                    self.state = 'charset'
                else:
                    self.state = 'text'
            elif self.state == 'csi':
                if '@' <= char <= '~':
                    self.state = 'text'
            elif self.state in ('osc', 'string'):
                if char == '\x07':
                    self.state = 'text'
                elif char == '\x1b':
                    self.state = 'string_escape'
            elif self.state == 'string_escape':
                self.state = 'text' if char == '\\' else 'string'
            elif self.state == 'charset':
                self.state = 'text'
        return ''.join(visible)
