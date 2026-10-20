import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

class LspClient:
    def __init__(self, language: str, root: str):
        self.language = language.lower()
        self.root = os.path.abspath(root)
        self.proc = None
        self.req_id = 0
        self.open_files = set()

    def start(self) -> None:
        cmd = None
        local_bin = os.path.expanduser("~/.local/bin")
        if self.language in ["c", "cpp", "c++"]:
            clangd_path = shutil.which("clangd") or os.path.join(local_bin, "clangd")
            cmd = [clangd_path, "--background-index"]
        elif self.language in ["python", "py"]:
            pylsp_path = shutil.which("pylsp") or shutil.which("pylsp-server") or "pylsp"
            cmd = [pylsp_path]
        else:
            cmd = ["clangd"]

        env = dict(os.environ)
        env["PATH"] = f"{local_bin}:{env.get('PATH', '')}"

        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env
        )

        # Initialize LSP
        root_uri = Path(self.root).as_uri()
        init_params = {
            "processId": os.getpid(),
            "rootUri": root_uri,
            "rootPath": self.root,
            "capabilities": {
                "textDocument": {
                    "completion": {"completionItem": {"snippetSupport": True}},
                    "definition": {"dynamicRegistration": True}
                }
            }
        }
        self.send_request("initialize", init_params)
        self.read_response()
        self.send_notification("initialized", {})

    def _send_payload(self, payload: dict) -> None:
        if not self.proc or not self.proc.stdin:
            return
        data = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(data)}\r\n\r\n".encode("ascii")
        self.proc.stdin.write(header + data)
        self.proc.stdin.flush()

    def send_request(self, method: str, params: dict) -> int:
        self.req_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
            "params": params
        }
        self._send_payload(payload)
        return self.req_id

    def send_notification(self, method: str, params: dict) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self._send_payload(payload)

    def read_response(self, target_id: int = None, timeout: float = 5.0) -> dict:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.proc or self.proc.poll() is not None:
                break
            
            line = self.proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
                
            line_str = line.decode("ascii", errors="replace").strip()
            if line_str.startswith("Content-Length:"):
                content_len = int(line_str.split(":")[1].strip())
                # Read until empty line
                while True:
                    hdr = self.proc.stdout.readline().decode("ascii", errors="replace").strip()
                    if not hdr:
                        break
                
                content = self.proc.stdout.read(content_len)
                try:
                    msg = json.loads(content.decode("utf-8"))
                    if target_id is not None:
                        if msg.get("id") == target_id:
                            return msg
                    else:
                        if "id" in msg:
                            return msg
                except Exception:
                    pass
        return {}

    def ensure_file_open(self, file_path: str) -> None:
        abs_path = os.path.abspath(file_path)
        if abs_path not in self.open_files:
            file_uri = Path(abs_path).as_uri()
            text = ""
            if os.path.exists(abs_path):
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            lang_id = "cpp" if self.language in ["c", "cpp", "c++"] else "python"
            self.send_notification("textDocument/didOpen", {
                "textDocument": {
                    "uri": file_uri,
                    "languageId": lang_id,
                    "version": 1,
                    "text": text
                }
            })
            self.open_files.add(abs_path)

    def definition(self, file_path: str, line: int, col: int):
        self.ensure_file_open(file_path)
        abs_path = os.path.abspath(file_path)
        file_uri = Path(abs_path).as_uri()

        req_id = self.send_request("textDocument/definition", {
            "textDocument": {"uri": file_uri},
            "position": {"line": line - 1, "character": col - 1}
        })

        res = self.read_response(target_id=req_id, timeout=4.0)
        result = res.get("result")
        if not result:
            return None

        loc = result[0] if isinstance(result, list) else result
        target_uri = loc.get("uri") or loc.get("targetUri")
        target_range = loc.get("range") or loc.get("targetSelectionRange") or loc.get("targetRange")

        if not target_uri or not target_range:
            return None

        target_path = target_uri.replace("file://", "")
        start_line = target_range["start"]["line"] + 1
        start_col = target_range["start"]["character"] + 1

        return (target_path, start_line, start_col)

    def completions(self, file_path: str, line: int, col: int) -> list[str]:
        self.ensure_file_open(file_path)
        abs_path = os.path.abspath(file_path)
        file_uri = Path(abs_path).as_uri()

        req_id = self.send_request("textDocument/completion", {
            "textDocument": {"uri": file_uri},
            "position": {"line": line - 1, "character": col - 1}
        })

        res = self.read_response(target_id=req_id, timeout=4.0)
        result = res.get("result")
        if not result:
            return []

        items = result.get("items", result) if isinstance(result, dict) else result
        labels = []
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and "label" in item:
                    labels.append(item["label"])
                elif isinstance(item, str):
                    labels.append(item)
        return labels

    def shutdown(self) -> None:
        if self.proc:
            try:
                self.send_request("shutdown", {})
                self.send_notification("exit", {})
                time.sleep(0.1)
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None
