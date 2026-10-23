"""
MEDHĀ IDE — turbo/protocol.py
=============================

WHAT:  Decoder for the PRABHA runtime's output stream. A Turbo C program writes
       two kinds of lines to stdout:
         * normal text from printf/cout  → goes to MEDHĀ's terminal
         * `##PRABHA##{json}` lines      → screen updates for the graphics panel
       Messages: init (w,h), palette (16 RGB), frame (x,y,w,h + RLE/base64 pixels),
       input (program waits for getch), sound (hz), bye/close.
WHY:   Pure Python with no Qt import, so it is unit-testable and the same code
       works on Windows (no fd 3 there — everything comes through stdout).
       Mirrors tests/decode.py in PRABHA, the reference decoder.
USED BY: runner.py feeds raw stdout bytes in; panel.py reads `framebuffer`/`palette`.
FLOW:  feed(bytes) → (text_for_terminal, [messages]) ; framebuffer updated in place.
"""

import base64
import json

MARK = b"##PRABHA##"

# Turbo C's 16 default colours (CGA/EGA palette) — used until the program sends one.
DEFAULT_RGB = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170), (170, 0, 0), (170, 0, 170),
    (170, 85, 0), (170, 170, 170), (85, 85, 85), (85, 85, 255), (85, 255, 85),
    (85, 255, 255), (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
]


class ProtocolDecoder:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.framebuffer = bytearray(self.width * self.height)   # one byte = colour index 0..15
        self.palette = list(DEFAULT_RGB)
        self.frames = 0            # number of frame messages applied
        self.inited = False        # True after the runtime sent "init"
        self._pending = b""        # bytes after the last newline (incomplete line)

    def feed(self, data: bytes):
        """Split a chunk of stdout into terminal text and protocol messages.

        A marker can appear in the MIDDLE of a line: `printf("Choice: "); getch();`
        prints text without a newline, then the runtime writes its `input` message
        right after it. So we look for the marker anywhere: text before it goes to
        the terminal, the JSON after it up to the newline is a message.
        Text without a newline (e.g. `printf("Enter a: ")` before scanf) must appear
        at once, so a partial tail is released unless it may be a marker's start.
        """
        buf = self._pending + data
        self._pending = b""
        text_parts, messages = [], []
        pos = 0
        while pos < len(buf):
            mk = buf.find(MARK, pos)
            if mk < 0:
                break
            nl = buf.find(b"\n", mk)
            if nl < 0:
                text_parts.append(buf[pos:mk])
                self._pending = buf[mk:]       # message not complete yet — wait for more
                pos = len(buf)
                break
            text_parts.append(buf[pos:mk])
            msg = self._parse(buf[mk + len(MARK):nl].strip())
            if msg is not None:
                messages.append(msg)
            pos = nl + 1
        rest = buf[pos:]
        if rest:
            # hold back only the bytes that could be the beginning of "##PRABHA##"
            hold = 0
            for k in range(min(len(MARK) - 1, len(rest)), 0, -1):
                if MARK.startswith(rest[-k:]):
                    hold = k
                    break
            text_parts.append(rest[:len(rest) - hold])
            if hold:
                self._pending = rest[len(rest) - hold:]
        text = b"".join(text_parts).decode("utf-8", errors="replace")
        return text, messages

    def flush_text(self) -> str:
        """Process ended — release anything still buffered as plain text."""
        rest, self._pending = self._pending, b""
        if rest.startswith(MARK):
            msg = self._parse(rest[len(MARK):].strip())
            return "" if msg is not None else rest.decode("utf-8", errors="replace")
        return rest.decode("utf-8", errors="replace")

    # ------------------------------------------------------------------ parse
    def _parse(self, raw: bytes):
        try:
            msg = json.loads(raw.decode("utf-8", errors="replace"))
        except ValueError:
            return None
        t = msg.get("t")
        if t == "init":
            self.width, self.height = int(msg.get("w", 640)), int(msg.get("h", 480))
            self.framebuffer = bytearray(self.width * self.height)
            self.inited = True
        elif t == "palette":
            rgb = msg.get("rgb") or []
            if len(rgb) == 16:
                self.palette = [tuple(int(v) for v in c[:3]) for c in rgb]
        elif t == "frame":
            self._apply_frame(msg)
        return msg

    def _apply_frame(self, msg):
        """RLE = (count, colour) byte pairs, base64 encoded; covers rectangle x,y,w,h."""
        raw = base64.b64decode(msg.get("rle", ""))
        x, y, w, h = int(msg["x"]), int(msg["y"]), int(msg["w"]), int(msg["h"])
        pix = bytearray()
        for i in range(0, len(raw) - 1, 2):
            pix += bytes([raw[i + 1]]) * raw[i]
        if len(pix) != w * h:
            return   # corrupt frame: ignore instead of drawing garbage
        W = self.width
        for r in range(h):
            row = (y + r) * W + x
            self.framebuffer[row:row + w] = pix[r * w:(r + 1) * w]
        self.inited = True
        self.frames += 1

    # ------------------------------------------------------------ helpers
    def pixel(self, x, y) -> int:
        """Colour index at (x, y) — used by tests to check real drawing."""
        return self.framebuffer[y * self.width + x]

    def rgb_bytes(self) -> bytes:
        """Framebuffer as packed RGB888 (for QImage / PNG export)."""
        lut = [bytes(c) for c in self.palette]
        return b"".join(lut[v & 15] for v in self.framebuffer)

    def colour_histogram(self):
        counts = [0] * 16
        for v in self.framebuffer:
            counts[v & 15] += 1
        return counts
