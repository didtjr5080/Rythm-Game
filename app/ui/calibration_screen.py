from collections import deque
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget
from app import config
from app.input.camera import CameraSource, rgb_pixmap
from app.input.input_fusion import InputFusion
from app.settings import load_settings, save_settings
from app.ui.theme import AuroraScreen, GlassPanel, draw_waveform
from app.ui.dashboard import Instrument


class SignalPlot(QWidget):
    def __init__(self):
        super().__init__(); self.raw=deque(maxlen=120); self.filtered=deque(maxlen=120); self.setMinimumHeight(150)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_waveform(p,QRectF(self.rect()).adjusted(12,12,-12,-24),self.raw,self.filtered)


class CalibrationScreen(AuroraScreen):
    def __init__(self,main_window):
        super().__init__(); self.main_window=main_window; self.settings=load_settings()
        self.fusion=InputFusion(use_camera=config.USE_CAMERA and self.settings['camera_enabled'],emg_threshold=self.settings['emg_threshold'],camera_flip=self.settings['camera_flip'])
        self.reader=self.fusion.emg_reader
        self.camera_source=CameraSource(self.settings,enabled=config.USE_CAMERA)
        self.capture=self.camera_source.capture
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        outer=QVBoxLayout(self); outer.setContentsMargins(45,28,45,24)
        title=QLabel('LIVE BIO-CALIBRATION / SONIC LAB'); title.setObjectName('title'); title.setAlignment(Qt.AlignmentFlag.AlignCenter); outer.addWidget(title)
        subtitle=QLabel('Hold SPACE to test mock EMG / Adjust threshold / Save calibration'); subtitle.setObjectName('subtitle'); outer.addWidget(subtitle)
        row=QHBoxLayout(); row.setSpacing(26)
        left=GlassPanel('EMG DSP FILTER & THRESHOLD'); ll=QVBoxLayout(left); ll.setContentsMargins(16,44,16,18)
        self.plot=SignalPlot(); ll.addWidget(self.plot,1)
        self.value_label=QLabel(); self.value_label.setObjectName('title'); ll.addWidget(self.value_label)
        self.state_label=QLabel(); ll.addWidget(self.state_label)
        center=GlassPanel('NEURO-MOTOR PERFORMANCE REPORT'); cl=QVBoxLayout(center); cl.setContentsMargins(16,44,16,18); cl.addWidget(Instrument('performance'))
        right=GlassPanel('LIVE BIO-CALIBRATION'); rl=QVBoxLayout(right); rl.setContentsMargins(16,44,16,18)
        self.bio=Instrument('bio'); rl.addWidget(self.bio,1)
        self.slider=QSlider(Qt.Orientation.Horizontal); self.slider.setRange(0,max(580,self.settings['emg_threshold'])); self.slider.setValue(self.settings['emg_threshold']); self.slider.valueChanged.connect(self.update_threshold); rl.addWidget(self.slider)
        self.threshold_label=QLabel(); rl.addWidget(self.threshold_label)
        for panel in (left,center,right): row.addWidget(panel,1)
        outer.addLayout(row,1)
        save=QPushButton('Save Calibration'); save.setObjectName('primary'); save.clicked.connect(self.save_calibration); outer.addWidget(save)
        back=QPushButton('Back'); back.clicked.connect(self.go_back); outer.addWidget(back)
        self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(33)
        self.update_threshold(self.slider.value()); self.refresh()

    def update_threshold(self,value):
        self.reader.threshold=value; self.bio.threshold=value; self.bio.update()
        self.threshold_label.setText(f'THRESHOLD: {value}')

    def save_calibration(self):
        self.settings['emg_threshold']=self.slider.value(); save_settings(self.settings)
        self.threshold_label.setText(f'SAVED THRESHOLD: {self.slider.value()}')

    def refresh(self):
        frame=self.camera_source.read()
        state,_=self.fusion.read(frame)
        self.plot.raw.append(self.fusion.raw_emg_value); self.plot.filtered.append(self.fusion.filtered_emg_value); self.plot.update()
        self.value_label.setText(f'{state.emg_value:.0f} EMG')
        self.state_label.setText(('MUSCLE ACTIVE / ' if state.emg_activated else 'RESTING / ')+getattr(self.reader,'status','MOCK EMG'))
        self.bio.camera_pixmap=rgb_pixmap(self.fusion.latest_frame_rgb)
        self.bio.hand_diagnostic=f"FINGERS: {state.finger_count if state.finger_count is not None else '--'} / {state.hand_label or '--'} / {state.tracker_status or '--'}"
        self.bio.finger_states=self.fusion.finger_states
        tracker=self.fusion.tracker
        self.bio.tracker_warning=tracker.diagnostic_summary if tracker and not tracker.backend_is_mediapipe else ''
        self.bio.landmarks=self.fusion.hand_landmarks_norm
        mock=not hasattr(self.reader,'serial') or self.reader.serial is None
        self.bio.sensor_status=self.camera_source.status+' / '+('TRACKED' if self.bio.landmarks else 'NO HAND')

    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_Space: self.fusion.set_space_pressed(True)
        else: super().keyPressEvent(event)
    def keyReleaseEvent(self,event):
        if event.key()==Qt.Key.Key_Space: self.fusion.set_space_pressed(False)
        else: super().keyReleaseEvent(event)
    def showEvent(self,event):
        super().showEvent(event); self.setFocus()
    def stop(self):
        self.timer.stop(); self.fusion.close()
        self.camera_source.release(); self.capture=None
    def go_back(self):
        self.stop(); self.main_window.show_start_screen()
    def closeEvent(self,event):
        self.stop(); super().closeEvent(event)
