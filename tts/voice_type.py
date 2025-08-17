from enum import Enum
import platform

class VoiceType(Enum):
    AMERICAN_MAN   = {
        "label": "American Man",
        "Darwin":  "com.apple.speech.synthesis.voice.Alex",
        "Windows": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_David_11.0",
        "Linux":   "english-us"
    }
    AMERICAN_WOMAN = {
        "label": "American Woman",
        "Darwin":  "com.apple.speech.synthesis.voice.Samantha",
        "Windows": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_Zira_11.0",
        "Linux":   "english+f3"
    }
    ENGLISH_MAN    = {
        "label": "English Man",
        "Darwin":  "com.apple.voice.compact.en-GB.Daniel",
        "Windows": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_George_11.0",
        "Linux":   "english-uk"
    }
    ENGLISH_WOMAN  = {
        "label": "English Woman",
        "Darwin":  "com.apple.voice.compact.en-GB.Karen",
        "Windows": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_Hazel_11.0",
        "Linux":   "english+f2"
    }

    @property
    def label(self):
        return self.value["label"]

    @property
    def voice_id(self):
        os_name = platform.system()
        return self.value.get(os_name, None)
