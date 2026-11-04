from medha.terminal_text import TerminalText


def test_conpty_controls_split_at_every_boundary():
    raw = '\x1b[?25l\x1b[2J\x1b]0;cmd.exe\x07C:\\work>\x1b[?25h\r\n'
    for split in range(len(raw) + 1):
        renderer = TerminalText()
        assert renderer.feed(raw[:split]) + renderer.feed(raw[split:]) == 'C:\\work>\r\n'


def test_unicode_and_program_output_survive_control_strings():
    renderer = TerminalText()
    result = ''.join(renderer.feed(c) for c in '\x1b]title\x1b\\नमस्ते\tANSWER=42\n\x1b[0m')
    assert result == 'नमस्ते\tANSWER=42\n'
