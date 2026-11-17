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
        self.camera_preview.setFixedHeight(200)
        self.camera_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.camera_preview.setWordWrap(True)
        self.camera_status = QLabel()
        self.camera_status.setWordWrap(False)
        self.camera_status.setFixedHeight(self.camera_status.fontMetrics().lineSpacing()*3+12)
        self.camera_status.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
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
        for combo in (self.emg_mode_combo,self.emg_port_combo,self.emg_baud_combo,self.emg_signal_combo):
            combo.currentIndexChanged.connect(self.emg_source_changed)
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
        layout.addWidget(QLabel('EMG input mode'),14,0); layout.addWidget(self.emg_mode_combo,14,1)
        layout.addWidget(QLabel('EMG device / COM port'),15,0); layout.addWidget(self.emg_port_combo,15,1)
        refresh=QPushButton('Refresh EMG Devices'); refresh.clicked.connect(self.refresh_emg_devices); layout.addWidget(refresh,15,2)
        layout.addWidget(QLabel('EMG baud rate'),16,0); layout.addWidget(self.emg_baud_combo,16,1)
        layout.addWidget(QLabel('EMG signal type'),17,0); layout.addWidget(self.emg_signal_combo,17,1)
        connect=QPushButton('Connect / Test EMG'); connect.clicked.connect(self.start_emg_test); layout.addWidget(connect,18,0)
        layout.addWidget(self.emg_status,18,1,1,2)
        rest = QPushButton('1. 안정 상태 측정 (힘 빼기)')
        rest.clicked.connect(lambda: self.start_emg_calibration('rest'))
        active = QPushButton('2. 3회 반복 수축 / 임계값 자동 보정')
        active.clicked.connect(lambda: self.start_emg_calibration('active'))
        layout.addWidget(rest,19,0)
        layout.addWidget(active,19,1,1,2)
        self.emg_calibration_status = QLabel('안정 측정 약 4초 → 안내에 따라 힘빼기/수축 3회 약 12초 → Save로 저장')
        self.emg_calibration_status.setWordWrap(True)
        layout.addWidget(self.emg_calibration_status,20,0,1,3)
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
        elif isinstance(self.emg_test_reader,SerialEMGReader) and self.emg_test_reader.verified:
            identity=self.emg_test_reader.connected_identity
        return dict(emg_input_mode=self.emg_mode_combo.currentData(), emg_port=port,
                    emg_device_id=identity, emg_baudrate=self.emg_baud_combo.currentData(),
                    emg_signal=self.emg_signal_combo.currentData())

    def start_emg_test(self):
        self.stop_emg_test()
        settings=self.emg_settings()
        threshold=self.emg_threshold_slider.value()
        if settings['emg_input_mode']=='mock':
            self.emg_test_reader=MockEMGReader(threshold)
        else:
            self.emg_test_reader=SerialEMGReader(port=settings['emg_port'],baudrate=settings['emg_baudrate'],
                threshold=threshold,device_id=settings['emg_device_id'],signal=settings['emg_signal'],
                release_threshold=self.emg_release_threshold)
        self.emg_timer.start(33)
        self.refresh_emg_test()

    def refresh_emg_test(self):
        reader=self.emg_test_reader
        if reader is None: return
        reader.threshold=self.emg_threshold_slider.value()
        value,activated=reader.read()
        status=getattr(reader,'status','MOCK EMG / SPACE')
        self.emg_status.setText(f'{status} / VALUE: {value:.2f} / ACTIVE: {activated} / '+
            f"RAW: {getattr(reader,'raw_value',value):.0f} / ACTIVITY: {value:.2f} / ON: {reader.threshold:.3f} / OFF: {getattr(reader,'release_level',reader.threshold*.6):.3f}")
        if getattr(reader, 'bypass_available', False):
            self.emg_status.setText(self.emg_status.text()+f' / BP RMS: {reader.envelope_value:.0f} / NO BP RMS: {reader.unfiltered_value:.0f}')
        self.emg_status.setText(self.emg_status.text()+(' / DIR: DOWN' if getattr(reader,'falling_activation',False) else ' / DIR: UP'))
        self.collect_emg_calibration(reader)

    def start_emg_calibration(self, phase):
        if self.emg_calibration_phase is not None:
            return
        if self.emg_mode_combo.currentData() != 'serial':
            self.emg_calibration_status.setText('자동 보정은 실제 EMG 센서 모드에서 진행하세요.')
            return
        if phase == 'active' and self.emg_rest_samples is None:
            self.emg_calibration_status.setText('먼저 1번 안정 상태 측정을 진행하세요.')
            return
        if self.emg_test_reader is None:
            self.start_emg_test()
        reader = self.emg_test_reader
        if isinstance(reader, SerialEMGReader) and reader.board_name == 'ESP8266_A0':
            if reader.firmware_version != 2 or reader.signal not in ('envelope', 'unfiltered'):
                self.emg_calibration_status.setText('SZH-GJD001: 펌웨어 v2와 RMS 신호 종류를 선택한 뒤 보정하세요.')
                return
            if reader.signal == 'unfiltered' and not reader.bypass_available:
                self.emg_calibration_status.setText('비교용 펌웨어가 필요합니다. NO BANDPASS 데이터 수신 후 보정하세요.')
                return
        if reader.serial is None or time.monotonic()-reader._last_sample >= .15:
            self.emg_calibration_status.setText('Connect / Test EMG로 연결한 뒤 신호가 들어오면 다시 누르세요.')
            return
        if phase == 'rest':
            self.emg_rest_samples = None
        self.emg_calibration_phase = phase
        self.emg_calibration_started = time.monotonic()
        self.emg_calibration_samples = []
        self.emg_contractions = [[], [], []]
        self.emg_recoveries = [[], [], []]
        self.emg_threshold_slider.setEnabled(False)
        self.emg_calibration_status.setText('힘을 빼고 유지하세요.' if phase == 'rest' else '1/3: 먼저 힘을 빼세요. 화면 안내에 따라 힘빼기/수축을 반복합니다.')

    def collect_emg_calibration(self, reader):
        phase = self.emg_calibration_phase
        if phase is None:
            return
        now = time.monotonic()
        if reader.serial is None or now-reader._last_sample >= .15:
            self.emg_calibration_phase = None
            self.emg_rest_samples = None
            self.emg_threshold_slider.setEnabled(True)
            self.emg_calibration_status.setText('신호가 끊겨 보정을 취소했습니다. 안정 측정부터 다시 진행하세요.')
            return
        elapsed = now-self.emg_calibration_started
        # Discard each transition; collect actual packets into three separate repetitions.
        duration = 3.75 if phase == 'rest' else 12.0
        if phase == 'rest':
            if .75 <= elapsed < duration:
                self.emg_calibration_samples.extend(reader.samples)
            instruction = f'힘 빼기: {max(0,duration-elapsed):.1f}초'
        else:
            step = min(int(elapsed//2), 5)
            within = elapsed-step*2
            contraction = step%2 == 1
            blocks = self.emg_contractions if contraction else self.emg_recoveries
            if elapsed < duration and .5 <= within < 2:
                blocks[step//2].extend(reader.samples)
            instruction = f'{step//2+1}/3: '+('힘을 주세요' if contraction else '힘을 빼세요')+f' / {max(0,2-within):.1f}초'
        self.emg_calibration_status.setText(instruction)
        if elapsed < duration:
            return
        self.emg_calibration_phase = None
        self.emg_threshold_slider.setEnabled(True)
        samples = self.emg_calibration_samples
        if phase == 'rest':
            if not samples:
                self.emg_calibration_status.setText('안정 측정값이 없습니다. 연결을 확인하고 다시 측정하세요.')
                return
            self.emg_rest_samples = samples
            self.emg_calibration_status.setText(f'안정 측정 완료: 중앙값 {median(samples):.2f}. 2번을 누르고 안내에 따라 힘빼기/수축을 3회 반복하세요.')
            return
        try:
            threshold, release = calibration_thresholds(self.emg_rest_samples, self.emg_contractions, self.emg_recoveries)
        except ValueError as exc:
            self.emg_calibration_status.setText(str(exc))
            return
        self.emg_threshold_slider.setValue(threshold)
        self.emg_release_threshold = release
        reader.set_thresholds(threshold, release)
        repeats = '/'.join(f'{median(block):.2f}' for block in self.emg_contractions)
        direction = '감소형' if reader.falling_activation else '증가형'
        self.emg_calibration_status.setText(f'측정값 보정 적용 ({direction}): 초기 안정 {median(self.emg_rest_samples):.2f} / 수축 3회 {repeats} / ON {threshold:.3f} / OFF {release:.3f}. Save로 저장하세요.')

    def clear_emg_release(self, *_args):
        self.emg_release_threshold = None
        if isinstance(self.emg_test_reader, SerialEMGReader):
            self.emg_test_reader.set_thresholds(self.emg_threshold_slider.value())

    def emg_source_changed(self, *_args):
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

    def go_back(self):
        defer = getattr(self.main_window, '_defer_hand_navigation', None)
        if defer is not None and defer(self.go_back): return
        self.stop_emg_test(); self.device_timer.stop()
        self.stop_camera_preview(); self.main_window.show_start_screen()

    def showEvent(self,event):
        super().showEvent(event)
        self.refresh_emg_devices()
        self.device_timer.start(2000)

    def hideEvent(self,event):
        self.stop_emg_test(); self.device_timer.stop()
        self.stop_camera_preview(); super().hideEvent(event)

    def reset_defaults(self):
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
