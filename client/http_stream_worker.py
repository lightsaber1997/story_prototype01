import json
from PySide6.QtCore import QThread, Signal
from typing import List, Dict
from engines.base_engine import BaseEngine


class HttpStreamWorker(QThread):
    token_received = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, engine: BaseEngine, messages: List[Dict[str, str]]):
        super().__init__()
        self.engine = engine
        self.messages = messages
        self.should_stop = False

    def stop(self):
        self.should_stop = True

    def run(self):
        try:
            for token in self.engine.generate_reply_stream(self.messages, max_new_tokens=200):
                if self.should_stop:
                    break
                self.token_received.emit(token)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()
