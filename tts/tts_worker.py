# tts/tts_worker.py
import time
import wave
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot
from piper import PiperVoice
from config.config_loader import load_config
import os
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl



class TTSWorker(QObject):
    # Signals for status updates
    started = Signal()
    finished = Signal()
    error = Signal(str)
    synthesized = Signal(str)

    def __init__(self, root_path):
        super().__init__()

        self.config = load_config()
        self._voice = None
        model_path = os.path.join(root_path, self.config["tts"]["option"]["voice_path"])
        self._voice = PiperVoice.load(model_path)
        self._root_path = root_path
        
    
        self._stop_requested = False

    @Slot(str, object, int)
    def play(self, text: str, voice_id: str | None, rate: int):
        """Generate TTS audio from text and save to file"""
        try:
            self.started.emit()
            self._stop_requested = False

            # Load Piper voice model (you can make this configurable)
            # If `voice_id` is provided by the controller, map it to a model file
            
            print(f"[DEBUG] tts text {text}")
            

            # Always overwrite to a fixed file or make dynamic filenames
            out_file = os.path.join(self._root_path, "data/output.wav")
            os.makedirs(os.path.dirname(out_file), exist_ok=True)

            start = time.time()
            with wave.open(out_file, "wb") as wav_file:
                self._voice.synthesize_wav(text, wav_file)

            end = time.time()
            print(f"[TTS] Synthesis took {end - start:.2f} seconds -> {out_file}")

            self.synthesized.emit(out_file)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    @Slot()
    def stop(self):
        """Request stop (currently only cooperative)"""
        self._stop_requested = True
        # Piper doesn’t support mid-synthesis stopping easily,
        # but you can check this flag in a streaming setup.
