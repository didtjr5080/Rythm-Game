"""Choose one input device and its matching chart before starting playback."""
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QStyle, QStyleOptionButton, QSizePolicy

from app.ui.theme import AuroraScreen


class GameModeCard(QPushButton):
    def __init__(self, heading, image_path):
        super().__init__(heading)
        self.image_path = image_path
        self.image = QPixmap(str(image_path))
        self.setAccessibleName(heading)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(240, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet('''
            QPushButton { background: #0b2529; border: 1px solid #365458; border-radius: 18px; padding: 0; }
            QPushButton:hover, QPushButton:focus { border: 2px solid #6ee7b7; background: #103239; }
            QPushButton:pressed { background: #17434a; }
        ''')

    def paintEvent(self, event):
        painter = QPainter(self)
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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 35, 50, 35)
        title = QLabel('게임 선택')
        title.setObjectName('title')
        title.setStyleSheet("font-family: 'Malgun Gothic'; font-size: 26px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(title)
        row = QHBoxLayout()
        row.setSpacing(24)
        self.mode_buttons = {}
        assets = Path(__file__).resolve().parents[1] / 'assets' / 'game_modes'
        for mode, heading, filename in (
            ('emg', '근전도 리듬 · 유지 게임', 'emg_rhythm_hold.png'),
            ('pinch', '핀치 리듬 게임', 'pinch_rhythm.png'),
        ):
            button = GameModeCard(heading, assets / filename)
            button.clicked.connect(lambda checked=False, selected_mode=mode: main_window.show_game_widget(selected_mode))
            self.mode_buttons[mode] = button
            row.addWidget(button, 1)
        outer.addLayout(row, 1)
        back = QPushButton('뒤로 / Back')
        back.clicked.connect(main_window.show_start_screen)
        outer.addWidget(back)
