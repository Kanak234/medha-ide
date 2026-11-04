"""
Unit tests for medha/turbo/ — Turbo C mode (graphics.h / conio.h / dos.h / iostream.h).

Tests cover:
- turbo/lexer.py: masked source generation
- turbo/adapt.py: void main → int main, far/near/huge removal
- turbo/protocol.py: PRABHA protocol decoding
- turbo/builder.py: BuildPlan generation
- turbo/modernize.py: Turbo → modern C/C++ rewriting
"""

import base64
import json
import os
import tempfile
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from medha.turbo import adapt, builder, lexer, protocol, modernize


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


# ---------------------------------------------------------------------------
# turbo/lexer.py tests
# ---------------------------------------------------------------------------

class TestLexer:
    def test_lex_masks_comments(self):
        """lex() replaces comments with spaces, preserving newlines."""
        src = "int main() {\n  // comment\n  /* block */\n  return 0;\n}"
        lx = lexer.lex(src)
        assert "// comment" not in lx.masked
        assert "/* block */" not in lx.masked
        assert lx.masked.count("\n") == src.count("\n")

    def test_lex_masks_strings(self):
        """lex() replaces string literals with spaces."""
        src = 'printf("hello world");'
        lx = lexer.lex(src)
        assert "hello world" not in lx.masked
        assert '"' not in lx.masked or lx.masked.count('"') == 2  # quotes may remain

    def test_lex_masks_char_literals(self):
        """lex() replaces char literals with spaces."""
        src = "char c = 'a';"
        lx = lexer.lex(src)
        assert "'a'" not in lx.masked

    def test_lex_preserves_preprocessor(self):
        """lex() captures preprocessor lines in preproc list."""
        src = "#include <stdio.h>\n#define FOO 1"
        lx = lexer.lex(src)
        assert len(lx.preproc) == 2
        assert "<stdio.h>" in lx.preproc[0].text
        assert "FOO" in lx.preproc[1].text

    def test_lex_raw_strings(self):
        """lex() handles C++11 raw string literals."""
        src = 'R"delim(hello)delim"'
        lx = lexer.lex(src)
        assert len(lx.strings) == 1
        assert lx.strings[0].kind == "raw"

    def test_match_bracket_finds_matching_brace(self):
        """match_bracket() finds the closing brace."""
        masked = "int main() { if (x) { return 1; } return 0; }"
        open_pos = masked.index("{")
        close_pos = lexer.match_bracket(masked, open_pos)
        assert masked[close_pos] == "}"
        assert close_pos == len(masked) - 1

    def test_match_bracket_handles_nested(self):
        """match_bracket() handles nested braces correctly."""
        masked = "{ { } }"
        assert lexer.match_bracket(masked, 0) == 6
        assert lexer.match_bracket(masked, 2) == 4

    def test_line_start_end_of(self):
        """line_start/line_end/line_of compute correct positions."""
        src = "line1\nline2\nline3"
        assert lexer.line_start(src, 7) == 6  # Start of "line2"
        assert lexer.line_end(src, 7) == 11   # End of "line2"
        assert lexer.line_of(src, 7) == 2     # Line 2 (1-indexed)


# ---------------------------------------------------------------------------
# turbo/adapt.py tests
# ---------------------------------------------------------------------------

class TestAdapt:
    def test_void_main_to_int_main(self):
        """void main() with bare return; → int main() with return 0; added."""
        src = textwrap.dedent("""
            void main() {
                printf("Hello");
                return;
            }
        """)
        adapted, changed = adapt.adapt(src)
        assert "int main()" in adapted
        assert "void main()" not in adapted
        assert "return 0;" in adapted
        assert any("void main() adapted" in c for c in changed)

    def test_implicit_int_main_to_int_main(self):
        """Old-style main() → int main()."""
        src = textwrap.dedent("""
            main() {
                printf("Hello");
            }
        """)
        adapted, changed = adapt.adapt(src)
        assert "int main()" in adapted
        assert "main()" not in adapted or "int main()" in adapted

    def test_far_near_huge_removed(self):
        """far/near/huge pointer qualifiers removed."""
        src = "int far *ptr; char near *str; void huge *mem;"
        adapted, changed = adapt.adapt(src)
        assert "far" not in adapted
        assert "near" not in adapted
        assert "huge" not in adapted
        assert any("far/near/huge" in c for c in changed)

    def test_uses_panel_detects_graphics_h(self):
        """uses_panel() returns True for graphics.h programs."""
        src = "#include <graphics.h>\nint main() { initgraph(0,0,\"\"); }"
        assert adapt.uses_panel(src) is True

    def test_uses_panel_detects_conio_h(self):
        """uses_panel() returns True for conio.h programs."""
        src = "#include <conio.h>\nint main() { getch(); }"
        assert adapt.uses_panel(src) is True

    def test_uses_panel_false_for_modern(self):
        """uses_panel() returns False for modern programs."""
        src = "#include <stdio.h>\nint main() { printf(\"hi\"); }"
        assert adapt.uses_panel(src) is False

    def test_needs_turbo_true_for_graphics_h(self):
        """needs_turbo() returns True for graphics.h."""
        assert adapt.needs_turbo("#include <graphics.h>\nint main(){}") is True

    def test_needs_turbo_true_for_void_main(self):
        """needs_turbo() returns True for void main."""
        assert adapt.needs_turbo("void main() {}") is True

    def test_needs_turbo_false_for_modern(self):
        """needs_turbo() returns False for modern C."""
        assert adapt.needs_turbo("#include <stdio.h>\nint main(){return 0;}") is False


# ---------------------------------------------------------------------------
# turbo/protocol.py tests
# ---------------------------------------------------------------------------

class TestProtocolDecoder:
    def test_init_sets_defaults(self):
        """ProtocolDecoder initializes with default palette and empty framebuffer."""
        dec = protocol.ProtocolDecoder()
        assert dec.width == 640
        assert dec.height == 480
        assert len(dec.framebuffer) == 640 * 480
        assert dec.palette == protocol.DEFAULT_RGB
        assert dec.frames == 0
        assert dec.inited is False

    def test_feed_plain_text_passes_through(self):
        """Plain text without marker is returned as-is."""
        dec = protocol.ProtocolDecoder()
        text, msgs = dec.feed(b"Hello, World!\n")
        assert text == "Hello, World!\n"
        assert msgs == []

    def test_feed_marker_parses_json(self):
        """##PRABHA##{json} lines are parsed as messages."""
        dec = protocol.ProtocolDecoder()
        msg = {"t": "init", "w": 640, "h": 480}
        data = b"Normal text\n##PRABHA##" + json.dumps(msg).encode() + b"\n"
        text, msgs = dec.feed(data)
        assert "Normal text\n" in text
        assert len(msgs) == 1
        assert msgs[0]["t"] == "init"
        assert dec.width == 640
        assert dec.height == 480

    def test_feed_palette_message(self):
        """palette message updates decoder palette."""
        dec = protocol.ProtocolDecoder()
        rgb = [[i*16, i*16, i*16] for i in range(16)]
        msg = {"t": "palette", "rgb": rgb}
        data = b"##PRABHA##" + json.dumps(msg).encode() + b"\n"
        dec.feed(data)
        assert dec.palette[0] == (0, 0, 0)
        assert dec.palette[15] == (240, 240, 240)

    def test_feed_frame_rle_decoding(self):
        """frame message with RLE data updates framebuffer."""
        dec = protocol.ProtocolDecoder()
        # Create a simple 2x2 frame: all color 1 (blue)
        # RLE encode: (count, color) pairs = 4 pixels of color 1
        rle = base64.b64encode(bytes([4, 1])).decode()
        msg = {"t": "frame", "x": 0, "y": 0, "w": 2, "h": 2, "rle": rle}
        data = b"##PRABHA##" + json.dumps(msg).encode() + b"\n"
        dec.feed(data)
        assert dec.frames == 1
        assert dec.inited is True
        # Check framebuffer - 2x2 frame at (0,0) in 640-wide buffer
        # Row 0: indices 0, 1
        # Row 1: indices 640, 641
        assert dec.framebuffer[0] == 1
        assert dec.framebuffer[1] == 1
        assert dec.framebuffer[640] == 1
        assert dec.framebuffer[641] == 1

    def test_feed_marker_mid_line(self):
        """Marker in middle of line splits text and message."""
        dec = protocol.ProtocolDecoder()
        data = b"Prompt: ##PRABHA##{\"t\":\"input\"}\n"
        text, msgs = dec.feed(data)
        assert text == "Prompt: "
        assert len(msgs) == 1
        assert msgs[0]["t"] == "input"

    def test_flush_text_returns_buffered(self):
        """flush_text() returns any remaining buffered text."""
        dec = protocol.ProtocolDecoder()
        dec._pending = b"Final output"
        text = dec.flush_text()
        assert text == "Final output"
        assert dec._pending == b""

    def test_pixel_returns_color_index(self):
        """pixel(x, y) returns color index at coordinates."""
        dec = protocol.ProtocolDecoder()
        dec.framebuffer[100 * 640 + 50] = 7
        assert dec.pixel(50, 100) == 7

    def test_rgb_bytes_returns_packed_rgb(self):
        """rgb_bytes() returns framebuffer as packed RGB888."""
        dec = protocol.ProtocolDecoder()
        dec.framebuffer[0] = 1  # Blue
        rgb = dec.rgb_bytes()
        assert rgb[:3] == bytes(protocol.DEFAULT_RGB[1])

    def test_colour_histogram_counts_pixels(self):
        """colour_histogram() returns count per color index."""
        dec = protocol.ProtocolDecoder()
        # Create a small framebuffer for testing
        dec.width = 5
        dec.height = 2
        dec.framebuffer = bytearray([1] * 5 + [2] * 5)
        hist = dec.colour_histogram()
        assert hist[1] == 5
        assert hist[2] == 5
        assert sum(hist) == 10


# ---------------------------------------------------------------------------
# turbo/builder.py tests
# ---------------------------------------------------------------------------

class TestBuilder:
    @patch("medha.turbo.builder.P")
    def test_plan_creates_build_plan(self, mock_P, tmp_path):
        """plan() returns BuildPlan with steps, binary, source_map."""
        mock_P.IS_WINDOWS = False
        mock_P.EXE = ""
        mock_P.ascii_work_dir.return_value = tmp_path

        # Create a test C file
        c_file = tmp_path / "test.c"
        c_file.write_text("#include <stdio.h>\nint main() { printf(\"hi\"); }")

        cc = "/usr/bin/gcc"
        cxx = "/usr/bin/g++"
        plan = builder.plan(str(c_file), cc, cxx)

        assert isinstance(plan, builder.BuildPlan)
        assert len(plan.steps) >= 1
        assert plan.binary != ""
        assert plan.work_dir != ""
        assert plan.is_cpp is False

    @patch("medha.turbo.builder.P")
    def test_plan_cpp_uses_gpp(self, mock_P, tmp_path):
        """plan() uses g++ for .cpp files."""
        mock_P.IS_WINDOWS = False
        mock_P.EXE = ""
        mock_P.ascii_work_dir.return_value = tmp_path

        cpp_file = tmp_path / "test.cpp"
        cpp_file.write_text("#include <iostream>\nint main() { std::cout << \"hi\"; }")

        cc = "/usr/bin/gcc"
        cxx = "/usr/bin/g++"
        plan = builder.plan(str(cpp_file), cc, cxx)

        assert plan.is_cpp is True
        # Last step should use g++
        last_prog = plan.steps[-1][0]
        assert last_prog == cxx

    @patch("medha.turbo.builder.P")
    def test_plan_turbo_mode_includes_runtime(self, mock_P, tmp_path):
        """plan() for graphics.h includes runtime object and flags."""
        mock_P.IS_WINDOWS = False
        mock_P.EXE = ""
        mock_P.ascii_work_dir.return_value = tmp_path

        c_file = tmp_path / "test.c"
        c_file.write_text("#include <graphics.h>\nint main() { initgraph(0,0,\"\"); }")

        cc = "/usr/bin/gcc"
        cxx = "/usr/bin/g++"
        plan = builder.plan(str(c_file), cc, cxx)

        assert plan.uses_panel is True
        # Should have runtime compilation step
        assert any("runtime" in step[3].lower() for step in plan.steps)
        # Should link with prabha_core.o
        last_args = plan.steps[-1][1]
        assert any("prabha_core" in arg for arg in last_args)

    @patch("medha.turbo.builder.P")
    def test_plan_console_program_includes_unbuffered(self, mock_P, tmp_path):
        """Console programs get unbuffered stdout header."""
        mock_P.IS_WINDOWS = False
        mock_P.EXE = ""
        mock_P.ascii_work_dir.return_value = tmp_path

        c_file = tmp_path / "test.c"
        c_file.write_text("#include <stdio.h>\nint main() { printf(\"Enter: \"); scanf(\"%d\", &x); }")

        cc = "/usr/bin/gcc"
        cxx = "/usr/bin/g++"
        plan = builder.plan(str(c_file), cc, cxx)

        # Should include prabha_unbuffered.h for console programs
        last_args = plan.steps[-1][1]
        assert any("unbuffered" in arg for arg in last_args)

    @patch("medha.turbo.builder.P")
    def test_plan_windows_static_link(self, mock_P, tmp_path):
        """plan() adds -static on Windows."""
        mock_P.IS_WINDOWS = True
        mock_P.EXE = ".exe"
        mock_P.ascii_work_dir.return_value = tmp_path

        c_file = tmp_path / "test.c"
        c_file.write_text("int main() { return 0; }")

        cc = "C:/mingw64/bin/gcc.exe"
        cxx = "C:/mingw64/bin/g++.exe"
        plan = builder.plan(str(c_file), cc, cxx)

        last_args = plan.steps[-1][1]
        assert "-static" in last_args

    def test_core_object_path_includes_compiler_and_debug(self):
        """core_object_path() includes compiler path and debug flag in hash."""
        with tempfile.TemporaryDirectory() as tmp:
            rt = os.path.join(tmp, "runtime")
            os.makedirs(rt)
            with open(os.path.join(rt, "prabha_core.c"), "w") as f:
                f.write("int main(){}")

            with patch("medha.turbo.builder.RUNTIME_DIR", rt):
                with patch("medha.turbo.builder.P") as mock_P:
                    mock_P.ascii_work_dir.return_value = tmp
                    path1 = builder.core_object_path("/usr/bin/gcc", False)
                    path2 = builder.core_object_path("/usr/bin/gcc", True)
                    path3 = builder.core_object_path("/usr/bin/g++", False)
                    assert path1 != path2  # Debug flag changes path
                    assert path1 != path3  # Compiler changes path

    def test_run_env_sets_protocol_fd(self):
        """run_env() sets PRABHA_PROTO_FD=1."""
        env = builder.run_env()
        assert env["PRABHA_PROTO_FD"] == "1"


# ---------------------------------------------------------------------------
# turbo/modernize.py tests
# ---------------------------------------------------------------------------

class TestModernize:
    def test_modernize_void_main(self):
        """modernize() converts void main to int main."""
        src = "void main() { printf(\"hi\"); }"
        res = modernize.modernize(src)
        assert "int main" in res.code
        assert "void main()" not in res.code
        assert len(res.changes) > 0
        assert any(c.rule == "void-main" for c in res.changes)

    def test_modernize_far_near_removal(self):
        """modernize() removes far/near/huge qualifiers."""
        src = "int far *ptr; char near *str;"
        res = modernize.modernize(src)
        assert "far" not in res.code
        assert "near" not in res.code
        assert any(c.rule == "far-near" for c in res.changes)

    def test_modernize_gets_to_fgets(self):
        """modernize() replaces gets() with fgets()."""
        src = textwrap.dedent("""
            #include <stdio.h>
            int main() {
                char buf[100];
                gets(buf);
                return 0;
            }
        """)
        res = modernize.modernize(src)
        assert "gets(buf)" not in res.code
        assert "fgets" in res.code
        assert any(c.rule == "gets" for c in res.changes)

    def test_modernize_old_headers(self):
        """modernize() converts iostream.h to iostream."""
        src = "#include <iostream.h>\nint main() { cout << \"hi\"; }"
        res = modernize.modernize(src, file_name="test.cpp")
        assert "<iostream>" in res.code
        assert "iostream.h" not in res.code
        assert any(c.rule == "old-headers" for c in res.changes)

    def test_modernize_std_qualify(self):
        """modernize() adds std:: to cout/cin/endl."""
        src = "#include <iostream>\nint main() { cout << \"hi\" << endl; }"
        res = modernize.modernize(src, file_name="test.cpp")
        assert "std::cout" in res.code
        assert "std::endl" in res.code
        assert any(c.rule == "std-qualify" for c in res.changes)

    def test_modernize_null_to_nullptr(self):
        """modernize() converts NULL to nullptr in C++."""
        src = "#include <iostream>\nint main() { int* p = NULL; }"
        res = modernize.modernize(src, file_name="test.cpp")
        assert "nullptr" in res.code
        assert "NULL" not in res.code
        assert any(c.rule == "null" for c in res.changes)

    def test_modernize_clrscr_review(self):
        """modernize() offers clrscr() removal as review (not applied by default)."""
        src = "int main() { clrscr(); return 0; }"
        res = modernize.modernize(src)
        # clrscr is a "review" rule, so it should be in available, not changes
        assert any(a["id"] == "clrscr" for a in res.available)
        assert not any(c.rule == "clrscr" for c in res.changes)

    def test_modernize_disabled_rules_not_applied(self):
        """modernize() respects enabled parameter."""
        src = "void main() { return; }"
        res = modernize.modernize(src, enabled=set())  # No rules enabled
        assert len(res.changes) == 0
        assert any(a["id"] == "void-main" for a in res.available)

    def test_modernize_detect_lang_cpp(self):
        """detect_lang() identifies C++ from file extension."""
        assert modernize.detect_lang("", file_name="test.cpp") == "cpp"
        assert modernize.detect_lang("", file_name="test.cc") == "cpp"
        assert modernize.detect_lang("", file_name="test.cxx") == "cpp"
        assert modernize.detect_lang("", file_name="test.hpp") == "cpp"

    def test_modernize_detect_lang_c(self):
        """detect_lang() identifies C from file extension or content."""
        assert modernize.detect_lang("", file_name="test.c") == "c"
        assert modernize.detect_lang("int main() { printf(\"hi\"); }") == "c"
        assert modernize.detect_lang("int main() { cout << \"hi\"; }") == "cpp"

    def test_balanced_brackets_check(self):
        """balanced() returns False for unbalanced brackets."""
        assert modernize.balanced("int main() { }") is True
        assert modernize.balanced("int main() { } }") is False
        assert modernize.balanced("int main() { ) }") is False

    def test_unified_diff_produces_diff(self):
        """unified_diff() produces a valid diff."""
        old = "int main() { return 0; }"
        new = "int main() { return 1; }"
        diff = modernize.unified_diff(old, new)
        assert "-int main() { return 0; }" in diff
        assert "+int main() { return 1; }" in diff