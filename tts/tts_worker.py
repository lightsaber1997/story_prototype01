# tts/tts_worker.py
import sys
import pyttsx3
from PySide6.QtCore import QObject, Signal, Slot

class TTSWorker(QObject):
    started = Signal()     # 🔹 재생 시작 알림
    finished = Signal()
    error = Signal(str)

    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._engine = pyttsx3.init()
        return cls._engine
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self._stopped = True
        self._loop_active = False

    @Slot(str, object, int)
    def play(self, text: str, voice_id=None, rate: int = 160):
        try:
            self._stopped = False
            self.engine = self.get_engine()
            self.engine.setProperty("rate", rate)
            if voice_id:
                self.engine.setProperty("voice", voice_id)

            if not text.strip():
                self.finished.emit()
                return

            # 여기서 started 신호!
            self.started.emit()

            self.engine.say(text)

            if sys.platform == "darwin":
                self.engine.runAndWait()
            else:
                self.engine.startLoop(False)
                self._loop_active = True
                while not self._stopped and self.engine.isBusy():
                    self.engine.iterate()
                if self._loop_active:
                    self.engine.endLoop()
                    self._loop_active = False

            self.finished.emit()

        except Exception as e:
            try:
                if self._loop_active:
                    self.engine.endLoop()
                    self._loop_active = False
            except Exception:
                pass
            self.error.emit(str(e))

    @Slot()
    def stop(self):
        self._stopped = True
        if self.engine:
            try:
                self.engine.stop()
                if self._loop_active:
                    self.engine.endLoop()
                    self._loop_active = False
            except Exception:
                pass
        # 🔹 macOS에서는 stop() 눌러도 즉시 finish 이벤트 쏴주자
        if sys.platform == "darwin":
            self.finished.emit()