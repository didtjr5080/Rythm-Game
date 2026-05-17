from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.i18n import tr
from app.settings import AVAILABLE_RESOLUTIONS, DEFAULT_SETTINGS, load_settings, save_settings


class SettingsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = load_settings()
        self.language = self.settings["language"]
        self.hud_checkbox = QCheckBox(tr("show_input_hud", self.language))
        self.judgement_checkbox = QCheckBox(tr("show_judgement_text", self.language))
        self.camera_debug_checkbox = QCheckBox(tr("show_camera_debug", self.language))
        self.camera_flip_checkbox = QCheckBox(tr("flip_camera", self.language))
        self.language_combo = QComboBox()
        self.window_mode_combo = QComboBox()
        self.resolution_combo = QComboBox()
        self.volume_slider, self.volume_value = self._slider(0, 100, int(self.settings["music_volume"] * 100))
        self.note_speed_slider, self.note_speed_value = self._slider(200, 900, int(self.settings["note_speed"]))
        self.judge_line_slider, self.judge_line_value = self._slider(
            55, 92, int(self.settings["judgement_line_y_ratio"] * 100)
        )
        self.emg_threshold_slider, self.emg_threshold_value = self._slider(0, 1000, int(self.settings["emg_threshold"]))
        self._build()

    def _slider(self, minimum: int, maximum: int, value: int):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        label = QLabel()
        label.setObjectName("sectionTitle")
        return slider, label

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 30, 36, 30)
        outer.setSpacing(18)
        title = QLabel(tr("settings", self.language))
        title.setObjectName("title")
        subtitle = QLabel(tr("settings_subtitle", self.language))
        subtitle.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(18)

        self.hud_checkbox.setChecked(self.settings["show_game_hud"])
        self.judgement_checkbox.setChecked(self.settings["show_judgement_text"])
        self.camera_debug_checkbox.setChecked(self.settings["show_camera_debug"])
        self.camera_flip_checkbox.setChecked(self.settings["camera_flip"])
        layout.addWidget(self.hud_checkbox, 0, 0)
        layout.addWidget(self.judgement_checkbox, 0, 1)
        layout.addWidget(self.camera_debug_checkbox, 1, 0)
        layout.addWidget(self.camera_flip_checkbox, 1, 1)

        self._setup_combo_boxes()
        layout.addWidget(QLabel(tr("language", self.language)), 2, 0)
        layout.addWidget(self.language_combo, 2, 1)
        layout.addWidget(QLabel(tr("window_mode", self.language)), 3, 0)
        layout.addWidget(self.window_mode_combo, 3, 1)
        layout.addWidget(QLabel(tr("resolution", self.language)), 4, 0)
        layout.addWidget(self.resolution_combo, 4, 1)

        self._add_slider_row(layout, 5, tr("music_volume", self.language), self.volume_slider, self.volume_value, "%")
        self._add_slider_row(layout, 6, tr("note_speed", self.language), self.note_speed_slider, self.note_speed_value, "")
        self._add_slider_row(layout, 7, tr("judgement_line", self.language), self.judge_line_slider, self.judge_line_value, "%")
        self._add_slider_row(layout, 8, tr("emg_threshold", self.language), self.emg_threshold_slider, self.emg_threshold_value, "")
        outer.addWidget(panel)

        row = QHBoxLayout()
        save = QPushButton(tr("save", self.language))
        save.setObjectName("primary")
        reset = QPushButton(tr("reset_defaults", self.language))
        back = QPushButton(tr("back", self.language))
        save.clicked.connect(self.save_and_back)
        reset.clicked.connect(self.reset_defaults)
        back.clicked.connect(self.main_window.show_start_screen)
        row.addWidget(save)
        row.addWidget(reset)
        row.addWidget(back)
        outer.addLayout(row)
        outer.addStretch(1)

        self.volume_slider.valueChanged.connect(lambda value: self.update_label(self.volume_value, value, "%"))
        self.note_speed_slider.valueChanged.connect(lambda value: self.update_label(self.note_speed_value, value, ""))
        self.judge_line_slider.valueChanged.connect(lambda value: self.update_label(self.judge_line_value, value, "%"))
        self.emg_threshold_slider.valueChanged.connect(lambda value: self.update_label(self.emg_threshold_value, value, ""))
        self.refresh_labels()

    def _setup_combo_boxes(self):
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Korean", "ko")
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(self.settings["language"])))

        for mode in ("windowed", "borderless", "fullscreen"):
            self.window_mode_combo.addItem(tr(mode, self.language), mode)
        self.window_mode_combo.setCurrentIndex(max(0, self.window_mode_combo.findData(self.settings["window_mode"])))

        for resolution in AVAILABLE_RESOLUTIONS:
            self.resolution_combo.addItem(resolution, resolution)
        self.resolution_combo.setCurrentIndex(max(0, self.resolution_combo.findData(self.settings["resolution"])))

    def _add_slider_row(self, layout: QGridLayout, row: int, name: str, slider: QSlider, value_label: QLabel, suffix: str):
        layout.addWidget(QLabel(name), row, 0)
        layout.addWidget(slider, row, 1)
        layout.addWidget(value_label, row, 2)
        self.update_label(value_label, slider.value(), suffix)

    def update_label(self, label: QLabel, value: int, suffix: str):
        label.setText(f"{value}{suffix}")

    def refresh_labels(self):
        self.update_label(self.volume_value, self.volume_slider.value(), "%")
        self.update_label(self.note_speed_value, self.note_speed_slider.value(), "")
        self.update_label(self.judge_line_value, self.judge_line_slider.value(), "%")
        self.update_label(self.emg_threshold_value, self.emg_threshold_slider.value(), "")

    def reset_defaults(self):
        self.hud_checkbox.setChecked(DEFAULT_SETTINGS["show_game_hud"])
        self.judgement_checkbox.setChecked(DEFAULT_SETTINGS["show_judgement_text"])
        self.camera_debug_checkbox.setChecked(DEFAULT_SETTINGS["show_camera_debug"])
        self.camera_flip_checkbox.setChecked(DEFAULT_SETTINGS["camera_flip"])
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(DEFAULT_SETTINGS["language"])))
        self.window_mode_combo.setCurrentIndex(max(0, self.window_mode_combo.findData(DEFAULT_SETTINGS["window_mode"])))
        self.resolution_combo.setCurrentIndex(max(0, self.resolution_combo.findData(DEFAULT_SETTINGS["resolution"])))
        self.volume_slider.setValue(int(DEFAULT_SETTINGS["music_volume"] * 100))
        self.note_speed_slider.setValue(int(DEFAULT_SETTINGS["note_speed"]))
        self.judge_line_slider.setValue(int(DEFAULT_SETTINGS["judgement_line_y_ratio"] * 100))
        self.emg_threshold_slider.setValue(int(DEFAULT_SETTINGS["emg_threshold"]))

    def save_and_back(self):
        save_settings(
            {
                "show_game_hud": self.hud_checkbox.isChecked(),
                "language": self.language_combo.currentData(),
                "window_mode": self.window_mode_combo.currentData(),
                "resolution": self.resolution_combo.currentData(),
                "show_judgement_text": self.judgement_checkbox.isChecked(),
                "show_camera_debug": self.camera_debug_checkbox.isChecked(),
                "camera_flip": self.camera_flip_checkbox.isChecked(),
                "music_volume": self.volume_slider.value() / 100.0,
                "note_speed": self.note_speed_slider.value(),
                "judgement_line_y_ratio": self.judge_line_slider.value() / 100.0,
                "emg_threshold": self.emg_threshold_slider.value(),
            }
        )
        if hasattr(self.main_window, "apply_window_settings"):
            self.main_window.apply_window_settings()
        self.main_window.show_start_screen()
