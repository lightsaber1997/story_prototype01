from config.config_loader import load_config
from engines.phi3_mini_engine import Phi3MiniEngine
from engines.chat_gpt_engine import ChatGPTEngine

def get_llm_engine():
    config = load_config()
    engine_type = config["llm"]["engine"]
    engine_type.lower() # lowercase

    if engine_type == "phi3":
        return Phi3MiniEngine()
    elif engine_type == "gpt":
        return ChatGPTEngine()
    else:
        raise ValueError(f"Unknown LLM engine type: {engine_type}")
