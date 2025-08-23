# chat_gpt_engine.py
import os
import openai
from typing import List, Dict
from dotenv import load_dotenv
from engines.base_engine import BaseEngine


class ChatGPTEngine(BaseEngine):
    """ChatGPT API wrapper compatible with Phi3MiniEngine interface."""

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in .env")

        self.client = openai.OpenAI(api_key=self.api_key)

        # model & params
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("OPENAI_TOP_P", "1.0"))

        print(f"[ChatGPTEngine] initialized with {self.model_name}")

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert generic messages into OpenAI format."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            if role not in ("user", "assistant", "system"):
                role = "user"
            formatted.append({"role": role, "content": msg["content"]})
        return formatted

    def generate_reply(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128) -> str:
        """One-shot completion call."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._format_messages(messages),
                max_tokens=max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ChatGPTEngine error] {str(e)}"

    def generate_reply_stream(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128):
        """Streaming completion generator."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._format_messages(messages),
                max_tokens=max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                stream=True,
            )
            for chunk in response:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and getattr(delta, "content", None):
                    yield delta.content
        except Exception as e:
            yield f"[ChatGPTEngine error] {str(e)}"
