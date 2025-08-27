# tts/tts_controller.py
from PySide6.QtCore import QObject, QThread, Signal
from tts.tts_worker import TTSWorker

class TTSController(QObject):
    # Signals for controlling playback
    playRequested = Signal(str, object, int)
    stopRequested = Signal()

    def __init__(self, root_path):
        super().__init__()
        # Create a dedicated worker thread
        self.thread = QThread()
        self.worker = TTSWorker(root_path)
        self.worker.moveToThread(self.thread)
        self.thread.start()

        # Connect controller signals to worker slots
        self.playRequested.connect(self.worker.play)
        self.stopRequested.connect(self.worker.stop)

        # Running state flag
        self._running = False

        # Connect worker signals to controller handlers
        self.worker.started.connect(self._on_started)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)

    def start(self, text, mode, rate):
        """Start TTS playback if not already running"""
        if self.is_running():
            return
        voice_id = getattr(mode, "voice_id", None)
        self.playRequested.emit(text, voice_id, int(rate))

    def stop(self):
        """Stop TTS playback"""
        self.stopRequested.emit()

    def is_running(self) -> bool:
        """Check if TTS is currently running"""
        return self._running

    def _on_started(self):
        """Set running flag when worker starts"""
        self._running = True

    def _on_finished(self):
        """Clear running flag when worker finishes"""
        self._running = False

    def _on_error(self, msg: str):
        """Handle worker error and reset running state"""
        self._running = False
        print("[TTS] error:", msg)
