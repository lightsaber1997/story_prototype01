# tts/tts_controller.py
from PySide6.QtCore import QObject, QThread, Signal
from tts.tts_worker import TTSWorker

class TTSController(QObject):
    playRequested = Signal(str, object, int)
    stopRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread(parent)
        self.worker = TTSWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()

        self.playRequested.connect(self.worker.play)
        self.stopRequested.connect(self.worker.stop)

        # 상태 플래그
        self._running = False

        # 워커 이벤트 연결
        self.worker.started.connect(self._on_started)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)

    def start(self, text, mode, rate):
        if self.is_running():
            return
        voice_id = getattr(mode, "voice_id", None)
        self.playRequested.emit(text, voice_id, int(rate))

    def stop(self):
        self.stopRequested.emit()

    def is_running(self) -> bool:
        return self._running

    # 내부 상태 업데이트
    def _on_started(self):
        self._running = True

    def _on_finished(self):
        self._running = False

    def _on_error(self, msg: str):
        self._running = False
        print("[TTS] error:", msg)
