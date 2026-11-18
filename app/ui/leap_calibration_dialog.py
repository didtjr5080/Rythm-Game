"""Five guided captures using the same Orion samples as gameplay."""
import time

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.input.leap_calibration import (
    LABELS, calculate_thresholds, load_profiles, save_profile,
)
from app.input.leap_tracker import LeapPinchTracker
from app.input.pinch_classifier import features


class LeapCalibrationDialog(QDialog):
    def __init__(self, parent=None, tracker_factory=LeapPinchTracker):
        super().__init__(parent)
        self.setWindowTitle('Leap Motion 핀치 보정')
        self.resize(620, 420)
        self.samples = {}
        self.phase = None
        self.tracker = None
        layout = QVBoxLayout(self)
        info = QLabel('오른손을 사용하세요. 개인 이름을 입력한 뒤 열린 손과 네 핀치를 각각 측정합니다.\n'
                      'Leap Motion만 사용합니다. 매 게임 시작 전에 보정합니다.\n'
                      '측정 버튼 → 1초 준비 → 3초 유지 → 다음 동작. 다섯 동작 측정 후 게임을 시작하세요.')
        info.setWordWrap(True)
        layout.addWidget(info)
        self.profile = QComboBox()
        self.profile.setEditable(True)
        layout.addWidget(self.profile)
        self.active = QLabel()
        layout.addWidget(self.active)
        self.pose = QComboBox()
        for label in ('열린 손 (손가락을 충분히 벌리기)', '엄지 + 검지 (INDEX)',
                      '엄지 + 중지 (MIDDLE)', '엄지 + 약지 (RING)', '엄지 + 소지 (PINKY)'):
            self.pose.addItem(label)
        layout.addWidget(self.pose)
        self.live_status = QLabel()
        self.live_status.setWordWrap(True)
        layout.addWidget(self.live_status)
        self.status = QLabel('Leap 연결 확인 중…')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.progress = QLabel()
        layout.addWidget(self.progress)
        row = QHBoxLayout()
        self.capture = QPushButton('선택 동작 측정')
        self.capture.clicked.connect(self.start_capture)
        row.addWidget(self.capture)
        self.save = QPushButton('보정 완료 · 게임 시작')
        self.save.clicked.connect(self.save_capture)
        row.addWidget(self.save)
        layout.addLayout(row)
        close = QPushButton('취소')
        close.clicked.connect(self.reject)
        layout.addWidget(close)
        try:
            data = load_profiles()
        except (OSError, ValueError) as exc:
            self.status.setText(str(exc))
            for button in (self.capture, self.save):
                button.setEnabled(False)
            return
        self.profile.addItems(data['profiles'])
        self.profile.setCurrentText(data['active'] or 'Player')
        self.active.setText('현재 보정: ' + (data['active'] or '기본값'))
        self.profile.editTextChanged.connect(self.clear_samples)
        self.tracker = tracker_factory()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(20)
        self.refresh_progress()

    def clear_samples(self):
        self.samples.clear()
        self.refresh_progress()

    def refresh_progress(self):
        self.progress.setText(' / '.join(f'{label}: {len(self.samples.get(label, []))}' for label in LABELS))
        self.save.setEnabled(self.phase is None and all(len(self.samples.get(label, [])) >= 25 for label in LABELS))

    def start_capture(self):
        self.phase = LABELS[self.pose.currentIndex()]
        self.samples[self.phase] = []
        self.started = time.monotonic()
        self.last_sample = None
        self.hand_id = None
        for control in (self.profile, self.pose, self.capture, self.save):
            control.setEnabled(False)

    def tick(self):
        self.live_status.setText(self.tracker.status)
        if self.phase is None:
            return
        elapsed = time.monotonic() - self.started
        if elapsed >= 4:
            count = len(self.samples[self.phase])
            self.status.setText(f'{self.phase}: {count} 프레임 측정. ' +
                                ('다음 동작을 측정하세요.' if count >= 25 else 'Leap 수신 부족: 다시 측정하세요.'))
            if count >= 25:
                self.pose.setCurrentIndex(min(4, self.pose.currentIndex() + 1))
            self.phase = None
            for control in (self.profile, self.pose, self.capture):
                control.setEnabled(True)
            self.refresh_progress()
            return
        if elapsed < 1:
            self.status.setText('준비: ' + self.pose.currentText())
            return
        sample = self.tracker.calibration_sample()
        self.status.setText(f'{self.phase}: {4-elapsed:.1f}초 유지 / ' + self.tracker.status)
        if sample is None or sample.t < self.started + 1:
            return
        key = (sample.t, sample.hand_id, sample.frame_id)
        if key == self.last_sample:
            return
        self.last_sample = key
        try:
            _, ratios, _ = features(sample)
        except (ValueError, IndexError):
            return
        if self.hand_id is not None and self.hand_id != sample.hand_id:
            self.samples[self.phase].clear()
        self.hand_id = sample.hand_id
        self.samples.setdefault(self.phase, []).append(ratios)
        self.refresh_progress()

    def save_capture(self):
        try:
            thresholds = calculate_thresholds(self.samples)
            save_profile(self.profile.currentText(), thresholds)
        except (OSError, ValueError) as exc:
            self.status.setText(str(exc))
            return
        self.accept()

    def done(self, result):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if self.tracker is not None:
            self.tracker.close()
        super().done(result)
