"""Choose one input device and its matching chart before starting playback."""
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QStyle, QStyleOptionButton, QSizePolicy

from app.ui.theme import AuroraScreen
from app.ui.profile_dialog import ProfileBar


class GameModeCard(QPushButton):
    def __init__(self, heading, image_path):
        super().__init__(heading)
        self.image_path = image_path
        self.image = QPixmap(str(image_path))
        self.setAccessibleName(heading)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(200, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet('''
            QPushButton { background: #0b2529; border: 1px solid #365458; border-radius: 18px; padding: 0; }
            QPushButton:hover, QPushButton:focus { border: 2px solid #6ee7b7; background: #103239; }
            QPushButton:pressed { background: #17434a; }
        ''')

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.isEnabled(): painter.setOpacity(.4)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ''
        self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
        image_rect = self.rect().adjusted(14, 14, -14, -84)
        if not self.image.isNull():
            scaled = self.image.scaled(image_rect.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(image_rect.x()+(image_rect.width()-scaled.width())//2,
                               image_rect.y()+(image_rect.height()-scaled.height())//2, scaled)
        font = QFont('Malgun Gothic')
        font.setPixelSize(22 if self.width() < 420 else 28)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(QColor('#f8fafc'))
        caption = self.rect().adjusted(12, self.height()-76, -12, -12)
        painter.drawText(caption, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.text())


class GameSelectionScreen(AuroraScreen):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 35, 50, 35)
        title = QLabel('게임 선택')
        title.setObjectName('title')
        title.setStyleSheet("font-family: 'Malgun Gothic'; font-size: 26px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(title)
        if getattr(main_window, 'profile_store', None) is not None:
            self.profile_bar = ProfileBar(main_window)
            outer.addWidget(self.profile_bar)
        self.camera_hint = QLabel()
        self.camera_hint.setWordWrap(True)
        self.camera_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.camera_hint)
        self.camera_status_timer = QTimer(self)
        self.camera_status_timer.timeout.connect(self.update_camera_hint)
        self.camera_status_timer.start(500)
        QTimer.singleShot(0, self.update_camera_hint)
        row = QHBoxLayout()
        row.setSpacing(24)
        self.mode_buttons = {}
        assets = Path(__file__).resolve().parents[1] / 'assets' / 'game_modes'
        for mode, heading, filename in (
            ('emg', '근전도 리듬 · 유지 게임', 'emg_rhythm_hold.png'),
            ('pinch', '핀치 리듬 게임', 'pinch_rhythm.png'),
            ('pinch_extension', '핀치 + 신전\n상위 리듬 게임', 'pinch_extension.png'),
        ):
            button = GameModeCard(heading, assets / filename)
            button.clicked.connect(lambda checked=False, selected_mode=mode: main_window.show_game_widget(selected_mode))
            self.mode_buttons[mode] = button
            row.addWidget(button, 1)
        outer.addLayout(row, 1)
        back = QPushButton('뒤로 / Back')
        back.clicked.connect(main_window.show_start_screen)
        outer.addWidget(back)
        self.refresh_profile_state()

    def refresh_profile_state(self):
        store = getattr(self.main_window, 'profile_store', None)
        if store is None: return
        unlocked = False
        try:
            profile_id, _ = store.active()
            unlocked = store.unlocked(profile_id)
        except (OSError, ValueError): pass
        button = self.mode_buttons['pinch_extension']
        button.setEnabled(unlocked)
        button.setText('핀치 + 신전\n상위 리듬 게임' if unlocked else '핀치 + 신전 / 잠김\n기본 2종 정상 완주 필요')
        button.setToolTip('선택한 프로필의 핀치·근전도 정상 완주 기록이 모두 필요합니다.')

    def update_camera_hint(self):
        source = getattr(self.main_window, '_navigation_video', None)
        if source is None:
            text = '웹캠 손 선택 꺼짐 · 설정에서 메뉴 손 커서를 켜 주세요.'
        else:
            text = '웹캠 선택: 손을 펴서 커서 이동 → 원하는 카드 위에서 주먹을 쥐면 선택됩니다.'
            error = getattr(source, 'last_error', None)
            text += '\n' + str(error or getattr(source, 'status', '카메라 준비 중'))
        self.camera_hint.setText(text)
