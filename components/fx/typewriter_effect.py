from PySide6.QtCore import QTimer, QObject, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox
)
import re

# TypewriterEffect: animates text display like a typewriter
class TypewriterEffect(QObject):
    """
    - by_word=True: type by word, False: type by character
    - Adds a short pause after punctuation (. , ! ? ; : …)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._label: QLabel | None = None
        self._tokens: list[str] = []
        self._i = 0
        self._base_interval = 35
        self._by_word = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        # Use list to accumulate tokens for efficient joining
        self._collected: list[str] = []

    # Tokenize text into words (with whitespace/newlines preserved) or characters
    def _tokenize(self, text: str) -> list[str]:
        if self._by_word:
            return re.findall(r'\S+|\s+', text)
        else:
            return list(text)

    # Compute common prefix length between two token lists
    def _common_prefix_len(self, a_tokens: list[str], b_tokens: list[str]) -> int:
        n = min(len(a_tokens), len(b_tokens))
        i = 0
        while i < n and a_tokens[i] == b_tokens[i]:
            i += 1
        return i

    # Start typewriter effect from scratch
    def start(self, label: QLabel, text: str, base_interval=35, by_word=False):
        self.stop()
        self._label = label
        self._base_interval = int(base_interval)
        self._by_word = by_word
        self._tokens = self._tokenize(text)
        self._i = 0
        self._collected.clear()
        self._timer.start(self._base_interval)
        self._tick()

    # Update existing text, continue typing from the new suffix
    def update(self, new_full_text: str):
        if not self._label:
            raise RuntimeError("Call start() before update().")
        new_tokens = self._tokenize(new_full_text)
        prev_full_tokens = self._collected + self._tokens
        n = min(len(prev_full_tokens), len(new_tokens))
        common_len = 0
        while common_len < n and prev_full_tokens[common_len] == new_tokens[common_len]:
            common_len += 1
        self._collected = new_tokens[:common_len]
        self._tokens = new_tokens[common_len:]
        self._i = 0
        if not self._tokens:
            self._label.setText("".join(self._collected))
            self._timer.stop()
            return
        if not self._timer.isActive():
            self._timer.start(self._base_interval)
        self._tick()

    # Stop animation and finalize text
    def stop(self):
        self._timer.stop()
        if self._label is not None:
            self._label.setText("".join(self._collected))

    # Timer tick: append one token and render
    def _tick(self):
        if not self._label:
            self.stop()
            return
        if self._i >= len(self._tokens):
            self.stop()
            return
        token = self._tokens[self._i]
        self._i += 1
        self._collected.append(token)
        current_text = "".join(self._collected)
        self._label.setText(current_text)
        # Adjust delay for punctuation
        last = token[-1] if token else ""
        if last in ".!?":
            delay = int(self._base_interval * 6)
        elif last in ",;:…":
            delay = int(self._base_interval * 3)
        else:
            delay = self._base_interval
        self._timer.start(max(1, delay))

# # Demo widget to test the typewriter effect
# class TypewriterEffectDemo(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("TypewriterEffect Demo")
#         self.setMinimumWidth(600)
#
#         self.typer = TypewriterEffect(self)
#
#         # Display label
#         self.label = QLabel("The typewriter effect will appear here.")
#         self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         self.label.setWordWrap(True)
#         self.label.setStyleSheet("font-size: 18px;")
#
#         # Input field (single line; replace with QTextEdit for multiline)
#         self.input = QLineEdit(
#             "Hello, this is a typewriter effect test. "
#             "It pauses briefly after commas and periods!"
#         )
#
#         # Interval control
#         self.interval = QSpinBox()
#         self.interval.setRange(5, 300)
#         self.interval.setValue(35)
#         self.interval.setSuffix(" ms")
#
#         # Buttons
#         self.btn_start_chars = QPushButton("Start (chars)")
#         self.btn_start_words = QPushButton("Start (words)")
#         self.btn_stop = QPushButton("Stop")
#
#         # Layout
#         top = QVBoxLayout(self)
#         ctrl1 = QHBoxLayout()
#         ctrl1.addWidget(QLabel("Text:"))
#         ctrl1.addWidget(self.input)
#
#         ctrl2 = QHBoxLayout()
#         ctrl2.addWidget(QLabel("Interval:"))
#         ctrl2.addWidget(self.interval)
#         ctrl2.addStretch()
#         ctrl2.addWidget(self.btn_start_chars)
#         ctrl2.addWidget(self.btn_start_words)
#         ctrl2.addWidget(self.btn_stop)
#
#         top.addLayout(ctrl1)
#         top.addLayout(ctrl2)
#         top.addWidget(self.label)
#
#         # Signals
#         self.btn_start_chars.clicked.connect(lambda: self.start_typing(False))
#         self.btn_start_words.clicked.connect(lambda: self.start_typing(True))
#         self.btn_stop.clicked.connect(self.typer.stop)
#
#     # Start typing effect with by_word flag
#     def start_typing(self, by_word: bool):
#         text = (
#             self.input.text()
#             if isinstance(self.input, QLineEdit)
#             else self.input.toPlainText()
#         )
#         self.typer.start(
#             label=self.label,
#             text=text,
#             base_interval=self.interval.value(),
#             by_word=by_word,
#         )

# # Entry point
# if __name__ == "__main__":
#     import sys
#     from PySide6.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     w = TypewriterEffectDemo()
#     w.show()
#     sys.exit(app.exec())
