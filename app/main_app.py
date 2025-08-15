from PySide6.QtWidgets import QApplication
from pages.main_window import StartWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = StartWindow()
    window.show()
    app.exec()
    sys.exit(app.exec())