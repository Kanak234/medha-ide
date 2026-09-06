import json
import urllib.request
import urllib.error

class AiAssistant:
    def __init__(self, model: str = "qwen2.5-coder:3b", host: str = "http://127.0.0.1:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def available(self) -> bool:
        try:
            url = f"{self.host}/api/tags"
            req = urllib.request.Request(url, headers={"User-Agent": "MEDHA-IDE"})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    available_models = [m.get("name") for m in data.get("models", [])]
                    if not available_models:
                        return False
                    # If specific model requested, check if present or fallback to first available
                    if self.model not in available_models:
                        # Auto select first available model if requested is missing
                        self.model = available_models[0]
                    return True
        except Exception:
            return False
        return False

    def models(self) -> list[str]:
        try:
            url = f"{self.host}/api/tags"
            req = urllib.request.Request(url, headers={"User-Agent": "MEDHA-IDE"})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def complete(self, prompt: str, context: str = "", timeout: float = 120.0) -> str:
        if not self.available():
            return "Ollama local service is unavailable or specified model is missing."

        full_prompt = prompt
        if context:
            full_prompt = f"Context Code:\n```\n{context}\n```\n\nTask:\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            url = f"{self.host}/api/generate"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "MEDHA-IDE"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    res = json.loads(response.read().decode("utf-8"))
                    return res.get("response", "")
        except Exception as e:
            return f"AI completion request failed: {e}"
        return ""

    def complete_stream(self, prompt: str, context: str = ""):
        if not self.available():
            yield "Ollama local service is unavailable."
            return

        full_prompt = prompt
        if context:
            full_prompt = f"Context Code:\n```\n{context}\n```\n\nTask:\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True
        }

        try:
            url = f"{self.host}/api/generate"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "MEDHA-IDE"}
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                for line in response:
                    if line:
                        msg = json.loads(line.decode("utf-8"))
                        chunk = msg.get("response", "")
                        if chunk:
                            yield chunk
        except Exception as e:
            yield f"\n[AI Error: {e}]"
