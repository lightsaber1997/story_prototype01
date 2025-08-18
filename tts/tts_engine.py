import pyttsx3
import platform
from PySide6.QtCore import QThread, Signal
from tts.voice_type import VoiceType

class TTSWorker(QThread):
    """QThread 기반 비동기 TTS 실행기"""
    finished = Signal()
    error = Signal(str)

    _engine = None  # 클래스 레벨 공유 엔진 (싱글톤)

    @classmethod
    def _get_engine(cls):
        """공용 pyttsx3 엔진 반환"""
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
