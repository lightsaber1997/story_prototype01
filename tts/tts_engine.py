import pyttsx3
import platform
from PySide6.QtCore import QThread, Signal
from tts.voice_type import VoiceType

class TTSWorker(QThread):
    """Asynchronous TTS runner based on QThread"""
    finished = Signal()
    error = Signal(str)

    _engine = None  # Shared class-level engine (singleton)

    @classmethod
    def _get_engine(cls):
        """Return the shared pyttsx3 engine instance"""
        if cls._engine is None:
            cls._engine = pyttsx3.init()
        return cls._engine

    def __init__(self, text: str, mode: VoiceType, rate: int = 160):
        super().__init__()
        self.text = text
        self.mode = mode
        self.rate = rate

    def run(self):
        try:
            engine = self._get_engine()
            engine.setProperty("rate", self.rate)

            voice_id = self.mode.voice_id
            if voice_id:
                engine.setProperty("voice", voice_id)
            else:
                print(f"[WARN] Voice ID not set for {platform.system()} / {self.mode}")

            engine.say(self.text)
            engine.runAndWait()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
