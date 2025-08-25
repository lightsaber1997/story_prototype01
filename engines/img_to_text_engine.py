# img_to_text_controller.py
import sys
from PySide6.QtCore import QObject, QThread, Signal, Slot


class ImgToTextWorker(QObject):
    """Worker that handles image → text conversion off-thread."""

    resultReady = Signal(dict)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    @Slot(str)
    def doWork(self, image_path: str):
        """Receive an image path, call engine, emit result."""
        print(f"[Worker] Got image_path={image_path}")

        try:
            # Call the high-level engine
            text_result = self.engine.image_to_text(image_path)
            self.resultReady.emit({"type": "img2text", "text": text_result})
        except Exception as e:
            self.resultReady.emit({"type": "error", "error": str(e)})


class ImgToTextController(QObject):
    """Controller: runs worker in a QThread."""

    operate = Signal(str)

    def __init__(self, engine, result_callback):
        super().__init__()
        self.workerThread = QThread()
        self.worker = ImgToTextWorker(engine)
        self.worker.moveToThread(self.workerThread)

        # Connect lifecycle
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        self.workerThread.start()
        self._closed = False

    def __del__(self):
        if self._closed:
            return
        self._closed = True

        if self.workerThread.isRunning():
            self.workerThread.quit()
            self.workerThread.wait(3000)  # timeout


# Dummy engine for now
class DummyImgToTextEngine:
    def image_to_text(self, image_path: str) -> str:
        # For now return dummy text
        return f"Once upon a time, dummy OCR text from {image_path}"

