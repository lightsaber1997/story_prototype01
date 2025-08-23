from config.config_loader import load_config
from engines.chat_gpt_engine import ChatGPTEngine
from engines.phi3_mini_engine import Phi3MiniEngine
from engines.server_engine import ServerEngine
from engines.chat_engine import ChatController
from typing import Optional, Callable

def get_engine():
    config = load_config()
    engine_type = config["llm"]["engine"].lower()
    if engine_type == "gpt":
        return ChatGPTEngine()
    elif engine_type == "phi3":
        return Phi3MiniEngine()
    elif engine_type == "server":
        return ServerEngine()
    else:
        raise ValueError(f"Unknown engine: {engine_type}")


def get_chat_controller(result_callback: Callable, token_callback: Optional[Callable] = None):
    """Public API: create ChatController with proper engine"""
    engine = get_engine()
    return ChatController(
        result_callback=result_callback,
        engine=engine,
        token_callback=token_callback
    )


def supports_streaming():
    """Check if current engine supports streaming"""
    config = load_config()
    if not config["llm"].get("streaming", {}).get("enabled", True):
        return False
    engine = get_engine()
    return hasattr(engine, "generate_reply_stream")


def is_streaming_enabled():
    """Check if streaming is enabled in config"""
    config = load_config()
    return config["llm"].get("streaming", {}).get("enabled", True)
