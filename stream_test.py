from client.http_stream_worker import HttpStreamWorker
from PySide6.QtCore import QCoreApplication
import sys

def main():
    app = QCoreApplication(sys.argv)

    worker = HttpStreamWorker("This is a test prompt")

    worker.token_received.connect(lambda t: print(f"[Token] {t}"))
    worker.chunk_received.connect(lambda c: print(f"[Chunk] {c}"))
    worker.error_occurred.connect(lambda e: print(f"[Error] {e}"))
    worker.finished.connect(lambda: print("[Finished]"))

    worker.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
