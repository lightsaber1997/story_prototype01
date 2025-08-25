from typing import List, Dict, Generator


class BaseEngine:
    def generate_reply(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128) -> str:
        raise NotImplementedError

    def generate_reply_stream(self, messages: List[Dict[str, str]], *, max_new_tokens: int = 128) -> Generator[
        str, None, None]:
        raise NotImplementedError
