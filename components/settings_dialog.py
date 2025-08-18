from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSpinBox, QComboBox,
    QPushButton, QHBoxLayout, QCheckBox, QLineEdit, QSlider, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt

from components.fx.typewriter_effect import TypewriterEffect
from tts.voice_type import VoiceType

class SettingsDialog(QDialog):
    def __init__(self, parent=None,
                 current_rate=200, current_mode=VoiceType.AMERICAN_WOMAN,
                 current_animated=True, current_interval=30, current_by_word=False):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(260)
        layout = QVBoxLayout(self)

        # --- TTS Section ---
        # TTS Rate (SpinBox ↔ Slider)
        layout.addWidget(QLabel("TTS Rate:"))
        tts_layout = QHBoxLayout()
        self.rateSpin = QSpinBox()
        self.rateSpin.setRange(50, 400)
        self.rateSpin.setValue(current_rate)
        self.rateSlider = QSlider(Qt.Horizontal)
        self.rateSlider.setRange(50, 400)
        self.rateSlider.setValue(current_rate)
        # SpinBox ↔ Slider connect
        self.rateSpin.valueChanged.connect(self.rateSlider.setValue)
        self.rateSlider.valueChanged.connect(self.rateSpin.setValue)
        tts_layout.addWidget(self.rateSpin)
        tts_layout.addWidget(self.rateSlider)
        layout.addLayout(tts_layout)

        # TTS Mode
        layout.addWidget(QLabel("TTS Mode:"))
        self.modeBox = QComboBox()
        self.modeBox.addItems([v.label for v in VoiceType])
        self.modeBox.setCurrentText(current_mode.label)
        layout.addWidget(self.modeBox)

        # --- Typewriter Section ---
        # Typewriter Animated (enable / disable)
        layout.addWidget(QLabel("Typewriter Animated:"))
        self.animatedBox = QCheckBox("Enable animation")
        self.animatedBox.setChecked(current_animated)
        layout.addWidget(self.animatedBox)

        # Typing Interval (SpinBox + Slider)
        layout.addWidget(QLabel("Typing Interval (ms):"))
        speed_layout = QHBoxLayout()
        self.intervalSpin = QSpinBox()
        self.intervalSpin.setRange(10, 200)
        self.intervalSpin.setValue(current_interval)
        self.intervalSlider = QSlider(Qt.Horizontal)
        self.intervalSlider.setRange(10, 200)
        self.intervalSlider.setValue(current_interval)
        # connect
        self.intervalSpin.valueChanged.connect(self.intervalSlider.setValue)
        self.intervalSlider.valueChanged.connect(self.intervalSpin.setValue)
        speed_layout.addWidget(self.intervalSpin)
        speed_layout.addWidget(self.intervalSlider)
        layout.addLayout(speed_layout)

        # Type by Character / Word (Radio Buttons)
        layout.addWidget(QLabel("Typing Unit:"))
        radio_layout = QHBoxLayout()
        self.charRadio = QRadioButton("Character")
        self.wordRadio = QRadioButton("Word")
        if current_by_word:
            self.wordRadio.setChecked(True)
        else:
            self.charRadio.setChecked(True)
        self.unitGroup = QButtonGroup(self)
        self.unitGroup.addButton(self.charRadio)
        self.unitGroup.addButton(self.wordRadio)
        radio_layout.addWidget(self.charRadio)
        radio_layout.addWidget(self.wordRadio)
        radio_layout.addStretch()
        layout.addLayout(radio_layout)

        # --- Typewriter Demo Preview ---
        # Typewriter Demo
        layout.addWidget(QLabel("Typewriter Demo:"))
        self.demoInput = QLineEdit("Hello, this is a typewriter demo.")
        self.demoInput.setMaxLength(80)
        layout.addWidget(self.demoInput)

        # Start / Stop buttons
        demoBtns = QHBoxLayout()
        self.btnDemoStart = QPushButton("Start")
        self.btnDemoStop = QPushButton("Stop")
        demoBtns.addWidget(self.btnDemoStart)
        demoBtns.addWidget(self.btnDemoStop)
        layout.addLayout(demoBtns)

        self.demoLabel = QLabel("Demo result will appear here.")
        self.demoLabel.setWordWrap(True)
        self.demoLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.demoLabel.setStyleSheet(
            "font-size: 16px; border: 1px solid gray; padding: 4px;"
        )
        self.demoLabel.setFixedHeight(100)
        layout.addWidget(self.demoLabel)

        # --- OK / Cancel ---
        btns = QHBoxLayout()
        ok = QPushButton("OK"); cancel = QPushButton("Cancel")
        btns.addWidget(ok); btns.addWidget(cancel)
        layout.addLayout(btns)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        # --- TypewriterEffect instance ---
        self.typer = TypewriterEffect(self)

        # --- Connect demo buttons ---
        self.btnDemoStart.clicked.connect(self.start_demo)
        self.btnDemoStop.clicked.connect(self.typer.stop)

    def get_values(self):
        return {
            "rate": self.rateSpin.value(),
            "mode": VoiceType[self.modeBox.currentText().replace(" ", "_").upper()],
            "animated": self.animatedBox.isChecked(),
            "interval": self.intervalSpin.value(),
            "by_word": self.wordRadio.isChecked()
        }

    def start_demo(self):
        text = self.demoInput.text()
        self.typer.start(
            label=self.demoLabel,
            text=text,
            base_interval=self.intervalSpin.value(),
            by_word=self.wordRadio.isChecked(),
        )

# # Entry point
# if __name__ == "__main__":
#     import sys
#     from PySide6.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     w = SettingsDialog()
#     w.show()
#     sys.exit(app.exec())
