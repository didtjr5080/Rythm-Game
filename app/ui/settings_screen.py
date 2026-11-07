from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.i18n import tr
from app import config
from app.input.camera import CameraSource, rgb_pixmap
from app.input.mediapipe_tracker import MediaPipeHandTracker
from app.ui.theme import draw_hand_skeleton_overlay, finger_summary
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QRectF
from app.settings import AVAILABLE_RESOLUTIONS, CAMERA_RESOLUTIONS, DEFAULT_SETTINGS, load_settings, save_settings


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
        self.camera_enabled_checkbox = QCheckBox('Enable real webcam')
        self.camera_enabled_checkbox.setChecked(self.settings['camera_enabled'])
        self.camera_index_combo = QComboBox()
        for index in range(10): self.camera_index_combo.addItem(f'Camera {index}',index)
        self.camera_index_combo.setCurrentIndex(self.settings['camera_index'])
        self.camera_resolution_combo = QComboBox()
        self.camera_resolution_combo.addItems(CAMERA_RESOLUTIONS)
        self.camera_resolution_combo.setCurrentText(self.settings['camera_resolution'])
        self.preview_tracker = None
        self.preview_source = None
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.refresh_camera_preview)
        self.camera_preview = QLabel('Select a camera and click Connect / Test Camera')
        self.camera_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_preview.setMinimumHeight(150)
        self.camera_preview.setWordWrap(True)
        self.camera_status = QLabel()
        self.camera_status.setWordWrap(True)
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
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); scroll.setWidget(content); root.addWidget(scroll)
        outer = QVBoxLayout(content)
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
        layout.addWidget(self.camera_enabled_checkbox,9,0)
        layout.addWidget(QLabel('Webcam device'),10,0); layout.addWidget(self.camera_index_combo,10,1)
        layout.addWidget(QLabel('Webcam capture size'),11,0); layout.addWidget(self.camera_resolution_combo,11,1)
        test = QPushButton('Connect / Test Camera'); test.clicked.connect(self.start_camera_preview)
        layout.addWidget(test,12,0); layout.addWidget(self.camera_status,12,1,1,2)
        layout.addWidget(self.camera_preview,13,0,1,3)
        outer.addWidget(panel)

        row = QHBoxLayout()
        save = QPushButton(tr("save", self.language))
        save.setObjectName("primary")
        reset = QPushButton(tr("reset_defaults", self.language))
        back = QPushButton(tr("back", self.language))
        save.clicked.connect(self.save_and_back)
        reset.clicked.connect(self.reset_defaults)
        back.clicked.connect(self.go_back)
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

    def stop_camera_preview(self):
        self.preview_timer.stop()
        if self.preview_tracker is not None: self.preview_tracker.close(); self.preview_tracker=None
        if self.preview_source is not None: self.preview_source.release(); self.preview_source=None

    def start_camera_preview(self):
        self.stop_camera_preview()
        settings=dict(self.settings, camera_enabled=self.camera_enabled_checkbox.isChecked(),
                      camera_index=self.camera_index_combo.currentData(),
                      camera_resolution=self.camera_resolution_combo.currentText())
        self.preview_source=CameraSource(settings,enabled=config.USE_CAMERA)
        if self.preview_source.capture is not None:
            self.preview_tracker=MediaPipeHandTracker(flip=self.camera_flip_checkbox.isChecked())
        self.camera_status.setText(self.preview_source.status+' / '+self.preview_source.error if self.preview_source.error else self.preview_source.status)
        self.refresh_camera_preview()
        if self.preview_source.capture is not None: self.preview_timer.start(33)

    def refresh_camera_preview(self):
        if self.preview_source is None: return
        frame=self.preview_source.read()
        self.camera_status.setText(self.preview_source.status+' / '+self.preview_source.error if self.preview_source.error else self.preview_source.status)
        if frame is None:
            self.camera_preview.setText(self.preview_source.status)
            return
        cv2=self.preview_source.cv2
        tracked=None
        if self.preview_tracker is not None:
            self.preview_tracker.set_flip(self.camera_flip_checkbox.isChecked())
            tracked=self.preview_tracker.track(frame)
            frame=tracked['frame']
        elif self.camera_flip_checkbox.isChecked(): frame=cv2.flip(frame,1)
        pixmap=rgb_pixmap(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        if tracked is not None:
            painter=QPainter(pixmap)
            if tracked.get('landmarks'):
                draw_hand_skeleton_overlay(painter,QRectF(pixmap.rect()),tracked['landmarks'],finger_states=tracked.get('finger_states'))
            painter.end()
            count=tracked.get('finger_count')
            self.camera_status.setText(self.preview_source.status+' / '+finger_summary(tracked.get('finger_states'))+f" / FINGERS: {count if count is not None else '--'} / "+self.preview_tracker.status+" / 1=LEFT 2=CENTER 3=RIGHT 4/5=POSITION"+(f" / {self.preview_tracker.last_error}" if self.preview_tracker.last_error else ''))
        self.camera_preview.setPixmap(pixmap.scaled(480,200,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def go_back(self):
        self.stop_camera_preview(); self.main_window.show_start_screen()

    def hideEvent(self,event):
        self.stop_camera_preview(); super().hideEvent(event)

    def reset_defaults(self):
        self.stop_camera_preview()
        self.camera_enabled_checkbox.setChecked(DEFAULT_SETTINGS['camera_enabled'])
        self.camera_index_combo.setCurrentIndex(DEFAULT_SETTINGS['camera_index'])
        self.camera_resolution_combo.setCurrentText(DEFAULT_SETTINGS['camera_resolution'])
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
        self.stop_camera_preview()
        save_settings(
            {
                "camera_enabled": self.camera_enabled_checkbox.isChecked(),
                "camera_index": self.camera_index_combo.currentData(),
                "camera_resolution": self.camera_resolution_combo.currentText(),
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
