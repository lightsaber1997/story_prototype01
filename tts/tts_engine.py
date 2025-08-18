import pyttsx3
import platform
from tts.voice_type import VoiceType

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine

def tts_speak(text: str, voice: VoiceType, rate: int = 160):
    engine = get_engine()
    engine.setProperty("rate", rate)
    voice_id = voice.voice_id
        engine.setProperty("voice", voice_id)
    else:
        print(f"[WARN] Voice ID not set for {platform.system()} / {voice}")
    engine.say(text)
    engine.runAndWait()

# # Running Example
# speech("Hello, this is an American male voice.", VoiceType.AMERICAN_MAN)
# speech("Hello, this is an English female voice.", VoiceType.ENGLISH_WOMAN)
