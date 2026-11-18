from collections import deque
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from app import config
from app.input.camera import rgb_pixmap
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
        self.fusion=InputFusion(emg_threshold=self.settings['emg_threshold'], emg_session=getattr(main_window,'emg_session',None))
        self.reader=self.fusion.emg_reader
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
        self.slider=QDoubleSpinBox(); self.slider.setDecimals(3); self.slider.setSingleStep(.1); self.slider.setRange(0,1023); self.slider.setValue(self.settings['emg_threshold']); self.slider.valueChanged.connect(self.update_threshold); rl.addWidget(self.slider)
        self.threshold_label=QLabel(); rl.addWidget(self.threshold_label)
        for panel in (left,center,right): row.addWidget(panel,1)
        outer.addLayout(row,1)
        save=QPushButton('Save Calibration'); save.setObjectName('primary'); save.clicked.connect(self.save_calibration); outer.addWidget(save)
        back=QPushButton('Back'); back.clicked.connect(self.go_back); outer.addWidget(back)
        self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(33)
        self.update_threshold(self.slider.value()); self.refresh()

    def update_threshold(self,value):
        if self.reader.threshold != value and hasattr(self.reader, 'set_thresholds'):
            self.reader.set_thresholds(value)
        self.reader.threshold=value; self.bio.threshold=value; self.bio.update()
        self.threshold_label.setText(f'THRESHOLD: {value}')

    def save_calibration(self):
        self.settings['emg_release_threshold']=getattr(self.reader,'release_threshold',None)
        self.settings['emg_threshold']=self.slider.value(); save_settings(self.settings)
        self.threshold_label.setText(f'SAVED THRESHOLD: {self.slider.value()}')

    def refresh(self):
        frame=None
        state,_=self.fusion.read(frame)
        self.plot.raw.append(self.fusion.raw_emg_value); self.plot.filtered.append(self.fusion.filtered_emg_value); self.plot.update()
        self.value_label.setText(f'{state.emg_value:.2f} EMG ACTIVITY')
        self.state_label.setText(('MUSCLE ACTIVE / ' if state.emg_activated else 'RESTING / ')+getattr(self.reader,'status','MOCK EMG'))
        self.bio.camera_pixmap=rgb_pixmap(self.fusion.latest_frame_rgb)
        self.bio.hand_diagnostic=f"LEAP PINCH: {state.hand_label or '--'}"
        self.bio.finger_states=self.fusion.finger_states
        tracker=self.fusion.tracker
        self.bio.tracker_warning=tracker.last_error or '' if tracker else ''
        self.bio.landmarks=self.fusion.hand_landmarks_norm
        mock=not hasattr(self.reader,'serial') or self.reader.serial is None
        self.bio.sensor_status=state.tracker_status or 'LEAP WAITING'

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
    def go_back(self):
        self.stop(); self.main_window.show_start_screen()
    def closeEvent(self,event):
        self.stop(); super().closeEvent(event)
