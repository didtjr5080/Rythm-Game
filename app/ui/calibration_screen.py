from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from app import config
from app.input.mock_emg_reader import MockEMGReader


class CalibrationScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.reader = MockEMGReader()
        self.value_label = QLabel()
        self.value_label.setObjectName("title")
        self.state_label = QLabel()
        self.state_label.setObjectName("sectionTitle")
        self.threshold_label = QLabel()
        self.threshold_label.setObjectName("sectionTitle")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(config.EMG_THRESHOLD)
        self.slider.valueChanged.connect(self.update_threshold)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 30, 36, 30)
        outer.setSpacing(18)

        title = QLabel("Input Calibration")
        title.setObjectName("title")
        subtitle = QLabel("Adjust the EMG activation threshold and test mock input.")
        subtitle.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(16)
        layout.addWidget(QLabel("Current EMG"))
        layout.addWidget(self.value_label)
        layout.addWidget(self.state_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Threshold"))
        row.addWidget(self.slider, 1)
        row.addWidget(self.threshold_label)
        layout.addLayout(row)

        hint = QLabel("MOCK EMG MODE: hold SPACE to activate input.")
        hint.setObjectName("muted")
        layout.addWidget(hint)
        outer.addWidget(panel)

        back = QPushButton("Back")
        back.clicked.connect(self.main_window.show_start_screen)
        outer.addWidget(back)
        outer.addStretch(1)
        self.refresh()

    def update_threshold(self, value: int):
        self.reader.threshold = value
        self.threshold_label.setText(str(value))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.reader.set_space_pressed(True)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.reader.set_space_pressed(False)

    def refresh(self):
        value, activated = self.reader.read()
        self.value_label.setText(f"{value:.0f}")
        self.state_label.setText(f"Activated: {activated}")
        self.threshold_label.setText(str(self.reader.threshold))

