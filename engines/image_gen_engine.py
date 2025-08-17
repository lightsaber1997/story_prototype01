# ── stdlib
import sys, re, json, textwrap, random, string, collections
from pathlib import Path
from typing import Dict, List

# ── Qt
from PySide6.QtCore import Qt, QThread, QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget,
    QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
)

import format_helper



# ════════════════════════════════════════════════════════════════════
# ImageGenWorker (runs in background thread)
# ════════════════════════════════════════════════════════════════════
class ImageGenWorker(QObject):
    """Handles image generation in a background thread."""

    resultReady = Signal(dict)  # keys: type, image (PIL.Image), prompt (str)

    def __init__(self, engine):  # engine: StableV15Engine
        super().__init__()
        self.engine = engine

    @Slot(str)
    def doWork(self, prompt: str):
        try:
            image = self.engine.generate_image(prompt)
            self.resultReady.emit({
                "type": "image_generated",
                "image": image,
                "prompt": prompt
            })
        except Exception as e:
            print(f"[ImageGenWorker] Error generating image: {e}")
            self.resultReady.emit({
                "type": "error",
                "error": str(e)
            })


# ════════════════════════════════════════════════════════════════════
# ImageGenController (thread wrapper)
# ════════════════════════════════════════════════════════════════════
class ImageGenController(QObject):
    operate = Signal(str)  # accepts the prompt string

    def __init__(self, result_callback, engine):  # engine: StableV15Engine
        super().__init__()
        self.workerThread = QThread()
        self.worker = ImageGenWorker(engine)
        self.worker.moveToThread(self.workerThread)

        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        self.workerThread.start()

    def __del__(self):
        self.workerThread.quit()
        self.workerThread.wait()
