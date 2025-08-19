# tts/tts_worker.py
import sys
import pyttsx3
from PySide6.QtCore import QObject, Signal, Slot

class TTSWorker(QObject):
    # Signals for playback events
    started = Signal()     # Emitted when playback starts
    finished = Signal()    # Emitted when playback finishes
    error = Signal(str)    # Emitted when an error occurs

    _engine = None

    @classmethod
    def get_engine(cls):
        """Return a singleton pyttsx3 engine instance"""
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
        """Play text-to-speech with given parameters"""
        try:
            self._stopped = False
            self.engine = self.get_engine()
            self.engine.setProperty("rate", rate)
            if voice_id:
                self.engine.setProperty("voice", voice_id)

            if not text.strip():
                self.finished.emit()
                return

            # Emit started signal when playback begins
            self.started.emit()

            self.engine.say(text)

            if sys.platform == "darwin":
                # On macOS use runAndWait (blocking)
                self.engine.runAndWait()
            else:
                # On Windows/Linux manage loop manually
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
        """Stop playback immediately if active"""
        self._stopped = True
        if self.engine:
            try:
                self.engine.stop()
                if self._loop_active:
                    self.engine.endLoop()
                    self._loop_active = False
            except Exception:
                pass
# tts/tts_worker.py
import sys
import pyttsx3
from PySide6.QtCore import QObject, Signal, Slot

class TTSWorker(QObject):
    # Signals for playback events
    started = Signal()     # Emitted when playback starts
    finished = Signal()    # Emitted when playback finishes
    error = Signal(str)    # Emitted when an error occurs

    _engine = None

    @classmethod
    def get_engine(cls):
        """Return a singleton pyttsx3 engine instance"""
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
        """Play text-to-speech with given parameters"""
        try:
            self._stopped = False
            self.engine = self.get_engine()
            self.engine.setProperty("rate", rate)
            if voice_id:
                self.engine.setProperty("voice", voice_id)

            if not text.strip():
                self.finished.emit()
                return

            # Emit started signal when playback begins
            self.started.emit()

            self.engine.say(text)

            if sys.platform == "darwin":
                # On macOS use runAndWait (blocking)
                self.engine.runAndWait()
            else:
                # On Windows/Linux manage loop manually
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
        """Stop playback immediately if active"""
        self._stopped = True
        if self.engine:
            try:
                self.engine.stop()
                if self._loop_active:
                    self.engine.endLoop()
                    self._loop_active = False
            except Exception:
                pass
