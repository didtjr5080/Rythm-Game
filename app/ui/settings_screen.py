import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from app.i18n import tr
from app import config
from app.input.live_video import open_live_video
from app.input.emg_devices import discover_emg_devices
from app.input.emg_reader import SerialEMGReader
from app.input.emg_session import EMGLease
from app.input.emg_factory import create_emg_reader
from app.input.emg_processing import calibration_thresholds
from statistics import median
from app.input.mock_emg_reader import MockEMGReader
from app.input.camera import rgb_pixmap
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
        self.camera_enabled_checkbox = QCheckBox('메뉴 손 커서 사용 / 웹캠 (저장 후 적용)')
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
        self.camera_preview.setFixedHeight(200)
        self.camera_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.camera_preview.setWordWrap(True)
        self.camera_status = QLabel()
        self.camera_status.setWordWrap(False)
        self.camera_status.setFixedHeight(self.camera_status.fontMetrics().lineSpacing()*3+12)
        self.camera_status.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.menu_camera_timer = QTimer(self)
        self.menu_camera_timer.timeout.connect(self.refresh_menu_camera_status)
        self.language_combo = QComboBox()
        self.window_mode_combo = QComboBox()
        self.resolution_combo = QComboBox()
        self.volume_slider, self.volume_value = self._slider(0, 100, int(self.settings["music_volume"] * 100))
        self.note_speed_slider, self.note_speed_value = self._slider(200, 900, int(self.settings["note_speed"]))
        self.judge_line_slider, self.judge_line_value = self._slider(
            55, 92, int(self.settings["judgement_line_y_ratio"] * 100)
        )
        self.emg_threshold_slider = QDoubleSpinBox()
        self.emg_threshold_slider.setRange(0, 1023)
        self.emg_threshold_slider.setDecimals(3)
        self.emg_threshold_slider.setSingleStep(.1)
        self.emg_threshold_slider.setValue(self.settings['emg_threshold'])
        self.emg_threshold_value = QLabel()
        self.emg_mode_combo = QComboBox()
        self.emg_mode_combo.addItem('Real EMG sensor', 'serial')
        self.emg_mode_combo.addItem('Demo / SPACE input', 'mock')
        self.emg_mode_combo.setCurrentIndex(max(0,self.emg_mode_combo.findData(self.settings['emg_input_mode'])))
        self.emg_backend_combo = QComboBox()
        self.emg_backend_combo.addItem('OYMotion USB dongle / 8CH 12bit 500Hz', 'oymotion')
        self.emg_backend_combo.addItem('Legacy Arduino / single-channel serial', 'legacy')
        self.emg_backend_combo.setCurrentIndex(max(0,self.emg_backend_combo.findData(self.settings['emg_backend'])))
        self.emg_port_combo = QComboBox()
        self.emg_baud_combo = QComboBox()
        for baud in (9600,57600,115200): self.emg_baud_combo.addItem(str(baud),baud)
        self.emg_baud_combo.setCurrentIndex(self.emg_baud_combo.findData(self.settings['emg_baudrate']))
        self.emg_signal_combo = QComboBox()
        self.emg_signal_combo.addItem('Filtered activity / SZH-GJD001 firmware RMS', 'envelope')
        self.emg_signal_combo.addItem('NO BANDPASS / DC removed RMS (comparison)', 'unfiltered')
        self.emg_signal_combo.addItem('Direct A0 / ENV sensors (not SZH-GJD001)', 'raw')
        self.emg_signal_combo.setCurrentIndex(max(0,self.emg_signal_combo.findData(self.settings['emg_signal'])))
        self.emg_status = QLabel('Connect the EMG board by USB, refresh devices, then test.')
        self.emg_status.setWordWrap(True)
        self.emg_test_reader = None
        self.emg_calibration_phase = None
        self.emg_rest_samples = None
        self.emg_calibration_samples = []
        self.emg_release_threshold = self.settings['emg_release_threshold']
        self.emg_devices = []
        self.emg_timer = QTimer(self)
        self.emg_timer.timeout.connect(self.refresh_emg_test)
        self.device_timer = QTimer(self)
        self.device_timer.timeout.connect(self.refresh_emg_devices)
        self.refresh_emg_devices()
        self.device_timer.start(2000)
        for combo in (self.emg_backend_combo,self.emg_mode_combo,self.emg_port_combo,self.emg_baud_combo,self.emg_signal_combo):
            combo.currentIndexChanged.connect(self.emg_source_changed)
        self._build()
        self.update_backend_controls()

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
        hand_help=QLabel('HAND CURSOR: OPEN = MOVE / FIST = CLICK / 2 FINGERS + WRIST BACK/IN = SCROLL UP/DOWN / STRAIGHT = STOP')
        hand_help.setObjectName('subtitle'); hand_help.setWordWrap(True)
        outer.addWidget(hand_help)

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
        self.camera_debug_checkbox.hide()
        self.camera_flip_checkbox.hide()

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
        self.emg_threshold_slider.hide()
        self.emg_threshold_value.hide()
        self.camera_preview.hide()
        layout.addWidget(self.camera_enabled_checkbox,8,0,1,3)
        layout.addWidget(QLabel('메뉴 웹캠 / 해상도'),9,0)
        layout.addWidget(self.camera_index_combo,9,1)
        layout.addWidget(self.camera_resolution_combo,9,2)
        layout.addWidget(self.camera_flip_checkbox,10,0)
        layout.addWidget(self.camera_status,10,1,1,2)
        layout.addWidget(QLabel('게임 중 웹캠 OFF / 핀치: Leap 전용 / 근전도: armband 전용'),11,0,1,3)
        layout.addWidget(QLabel('Leap Motion 핀치 보정은 매 게임 시작 전에 진행합니다.'),12,0,1,3)
        layout.addWidget(QLabel('EMG hardware'),13,0); layout.addWidget(self.emg_backend_combo,13,1,1,2)
        layout.addWidget(QLabel('EMG input mode'),14,0); layout.addWidget(self.emg_mode_combo,14,1)
        layout.addWidget(QLabel('EMG device / COM port'),15,0); layout.addWidget(self.emg_port_combo,15,1)
        refresh=QPushButton('Refresh EMG Devices'); refresh.clicked.connect(self.refresh_emg_devices); layout.addWidget(refresh,15,2)
        layout.addWidget(QLabel('EMG baud rate'),16,0); layout.addWidget(self.emg_baud_combo,16,1)
        layout.addWidget(QLabel('EMG signal type'),17,0); layout.addWidget(self.emg_signal_combo,17,1)
        connect=QPushButton('Connect / Test EMG'); connect.clicked.connect(self.start_emg_test); layout.addWidget(connect,18,0)
        layout.addWidget(self.emg_status,18,1,1,2)
        layout.addWidget(QLabel('EMG: 3 seconds of rest before each game / baseline + 0.01'),19,0,1,3)
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
        self.emg_threshold_slider.valueChanged.connect(self.clear_emg_release)
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

    def refresh_emg_devices(self):
        selected=self.emg_port_combo.currentData() or self.settings['emg_port']
        try:
            self.emg_devices=discover_emg_devices()
        except Exception as exc:
            self.emg_status.setText(f'Device search failed: {exc}')
            return
        self.emg_port_combo.blockSignals(True)
        self.emg_port_combo.clear()
        self.emg_port_combo.addItem('Auto detect EMG firmware','auto')
        for device in self.emg_devices:
            self.emg_port_combo.addItem(f"{device['port']} / {device['description']}",device['port'])
        if selected!='auto' and self.emg_port_combo.findData(selected)<0:
            self.emg_port_combo.addItem(f'{selected} / disconnected',selected)
        self.emg_port_combo.setCurrentIndex(max(0,self.emg_port_combo.findData(selected)))
        self.emg_port_combo.blockSignals(False)
        if not self.emg_devices and self.emg_test_reader is None:
            self.emg_status.setText('No COM devices found. Check board power, USB data cable and USB serial driver.')

    def emg_settings(self):
        port=self.emg_port_combo.currentData()
        identity=''
        if port!='auto':
            device=next((d for d in self.emg_devices if d['port']==port),None)
            identity=device['identity'] if device else (self.settings['emg_device_id'] if port==self.settings['emg_port'] else '')
        elif (isinstance(self.emg_test_reader,SerialEMGReader) or isinstance(self.emg_test_reader,EMGLease) and self.emg_test_reader.is_serial) and self.emg_test_reader.verified:
            identity=self.emg_test_reader.connected_identity
        if self.emg_backend_combo.currentData() == 'oymotion':
            identity = (self.emg_test_reader.connected_identity if self.emg_test_reader is not None
                        and getattr(self.emg_test_reader, 'verified', False) else '')
        return dict(emg_backend=self.emg_backend_combo.currentData(), emg_input_mode=self.emg_mode_combo.currentData(), emg_port=port,
                    emg_device_id=identity, emg_baudrate=self.emg_baud_combo.currentData(),
                    emg_signal=self.emg_signal_combo.currentData())

    def start_emg_test(self):
        self.stop_emg_test()
        settings=self.emg_settings()
        threshold=self.emg_threshold_slider.value()
        session = getattr(self.main_window, 'emg_session', None)
        if session is not None:
            self.emg_test_reader=session.acquire(dict(self.settings, **settings,
                emg_threshold=threshold, emg_release_threshold=self.emg_release_threshold))
        elif settings['emg_input_mode']=='mock':
            self.emg_test_reader=MockEMGReader(threshold)
        else:
            self.emg_test_reader=create_emg_reader(dict(self.settings, **settings), threshold=threshold)
        self.emg_timer.start(33)
        self.refresh_emg_test()

    def refresh_emg_test(self):
        reader=self.emg_test_reader
        if reader is None: return
        reader.threshold=self.emg_threshold_slider.value()
        value,activated=reader.read()
        status=getattr(reader,'status','MOCK EMG / SPACE')
        self.emg_status.setText(f'{status} / ACTIVITY: {value:.2f} / GAME: 3s rest, then +0.01')
        channels = getattr(reader, 'channel_rms', None)
        if channels is not None:
            self.emg_status.setText(self.emg_status.text()+'\nCH1-8 RMS: '+', '.join(f'{v:.2f}' for v in channels))

    def update_backend_controls(self):
        legacy = self.emg_backend_combo.currentData() == 'legacy'
        self.emg_signal_combo.setEnabled(legacy)
        self.emg_baud_combo.setEnabled(legacy)

    def clear_emg_release(self, *_args):
        self.emg_release_threshold = None
        if isinstance(self.emg_test_reader, (SerialEMGReader, EMGLease)):
            self.emg_test_reader.set_thresholds(self.emg_threshold_slider.value())

    def emg_source_changed(self, *_args):
        self.update_backend_controls()
        self.clear_emg_release()
        self.stop_emg_test()

    def stop_emg_test(self,*_args):
        self.emg_calibration_phase = None
        self.emg_rest_samples = None
        self.emg_calibration_samples = []
        self.emg_contractions = [[], [], []]
        self.emg_recoveries = [[], [], []]
        self.emg_threshold_slider.setEnabled(True)
        if hasattr(self, 'emg_calibration_status'):
            self.emg_calibration_status.setText('보정 초기화: 안정 측정 → 수축 측정 순서로 진행하세요.')
        self.emg_timer.stop()
        if self.emg_test_reader is not None: self.emg_test_reader.close()
        self.emg_test_reader=None

    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_Space and self.emg_test_reader is not None:
            self.emg_test_reader.set_space_pressed(True)
        else: super().keyPressEvent(event)

    def keyReleaseEvent(self,event):
        if event.key()==Qt.Key.Key_Space and self.emg_test_reader is not None:
            self.emg_test_reader.set_space_pressed(False)
        else: super().keyReleaseEvent(event)

    def stop_camera_preview(self):
        self.preview_timer.stop()
        if self.preview_tracker is not None: self.preview_tracker.close(); self.preview_tracker=None
        if self.preview_source is not None: self.preview_source.release(); self.preview_source=None

    def start_camera_preview(self):
        return  # Webcam input is disabled; hand input comes from Leap Motion.
        self.stop_camera_preview()
        settings=dict(self.settings, camera_enabled=self.camera_enabled_checkbox.isChecked(),
                      camera_index=self.camera_index_combo.currentData(),
                      camera_resolution=self.camera_resolution_combo.currentText(),
                      camera_flip=self.camera_flip_checkbox.isChecked())
        self.preview_source=open_live_video(self.main_window,settings,enabled=config.USE_CAMERA)
        self.preview_tracker=self.preview_source
        self._preview_frame_reference=None
        self.camera_status.setText(self.preview_source.status+' / '+self.preview_source.error if self.preview_source.error else self.preview_source.status)
        self.refresh_camera_preview()
        self.preview_timer.start(33)

    def refresh_camera_preview(self):
        if self.preview_source is None: return
        self.preview_tracker.set_flip(self.camera_flip_checkbox.isChecked())
        frame=self.preview_source.read()
        if frame is None:
            self._set_camera_status(self.preview_source.status+'\n'+(self.preview_source.error or 'Waiting for a fresh camera frame')+'\n1-5 fingers: lanes 1-5 / Fist: none')
            self.camera_preview.setText(self.preview_source.status)
            return
        if frame is self._preview_frame_reference: return
        self._preview_frame_reference=frame
        import cv2
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
            backend='MediaPipe ready' if self.preview_tracker.backend_is_mediapipe else 'MediaPipe unavailable / check camera'
            self._set_camera_status(self.preview_source.status+'\n'+backend+f"\nFingers: {count if count is not None else '--'} / 1-5: lanes / Fist: none")
            self.camera_status.setToolTip(self.preview_tracker.diagnostic_summary)
            style='color: #6EE7B7;' if self.preview_tracker.backend_is_mediapipe else 'color: #FB923C;'
            if self.camera_status.styleSheet()!=style: self.camera_status.setStyleSheet(style)
        self.camera_preview.setPixmap(pixmap.scaled(480,200,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def _set_camera_status(self, text):
        if self.camera_status.text()!=text: self.camera_status.setText(text)

    def refresh_menu_camera_status(self):
        source = getattr(self.main_window, '_navigation_video', None)
        status = (source.status+'\n'+source.diagnostic_summary if source is not None
                  else '메뉴 웹캠 꺼짐 / 변경 사항은 저장 후 적용됩니다.')
        self._set_camera_status(status)
        self.camera_status.setToolTip(status)

    def go_back(self):
        defer = getattr(self.main_window, '_defer_hand_navigation', None)
        if defer is not None and defer(self.go_back): return
        self.stop_emg_test(); self.device_timer.stop()
        self.stop_camera_preview(); self.main_window.show_start_screen()

    def showEvent(self,event):
        super().showEvent(event)
        self.refresh_emg_devices()
        self.device_timer.start(2000)
        self.menu_camera_timer.start(250)

    def hideEvent(self,event):
        self.menu_camera_timer.stop()
        self.stop_emg_test(); self.device_timer.stop()
        self.stop_camera_preview(); super().hideEvent(event)

    def reset_defaults(self):
        self.emg_backend_combo.setCurrentIndex(0)
        self.clear_emg_release()
        self.stop_emg_test()
        self.emg_mode_combo.setCurrentIndex(0)
        self.emg_port_combo.setCurrentIndex(0)
        self.emg_baud_combo.setCurrentIndex(self.emg_baud_combo.findData(DEFAULT_SETTINGS['emg_baudrate']))
        self.emg_signal_combo.setCurrentIndex(max(0,self.emg_signal_combo.findData(DEFAULT_SETTINGS['emg_signal'])))
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
        self.emg_threshold_slider.setValue(DEFAULT_SETTINGS["emg_threshold"])

    def save_and_back(self):
        defer = getattr(self.main_window, '_defer_hand_navigation', None)
        if defer is not None and defer(self.save_and_back): return
        emg_settings=self.emg_settings()
        self.stop_emg_test(); self.device_timer.stop()
        self.stop_camera_preview()
        save_settings(
            {
                **emg_settings,
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
                "emg_release_threshold": self.emg_release_threshold,
            }
        )
        self.main_window.show_start_screen()
        if hasattr(self.main_window, "apply_window_settings"):
            self.main_window.apply_window_settings()
