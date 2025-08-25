import json
import textwrap
import requests
from typing import Dict, List, Generator, Any
from config.config_loader import load_config
from engines.base_engine import BaseEngine


class ServerEngine(BaseEngine):
    """Wrapper for custom HTTP server (sync + streaming) sending sys_prompt/user_prompt."""

    def __init__(self):
        config = load_config()
        server_cfg = config["llm"].get("server", {})
        self.server_url = server_cfg.get("url", "http://localhost:8080")
        self.endpoint_sync = server_cfg.get("endpoint_sync", "/chat")
        self.endpoint_stream = server_cfg.get("endpoint_stream", "/chat_stream")
        self.timeout = float(server_cfg.get("timeout_sec", 300))
        self.default_temperature = float(server_cfg.get("temperature", 0.7))
        self.default_top_p = float(server_cfg.get("top_p", 1.0))

        self.headers = {
            "Content-Type": "application/json",
        }

    # -----------------------
    # Helpers
    # -----------------------
    @staticmethod
    def _normalize_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        out = []
        for m in messages:
            role = m.get("role", "user")
            if role not in ("user", "assistant", "system"):
                role = "user"
            out.append({"role": role, "content": m.get("content", "")})
        return out

    @staticmethod
    def _split_sys_user(messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        messages에서 sys_prompt / user_prompt 추출 규칙:
        - sys_prompt: 모든 system 메시지를 순서대로 합침(빈 줄로 구분)
        - user_prompt: 가장 마지막 user 메시지의 content
        - (참고) 필요하면 이전 대화 문맥을 서버가 지원하는 별도 필드로 넘길 수 있지만,
                 요구사항은 sys/user 두 필드이므로 여기서는 생략.
        """
        sys_parts: List[str] = []
        last_user: str = ""

        for m in messages:
            r = m.get("role", "user").lower()
            c = textwrap.dedent(m.get("content", "")).strip("\n")
            if r == "system":
                if c:
                    sys_parts.append(c)
            elif r == "user":
                # 마지막 user를 추적
                if c:
                    last_user = c

        sys_prompt = "\n\n".join(sys_parts).strip()
        user_prompt = last_user.strip()
        return {"sys_prompt": sys_prompt, "user_prompt": user_prompt}

    @staticmethod
    def _first_nonempty(*candidates: Any) -> str:
        for c in candidates:
            if isinstance(c, str) and c.strip():
                return c.strip()
        return ""

    @staticmethod
    def _extract_sync_text(payload: Dict[str, Any]) -> str:
        # 서버가 동기 응답을 text/answer/content/completion 형태로 줄 수 있음
        text = ServerEngine._first_nonempty(
            payload.get("answer"),
            payload.get("text"),
            payload.get("content"),
            payload.get("completion"),
        )
        if text:
            return text

        # OpenAI 호환
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            ch0 = choices[0]
            msg = (ch0.get("message") or {})
            text = ServerEngine._first_nonempty(
                msg.get("content"),
                ch0.get("text"),
            )
            if text:
                return text

        # 마지막 fallback: 원본 JSON 문자열
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _iter_stream_lines(resp: requests.Response) -> Generator[str, None, None]:
        # SSE / JSONL / raw 모두 수용
        for raw_line in resp.iter_lines(decode_unicode=True, delimiter=b"\n"):
            if raw_line is None:
                continue
            line = (raw_line or "").strip()
            if not line:
                continue
            if line.startswith("data:"):
                yield line[5:].strip()
            else:
                yield line

    @staticmethod
    def _extract_delta(line: str) -> str:
        # JSON 라인이면 delta/content/text/choices[].delta.content/choices[].text 우선 추출
        if line.startswith("{") or line.startswith("["):
            try:
                obj = json.loads(line)
            except Exception:
                return line

            for key in ("delta", "content", "text"):
                v = obj.get(key)
                if isinstance(v, str) and v:
                    return v

            choices = obj.get("choices")
            if isinstance(choices, list) and choices:
                ch0 = choices[0]
                delta = ch0.get("delta") or {}
                if isinstance(delta, dict):
                    v = delta.get("content")
                    if isinstance(v, str) and v:
                        return v
                v = ch0.get("text")
                if isinstance(v, str) and v:
                    return v

            v = obj.get("completion")
            if isinstance(v, str) and v:
                return v

            return ""
        else:
            # RAW 텍스트
            return line

    def _compose_payload(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int,
        stream: bool,
    ) -> Dict[str, Any]:
        norm = self._normalize_messages(messages)
        split = self._split_sys_user(norm)

        # 서버 요구: sys_prompt / user_prompt를 최상위에 넣어 전송
        payload: Dict[str, Any] = {
            "sys_prompt": split["sys_prompt"],
            "user_prompt": split["user_prompt"],
            "max_new_tokens": max_new_tokens,
            "temperature": self.default_temperature,
            "top_p": self.default_top_p,
            "stream": stream,
        }

        # (선택) 서버가 과거 assistant/user 히스토리를 따로 받는 스펙이라면 여기에 추가:
        # payload["history"] = [
        #     m for m in norm if m["role"] in ("assistant", "user")
        # ]

        return payload

    # -----------------------
    # Public API
    # -----------------------
    def generate_reply(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128) -> str:
        url = f"{self.server_url.rstrip('/')}/{self.endpoint_sync.lstrip('/')}"
        payload = self._compose_payload(messages, max_new_tokens, stream=False)
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
            r.raise_for_status()
            ctype = r.headers.get("Content-Type", "")
            data = r.json() if ctype.startswith("application/json") else {"text": r.text}
            return self._extract_sync_text(data)
        except Exception as e:
            return f"[ServerEngine error] {str(e)}"

    def generate_reply_stream(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128):
        url = f"{self.server_url.rstrip('/')}/{self.endpoint_stream.lstrip('/')}"
        payload = self._compose_payload(messages, max_new_tokens, stream=True)
        print(f"payload={payload}")
        try:
            with requests.post(url, headers=self.headers, json=payload, timeout=self.timeout, stream=True) as resp:
                resp.raise_for_status()
                for line in self._iter_stream_lines(resp):
                    delta = self._extract_delta(line)
                    if delta:
                        yield delta
        except Exception as e:
            yield f"[ServerEngine error] {str(e)}"
