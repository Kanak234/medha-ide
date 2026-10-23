import os
import sys
import re
import json
import time
import socket
import shutil
import subprocess

class DebugSession:
    def __init__(self, target: str, kind: str = "gdb"):
        self.target = os.path.abspath(target)
        self.kind = kind.lower()
        self.proc = None
        self.sock = None
        self.stopped = False
        self.stopped_thread_id = 1
        self.frame_id = None
        self.req_seq = 0

    def start(self) -> None:
        if self.kind == "gdb":
            # toolchains.py: settings → bundled MinGW gdb (Windows) → PATH
            from medha import toolchains
            gdb_path = toolchains.find("gdb").path or shutil.which("gdb") or "gdb"
            cmd = [gdb_path, "--interpreter=mi2", self.target]
            self.proc = subprocess.Popen(
                cmd,
                creationflags=0x08000000 if os.name == "nt" else 0,   # no console flash on Windows
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
            self._read_gdb_until_prompt()
        elif self.kind == "debugpy":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', 0))
            self.port = s.getsockname()[1]
            s.close()

            # In a frozen (MSIX/PyInstaller) build sys.executable is MEDHA.exe, not
            # Python — use the detected Python interpreter instead.
            from medha import toolchains
            py = toolchains.find("python").path or sys.executable
            cmd = [py, "-m", "debugpy", "--listen", f"127.0.0.1:{self.port}", "--wait-for-client", self.target]
            self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            connected = False
            for _ in range(50):
                time.sleep(0.1)
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect(('127.0.0.1', self.port))
                    connected = True
                    break
                except Exception:
                    pass

            if connected:
                self.send_dap_request("initialize", {
                    "clientID": "medha",
                    "clientName": "MEDHA IDE",
                    "adapterID": "debugpy",
                    "linesStartAt1": True,
                    "columnsStartAt1": True,
                    "pathFormat": "path"
                })
                self.read_dap_response()
                self.send_dap_request("attach", {"justMyCode": False})
                self.read_dap_response()

    def _send_gdb_cmd(self, cmd: str) -> str:
        if not self.proc or not self.proc.stdin:
            return ""
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()
        return self._read_gdb_until_prompt()

    def _read_gdb_until_prompt(self, timeout: float = 5.0) -> str:
        lines = []
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.proc or self.proc.poll() is not None:
                break
            line = self.proc.stdout.readline()
            if not line:
                time.sleep(0.02)
                continue
            lines.append(line)
            if line.strip() == "(gdb)" or line.startswith("(gdb)"):
                break
        return "".join(lines)

    def send_dap_request(self, command: str, arguments: dict = None) -> int:
        self.req_seq += 1
        payload = {
            "seq": self.req_seq,
            "type": "request",
            "command": command
        }
        if arguments:
            payload["arguments"] = arguments
        data = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(data)}\r\n\r\n".encode("ascii")
        self.sock.sendall(header + data)
        return self.req_seq

    def read_dap_response(self, target_seq: int = None, timeout: float = 10.0) -> dict:
        start_time = time.time()
        buf = b""
        res_dict = {}
        while time.time() - start_time < timeout:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    time.sleep(0.05)
                    continue
                buf += chunk
                while b"Content-Length:" in buf:
                    header_part, rest = buf.split(b"\r\n\r\n", 1)
                    header_lines = header_part.decode("ascii").split("\r\n")
                    length = 0
                    for h in header_lines:
                        if h.startswith("Content-Length:"):
                            length = int(h.split(":")[1].strip())
                    if len(rest) >= length:
                        body = rest[:length]
                        buf = rest[length:]
                        msg = json.loads(body.decode("utf-8"))
                        if msg.get("event") == "stopped":
                            self.stopped = True
                            self.stopped_thread_id = msg.get("body", {}).get("threadId", 1)
                        if target_seq is not None and msg.get("request_seq") == target_seq:
                            res_dict = msg
                            return res_dict
                        elif target_seq is None and msg.get("type") in ["response", "event"]:
                            return msg
                    else:
                        break
            except Exception:
                break
        return res_dict

    def set_breakpoint(self, file_path: str, line: int) -> bool:
        if self.kind == "gdb":
            abs_file = os.path.abspath(file_path)
            res = self._send_gdb_cmd(f"-break-insert {abs_file}:{line}")
            return "^done" in res or "bkpt=" in res
        elif self.kind == "debugpy":
            abs_file = os.path.abspath(file_path)
            seq = self.send_dap_request("setBreakpoints", {
                "source": {"path": abs_file},
                "breakpoints": [{"line": line}]
            })
            res = self.read_dap_response(target_seq=seq)
            bps = res.get("body", {}).get("breakpoints", [])
            return bool(bps and bps[0].get("verified", True))
        return False

    def run(self) -> None:
        if self.kind == "gdb":
            self.proc.stdin.write("-exec-run\n")
            self.proc.stdin.flush()
        elif self.kind == "debugpy":
            self.send_dap_request("configurationDone")

    def wait_for_stop(self, timeout: float = 30.0) -> bool:
        if self.kind == "gdb":
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not self.proc or self.proc.poll() is not None:
                    break
                line = self.proc.stdout.readline()
                if not line:
                    time.sleep(0.05)
                    continue
                if line.startswith("*stopped"):
                    self.stopped = True
                    self._read_gdb_until_prompt(timeout=1.0)
                    return True
            return self.stopped
        elif self.kind == "debugpy":
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.stopped:
                    # Fetch stack trace to get frameId for variable evaluation
                    seq = self.send_dap_request("stackTrace", {"threadId": self.stopped_thread_id})
                    res = self.read_dap_response(target_seq=seq, timeout=3.0)
                    frames = res.get("body", {}).get("stackFrames", [])
                    if frames:
                        self.frame_id = frames[0]["id"]
                    return True
                self.read_dap_response(timeout=1.0)
            return self.stopped
        return False

    def evaluate(self, expr: str) -> str:
        if self.kind == "gdb":
            res = self._send_gdb_cmd(f"-data-evaluate-expression {expr}")
            m = re.search(r'value="([^"]+)"', res)
            if m:
                return m.group(1)
            return res
        elif self.kind == "debugpy":
            args = {"expression": expr, "context": "watch"}
            if self.frame_id is not None:
                args["frameId"] = self.frame_id
            seq = self.send_dap_request("evaluate", args)
            res = self.read_dap_response(target_seq=seq, timeout=5.0)
            return str(res.get("body", {}).get("result", ""))
        return ""

    def continue_(self) -> None:
        if self.kind == "gdb":
            self._send_gdb_cmd("-exec-continue")
        elif self.kind == "debugpy":
            self.send_dap_request("continue", {"threadId": self.stopped_thread_id})

    def terminate(self) -> None:
        if self.kind == "gdb" and self.proc:
            try:
                self.proc.stdin.write("-gdb-exit\n")
                self.proc.stdin.flush()
                self.proc.terminate()
            except Exception:
                pass
        elif self.kind == "debugpy":
            if self.sock:
                try:
                    self.send_dap_request("disconnect")
                    self.sock.close()
                except Exception:
                    pass
            if self.proc:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
        self.proc = None
