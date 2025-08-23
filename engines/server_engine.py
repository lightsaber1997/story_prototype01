import requests
import json
from config.config_loader import load_config
from engines.base_engine import BaseEngine


class ServerEngine(BaseEngine):
    """Wrapper for custom HTTP server (sync + streaming)."""

    def __init__(self):
        config = load_config()
        server_cfg = config["llm"].get("server", {})
        self.server_url = server_cfg.get("url", "http://localhost:8080")
        self.endpoint = server_cfg.get("endpoint", "/generate")

    def generate_reply(self, messages, *, max_new_tokens: int = 128) -> str:
        """One-shot generation (non-streaming)."""
        payload = {
            "prompt": self._build_prompt(messages),
            "max_new_tokens": max_new_tokens,
            "stream": False,
        }
        try:
            resp = requests.post(f"{self.server_url}{self.endpoint}", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("text") or data.get("content") or data.get("token") or ""
        except requests.RequestException as e:
            return f"[ServerEngine network error] {str(e)}"
        except (ValueError, KeyError) as e:
            return f"[ServerEngine parse error] {str(e)}"
        except Exception as e:
            return f"[ServerEngine error] {str(e)}"

    def generate_reply_stream(self, messages, *, max_new_tokens: int = 128):
        """Streaming generation (yields tokens)."""
        payload = {
            "prompt": self._build_prompt(messages),
            "max_new_tokens": max_new_tokens,
            "stream": True,
        }
        try:
            with requests.post(
                f"{self.server_url}{self.endpoint}",
                json=payload,
                stream=True,
                timeout=(10, None),
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line or not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        token = data.get("token") or data.get("text") or data.get("content")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        # 로그성 메시지는 무시
                        continue
        except requests.RequestException as e:
            yield f"[ServerEngine network error] {str(e)}"
        except Exception as e:
            yield f"[ServerEngine streaming error] {str(e)}"

    @staticmethod
    def _build_prompt(messages) -> str:
        """Basic prompt builder: include roles for clarity."""
        return "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in messages if "content" in m)
