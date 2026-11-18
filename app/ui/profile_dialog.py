"""Profile controls shared by the main and game selection screens."""
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                            QLabel, QPushButton, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt


class ProfileBar(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel('플레이어'))
        self.combo = QComboBox(); self.combo.setMinimumWidth(180)
        self.combo.currentIndexChanged.connect(self.select)
        row.addWidget(self.combo)
        self.status = QLabel(); self.status.setTextFormat(Qt.TextFormat.PlainText); self.status.setWordWrap(True); row.addWidget(self.status, 1)
        manage = QPushButton('프로필 추가 · 삭제 · 보정 관리')
        manage.clicked.connect(owner.show_profile_dialog)
        row.addWidget(manage)
        self.refresh()

    def refresh(self):
        store = getattr(self.owner, 'profile_store', None)
        if store is None: self.hide(); return
        try:
            data = store.load()
            self.combo.blockSignals(True)
            self.combo.clear(); self.combo.addItem('선택 안 함 / 연습', None)
            for key, person in data['profiles'].items(): self.combo.addItem(person['name'], key)
            self.combo.setCurrentIndex(max(0, self.combo.findData(data['active'])))
            self.combo.blockSignals(False)
            person = data['profiles'].get(data['active'])
            self.status.setText(('핀치 ' + ('완료' if person['completed']['pinch'] else '미완료')
                                 + ' / 근전도 ' + ('완료' if person['completed']['emg'] else '미완료'))
                                if person else '연습: 보정·완료 이력 저장 안 함 / 상위 모드 잠김')
        except (OSError, ValueError) as exc:
            self.combo.blockSignals(False)
            self.status.setText('프로필 읽기 실패: ' + str(exc))

    def select(self):
        try:
            self.owner.profile_store.select(self.combo.currentData())
            self.refresh()
            screen = self.owner.centralWidget()
            if hasattr(screen, 'refresh_profile_state'): screen.refresh_profile_state()
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, '프로필 오류', str(exc))


class ProfileDialog(QDialog):
    def __init__(self, owner):
        super().__init__(owner)
        self.store = owner.profile_store
        self.setWindowTitle('플레이어 프로필')
        self.resize(620, 360)
        layout = QVBoxLayout(self)
        self.combo = QComboBox(); self.combo.currentIndexChanged.connect(self.describe)
        layout.addWidget(self.combo)
        self.status = QLabel(); self.status.setTextFormat(Qt.TextFormat.PlainText); self.status.setWordWrap(True); layout.addWidget(self.status)
        row = QHBoxLayout()
        self.name = QLineEdit(); self.name.setPlaceholderText('새 플레이어 이름')
        row.addWidget(self.name)
        add = QPushButton('프로필 만들기'); add.clicked.connect(self.create); row.addWidget(add)
        layout.addLayout(row)
        row = QHBoxLayout()
        for label, mode in (('핀치 보정값 지우기 · 재보정', 'pinch'), ('근전도 기준 지우기 · 재측정', 'emg')):
            button = QPushButton(label); button.clicked.connect(lambda checked=False, m=mode:self.clear(m)); row.addWidget(button)
        layout.addLayout(row)
        delete = QPushButton('선택 프로필 삭제'); delete.setObjectName('danger'); delete.clicked.connect(self.delete)
        layout.addWidget(delete)
        use = QPushButton('선택하고 닫기'); use.clicked.connect(self.use); layout.addWidget(use)
        close = QPushButton('닫기'); close.clicked.connect(self.reject); layout.addWidget(close)
        self.refresh()

    def refresh(self):
        try:
            data = self.store.load()
            self.combo.blockSignals(True); self.combo.clear()
            for key, person in data['profiles'].items(): self.combo.addItem(person['name'], key)
            self.combo.setCurrentIndex(max(0, self.combo.findData(data['active'])))
            self.combo.blockSignals(False); self.describe()
        except (OSError, ValueError) as exc: self.status.setText(str(exc))

    def describe(self):
        try:
            person = self.store.get(self.combo.currentData())
            if not person: self.status.setText('프로필을 만들어 보정값과 완료 이력을 저장하세요.'); return
            pinch = '저장됨' if person['pinch'] else '없음'
            emg = f"{person['emg']['minimum']:.4f}" if person['emg'] else '없음'
            self.status.setText(f"핀치 보정: {pinch} / 근전도 최저값: {emg}\n"
                                f"핀치 완료: {person['completed']['pinch']} / 근전도 완료: {person['completed']['emg']}\n"
                                '두 기본 모드를 정상 완주하면 상위 모드가 열립니다.\n'
                                '보정값을 지우면 해당 모드의 완료 이력도 초기화됩니다.')
        except (OSError, ValueError) as exc: self.status.setText(str(exc))

    def create(self):
        try: self.store.create(self.name.text()); self.name.clear(); self.refresh()
        except (OSError, ValueError) as exc: self.status.setText(str(exc))

    def use(self):
        try:
            if self.combo.currentData() is None: return
            self.store.select(self.combo.currentData()); self.accept()
        except (OSError, ValueError) as exc: self.status.setText(str(exc))

    def clear(self, mode):
        try:
            if self.combo.currentData() is None: return
            self.store.clear_calibration(self.combo.currentData(), mode); self.describe()
        except (OSError, ValueError) as exc: self.status.setText(str(exc))

    def delete(self):
        key = self.combo.currentData()
        if key is None: return
        if QMessageBox.question(self, '프로필 삭제', '선택한 사람의 보정값과 완료 이력을 삭제할까요?\n기존 결과 기록은 유지됩니다.') != QMessageBox.StandardButton.Yes: return
        try: self.store.delete(key); self.refresh()
        except (OSError, ValueError) as exc: self.status.setText(str(exc))
