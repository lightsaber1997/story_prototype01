from app.core.config_loader import load_config
from phi3_mini_engine import Phi3MiniEngine
from chat_gpt_engine import ChatGPTEngine

def get_llm_engine():
    config = load_config()
    engine_type = config["llm"]["engine"]

    if engine_type == "phi3":
        return Phi3MiniEngine()
    elif engine_type == "gpt":
        return ChatGPTEngine()
    else:
        raise ValueError(f"Unknown LLM engine type: {engine_type}")
