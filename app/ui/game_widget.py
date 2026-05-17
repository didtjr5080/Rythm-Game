import time

from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget

from app import config
from app.analytics.game_metrics import calculate_game_metrics
from app.analytics.session_logger import SessionLogger
from app.audio.audio_player import AudioPlayer
from app.game.rhythm_game_engine import RhythmGameEngine
from app.i18n import tr
from app.input.input_fusion import GameInputState, InputFusion
from app.settings import load_settings


LANE_NAMES = ["LEFT", "CENTER", "RIGHT"]


class GameWidget(QWidget):
    def __init__(self, main_window, notes_path: str | None = None, song_path: str | None = None):
        super().__init__()
        self.main_window = main_window
        self.song_path = song_path
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings = load_settings()
        self.language = self.settings["language"]
        self.engine = RhythmGameEngine.from_json_file(notes_path) if notes_path else RhythmGameEngine()
        self.input_fusion = InputFusion(
            emg_threshold=int(self.settings["emg_threshold"]),
            camera_flip=bool(self.settings["camera_flip"]),
        )
        self.session_logger = SessionLogger()
        self.audio_player = AudioPlayer(self.song_path, volume=self.settings["music_volume"])
        self.start_time = time.monotonic()
        self.current_input = GameInputState(None, 0.0, False, False, None, None, None, time.time())
        self.camera_pixmap = None
        self.camera_debug_pixmap = None
        self.camera_flip = bool(self.settings["camera_flip"])
        self.manual_lane: int | None = None
        self.input_delays_ms: list[float] = []
        self.result_flash: str | None = None
        self.result_flash_time_ms = -9999
        self.finished = False
        self.cv2 = None
        self.capture = None
        self.back_button = QPushButton(tr("back", self.language), self)
        self.back_button.setObjectName("danger")
        self.back_button.clicked.connect(self.abort_game)
        self.back_button.setFixedSize(96, 38)
        self._open_camera()
        self.audio_player.play()
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(max(1, int(1000 / config.FPS)))

    def _open_camera(self):
        if not config.USE_CAMERA:
            return
        try:
            import cv2

            self.cv2 = cv2
            self.capture = cv2.VideoCapture(config.CAMERA_INDEX)
            if not self.capture.isOpened():
                print("Camera is not available. Keyboard lane fallback remains enabled.")
                self.capture.release()
                self.capture = None
        except Exception as exc:
            print(f"OpenCV camera setup failed: {exc}")
            self.capture = None

    def _read_camera_frame(self):
        if self.capture is None:
            return None
        try:
            ok, frame = self.capture.read()
            return frame if ok else None
        except Exception as exc:
            print(f"Camera read failed: {exc}")
            return None

    def _update_camera_pixmap(self, frame):
        if frame is None or self.cv2 is None:
            self.camera_pixmap = None
            self.camera_debug_pixmap = None
            return
        try:
            if self.camera_flip:
                frame = self.cv2.flip(frame, 1)
            rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888)
            self.camera_pixmap = QPixmap.fromImage(image.copy())
            if self.settings.get("show_camera_debug", True):
                self.camera_debug_pixmap = self.camera_pixmap.scaled(
                    240, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            else:
                self.camera_debug_pixmap = None
        except Exception:
            self.camera_pixmap = None
            self.camera_debug_pixmap = None

    def game_loop(self):
        current_time_ms = int((time.monotonic() - self.start_time) * 1000)
        raw_frame = self._read_camera_frame()
        input_state, _tracked_frame = self.input_fusion.read(raw_frame)
        if not input_state.hand_visible and self.manual_lane is not None:
            input_state.lane = self.manual_lane
            input_state.hand_visible = True
            input_state.hand_x = (self.manual_lane + 0.5) / config.LANE_COUNT
            input_state.hand_y = 0.5
        self.current_input = input_state
        self._update_camera_pixmap(raw_frame)

        result = self.engine.update(input_state, current_time_ms)
        note_index = self.engine.last_judged_note_index
        if result in {"PERFECT", "GOOD"} and 0 <= note_index < len(self.engine.notes):
            self.input_delays_ms.append(current_time_ms - self.engine.notes[note_index].hit_time_ms)
        if result:
            self.result_flash = result
            self.result_flash_time_ms = current_time_ms
        self.session_logger.log(current_time_ms, input_state, note_index, result)

        if self.engine.is_finished(current_time_ms):
            self.finish_game()
            return
        self.update()

    def finish_game(self):
        if self.finished:
            return
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
        if self.capture is not None:
            self.capture.release()
        self.input_fusion.close()
        session_paths = self.session_logger.save() if config.SAVE_SESSION_LOG else None
        metrics = calculate_game_metrics(self.engine.score_state, self.session_logger.rows, self.input_delays_ms)
        self.main_window.show_result_screen(metrics, session_paths=session_paths)

    def abort_game(self):
        if self.finished:
            return
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
        if self.capture is not None:
            self.capture.release()
        self.input_fusion.close()
        self.main_window.show_start_screen()

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus(Qt.FocusReason.OtherFocusReason)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.back_button.move(self.width() - self.back_button.width() - 18, 16)

    def eventFilter(self, watched, event):
        if self.finished:
            return False
        if event.type() == QEvent.Type.KeyPress:
            self._handle_key(event.key(), True)
            return event.key() in self._handled_keys()
        if event.type() == QEvent.Type.KeyRelease:
            self._handle_key(event.key(), False)
            return event.key() == Qt.Key.Key_Space
        return False

    @staticmethod
    def _handled_keys():
        return {
            Qt.Key.Key_Space,
            Qt.Key.Key_Escape,
            Qt.Key.Key_Left,
            Qt.Key.Key_Down,
            Qt.Key.Key_Right,
            Qt.Key.Key_A,
            Qt.Key.Key_S,
            Qt.Key.Key_D,
            Qt.Key.Key_F,
        }

    def keyPressEvent(self, event):
        self._handle_key(event.key(), True)

    def keyReleaseEvent(self, event):
        self._handle_key(event.key(), False)

    def _handle_key(self, key, pressed: bool):
        if key == Qt.Key.Key_Escape and pressed:
            self.finish_game()
            return
        if key == Qt.Key.Key_Space:
            self.input_fusion.set_space_pressed(pressed)
        elif not pressed:
            return
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.manual_lane = 0
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.manual_lane = 1
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.manual_lane = 2
        elif key == Qt.Key.Key_F:
            self.camera_flip = not self.camera_flip
            self.input_fusion.set_camera_flip(self.camera_flip)
            print(f"Camera flip set to {self.camera_flip}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#101216"))
        width = self.width()
        height = self.height()
        lane_width = width / config.LANE_COUNT
        judge_y = height * float(self.settings["judgement_line_y_ratio"])

        if self.camera_pixmap is not None:
            scaled_camera = self.camera_pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            x = int((width - scaled_camera.width()) / 2)
            y = int((height - scaled_camera.height()) / 2)
            painter.drawPixmap(x, y, scaled_camera)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 85))

        painter.setFont(QFont("Arial", 13))
        for lane in range(config.LANE_COUNT):
            x = lane * lane_width
            color = QColor(24, 30, 38, 95) if lane % 2 == 0 else QColor(12, 17, 24, 95)
            if self.current_input.lane == lane and self.current_input.hand_visible:
                color = QColor(31, 102, 140, 120)
            painter.fillRect(QRectF(x, 0, lane_width - 2, height), color)
            painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
            painter.drawLine(int(x), 0, int(x), height)
            painter.setPen(QColor("#d8dde6"))
            painter.drawText(QRectF(x, 16, lane_width, 32), Qt.AlignmentFlag.AlignCenter, LANE_NAMES[lane])

        painter.setPen(QPen(QColor("#f2c94c"), 4))
        painter.drawLine(0, int(judge_y), width, int(judge_y))

        current_time_ms = int((time.monotonic() - self.start_time) * 1000)
        for note, y in self.engine.visible_notes(
            current_time_ms,
            height,
            note_speed=int(self.settings["note_speed"]),
            judgement_line_y_ratio=float(self.settings["judgement_line_y_ratio"]),
        ):
            note_x = note.lane * lane_width + lane_width * 0.18
            note_rect = QRectF(note_x, y - 18, lane_width * 0.64, 36)
            painter.setBrush(QColor("#4fd1c5"))
            painter.setPen(QPen(QColor("#e6fffb"), 2))
            painter.drawRoundedRect(note_rect, 6, 6)

        if self.settings.get("show_judgement_text", True):
            self._draw_judgement_flash(painter, current_time_ms)
        self._draw_score_overlay(painter)
        if self.settings.get("show_game_hud", True):
            self._draw_hud(painter)

    def _draw_judgement_flash(self, painter: QPainter, current_time_ms: int):
        if not self.result_flash:
            return
        age = current_time_ms - self.result_flash_time_ms
        if age > 650:
            return
        alpha = max(0, 255 - int(age / 650 * 255))
        center_y = self.height() * 0.46
        colors = {
            "PERFECT": QColor("#63f7dd"),
            "GOOD": QColor("#f7d95e"),
            "MISS": QColor("#ff5f77"),
        }
        color = colors.get(self.result_flash, QColor("#ffffff"))
        color.setAlpha(alpha)
        painter.setFont(QFont("Arial", 42, QFont.Weight.Black))
        painter.setPen(color)
        painter.drawText(
            QRectF(0, center_y - 54, self.width(), 90),
            Qt.AlignmentFlag.AlignCenter,
            self.result_flash,
        )

    def _draw_score_overlay(self, painter: QPainter):
        score = self.engine.score_state
        painter.setFont(QFont("Arial", 22, QFont.Weight.Black))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(18, 16, 260, 36), Qt.AlignmentFlag.AlignLeft, f"{score.score:07d}")
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QColor("#b9c5d8"))
        painter.drawText(QRectF(20, 50, 260, 28), Qt.AlignmentFlag.AlignLeft, f"COMBO {score.combo}")

    def _draw_hud(self, painter: QPainter):
        score = self.engine.score_state
        state = self.current_input
        lane_name = LANE_NAMES[state.lane] if state.lane is not None else "NONE"
        hud_lines = [
            f"score: {score.score}",
            f"combo: {score.combo}",
            f"last: {self.engine.last_result or '-'}",
            f"hand visible: {state.hand_visible}",
            f"finger number: {state.finger_count if state.finger_count is not None else '-'}",
            f"hand lane: {lane_name}",
            f"EMG value: {state.emg_value:.0f}",
            f"EMG threshold: {int(self.settings['emg_threshold'])}",
            f"EMG activated: {state.emg_activated}",
            f"camera flip: {self.camera_flip} (F)",
            f"audio: {'selected' if self.song_path else 'none'}",
            "Finger lane: 1=LEFT 2=CENTER 3=RIGHT",
            "MOCK EMG MODE: SPACE",
            "Lane fallback: A/S/D or Left/Down/Right",
        ]
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor("#f5f7fb"))
        x = 20
        y = 88
        for line in hud_lines:
            painter.drawText(QPointF(x, y), line)
            y += 24
        if self.camera_debug_pixmap is not None:
            painter.drawPixmap(self.width() - self.camera_debug_pixmap.width() - 20, 52, self.camera_debug_pixmap)

    def closeEvent(self, event):
        self.audio_player.stop()
        if self.capture is not None:
            self.capture.release()
        self.input_fusion.close()
        super().closeEvent(event)
