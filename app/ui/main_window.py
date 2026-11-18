from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QMainWindow, QMessageBox
import logging

from app import config
from app.audio.note_generator_adapter import find_saved_notes_for_song
from app.settings import load_settings
from app.ui.calibration_screen import CalibrationScreen
from app.ui.game_widget import GameWidget
from app.ui.result_screen import ResultScreen
from app.ui.results_browser_screen import ResultsBrowserScreen
from app.ui.settings_screen import SettingsScreen
from app.ui.start_screen import StartScreen
from app.ui.game_selection_screen import GameSelectionScreen
from app.ui.hand_cursor import HandCursorController
from app.ui.leap_calibration_dialog import LeapCalibrationDialog
from app.input.video_session import VideoSession
from app.input.emg_session import EMGSession
from app.player_profiles import ProfileStore
from app.ui.profile_dialog import ProfileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_session = VideoSession(self)
        self.emg_session = EMGSession(self)
        self._navigation_video = None
        self.selected_song_path: str | None = None
        self.notes_path: str | None = None
        self.game_mode = 'pinch'
        self.profile_store = ProfileStore()
        self.setWindowTitle(config.PROJECT_NAME)
        self.apply_window_settings()
        self.hand_cursor = HandCursorController(self)
        self.show_start_screen()

    def setCentralWidget(self, widget):
        if hasattr(self, 'hand_cursor'): self.hand_cursor.detach()
        if self._navigation_video is not None:
            self._navigation_video.close()
            self._navigation_video = None
        super().setCentralWidget(widget)
        if not hasattr(self, 'hand_cursor'): return
        self._attach_navigation_camera()

    def _attach_navigation_camera(self):
        screen = self.centralWidget()
        if not isinstance(screen, (StartScreen, GameSelectionScreen, SettingsScreen, ResultScreen, ResultsBrowserScreen)):
            return
        settings = load_settings()
        if config.USE_CAMERA and settings['camera_enabled']:
            self._navigation_video = self.video_session.acquire(settings, enabled=True)
            self.hand_cursor.attach(screen, lambda: self._navigation_video)

    def apply_window_settings(self):
        was_active = self.isActiveWindow()
        settings = load_settings()
        width, height = (int(part) for part in settings["resolution"].split("x", 1))
        mode = settings["window_mode"]
        display = (mode, settings['resolution'])
        previous = getattr(self, '_applied_display', None)
        if previous == display:
            return
        self._applied_display = display
        available = self.screen().availableGeometry()
        width = min(width, available.width())
        height = min(height, max(1, available.height()-40))
        flags = Qt.WindowType.Window
        if mode == 'borderless': flags |= Qt.WindowType.FramelessWindowHint
        if self.windowFlags() != flags:
            self.setWindowFlags(flags)
        self.showNormal()
        self.resize(width, height)
        if mode == 'fullscreen': self.showFullScreen()
        else: self.show()
        if was_active: self.activateWindow()
        logging.getLogger(__name__).info('Display requested=%s actual=%sx%s available=%sx%s dpr=%s state=%s',display,self.width(),self.height(),available.width(),available.height(),self.devicePixelRatioF(),self.windowState())

    def _release_current_inputs(self):
        if hasattr(self, 'hand_cursor'):
            self.hand_cursor.detach()
        if self._navigation_video is not None:
            self._navigation_video.close()
            self._navigation_video = None
        current=self.centralWidget()
        if current is None: return
        bio=getattr(current,'bio',None)
        if bio is not None and hasattr(bio,'stop_live'): bio.stop_live()
        if isinstance(current,CalibrationScreen): current.stop()
        if isinstance(current,SettingsScreen):
            current.stop_emg_test(); current.device_timer.stop(); current.stop_camera_preview()

    def closeEvent(self,event):
        self.hand_cursor.detach()
        self._release_current_inputs()
        current=self.centralWidget()
        if isinstance(current,GameWidget): current.close()
        self.video_session.shutdown()
        self.emg_session.shutdown()
        super().closeEvent(event)

    def show_start_screen(self):
        if self._defer_hand_navigation(self.show_start_screen): return
        self._release_current_inputs()
        self.setCentralWidget(StartScreen(self))

    def show_calibration_screen(self):
        self.show_settings_screen()

    def show_settings_screen(self):
        if self._defer_hand_navigation(self.show_settings_screen): return
        self._release_current_inputs()
        self.setCentralWidget(SettingsScreen(self))

    def show_results_browser_screen(self):
        if self._defer_hand_navigation(self.show_results_browser_screen): return
        self._release_current_inputs()
        self.setCentralWidget(ResultsBrowserScreen(self))

    def show_game_selection(self):
        if self._defer_hand_navigation(self.show_game_selection): return
        if self.selected_song_path and not self._ensure_song_notes(self.show_game_selection): return
        self._release_current_inputs()
        self.setCentralWidget(GameSelectionScreen(self))

    def _ensure_song_notes(self, on_ready):
        saved = find_saved_notes_for_song(self.selected_song_path)
        self.notes_path = str(saved) if saved else None
        if saved is not None:
            return True
        if not isinstance(self.centralWidget(), StartScreen):
            self.show_start_screen()
        self.centralWidget().generate_notes(on_ready=on_ready)
        return False

    def show_game_widget(self, game_mode=None):
        mode = self.game_mode if game_mode is None else game_mode
        if mode not in ('pinch', 'emg', 'pinch_extension'):
            raise ValueError('Unknown game mode.')
        if self._defer_hand_navigation(lambda: self.show_game_widget(mode)): return
        store = getattr(self, 'profile_store', None)
        profile_id, person = (None, None)
        if store is not None:
            try:
                profile_id, person = store.active()
                if mode == 'pinch_extension' and not store.unlocked(profile_id):
                    QMessageBox.warning(self, '상위 모드 잠김', '같은 프로필로 핀치와 근전도 게임을 모두 정상 완주하세요.')
                    return
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, '프로필 오류', str(exc))
                return
        if self.selected_song_path and not self._ensure_song_notes(lambda: self.show_game_widget(mode)): return
        self._release_current_inputs()
        if self.notes_path:
            from app.game.rhythm_game_engine import RhythmGameEngine
            try: RhythmGameEngine.from_json_file(self.notes_path, mode=mode)
            except (OSError, ValueError, TypeError, AttributeError, OverflowError) as exc:
                self.show_start_screen()
                QMessageBox.warning(self,'Chart unavailable',f'{exc}\nGenerate Notes again, then retry.')
                return
        video = getattr(self, 'video_session', None)
        if video is not None:
            video.stop()
            if not video.is_stopped:
                ticket = self._pending_game_start = object()
                screen = self.centralWidget()
                def retry_after_camera_close():
                    if (getattr(self, '_pending_game_start', None) is ticket
                            and self.centralWidget() is screen and self.isVisible()):
                        self.show_game_widget(mode)
                QTimer.singleShot(30, retry_after_camera_close)
                return
        self._pending_game_start = None
        guest_thresholds = None
        if mode in ('pinch', 'pinch_extension') and not (person and person['pinch']):
            dialog = (LeapCalibrationDialog(self, player_profile=person or {'name': '연습', 'pinch': None})
                      if store is not None else LeapCalibrationDialog(self))
            try:
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    self._attach_navigation_camera()
                    return
                if person is not None:
                    try:
                        store.save_pinch(profile_id, dialog.calibrated_thresholds)
                    except (OSError, ValueError) as exc:
                        QMessageBox.warning(self, '보정 저장 실패', str(exc))
                        self._attach_navigation_camera()
                        return
                elif store is not None and isinstance(dialog.calibrated_thresholds, dict):
                    guest_thresholds = dialog.calibrated_thresholds
            finally:
                dialog.deleteLater()
        options = {'profile_id': profile_id} if store is not None else {}
        if guest_thresholds is not None: options['guest_leap_thresholds'] = guest_thresholds
        try:
            game = GameWidget(self, notes_path=self.notes_path, song_path=self.selected_song_path,
                              mode=mode, **options)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, '게임 준비 실패', str(exc))
            self._attach_navigation_camera()
            return
        self.game_mode = mode
        self.setCentralWidget(game)

    def show_profile_dialog(self):
        if self._defer_hand_navigation(self.show_profile_dialog): return
        dialog = ProfileDialog(self)
        try: dialog.exec()
        finally: dialog.deleteLater()
        screen = self.centralWidget()
        if hasattr(screen, 'profile_bar'): screen.profile_bar.refresh()
        if hasattr(screen, 'refresh_profile_state'): screen.refresh_profile_state()

    def _defer_hand_navigation(self, callback):
        cursor = getattr(self, 'hand_cursor', None)
        if cursor is not None and cursor._dispatching:
            screen = self.centralWidget()
            def navigate_after_release():
                if self.isVisible() and self.centralWidget() is screen and cursor._can_control():
                    callback()
            QTimer.singleShot(0, navigate_after_release)
            return True
        return False

    def show_result_screen(self, metrics: dict, session_paths: tuple | None = None):
        if self._defer_hand_navigation(lambda: self.show_result_screen(metrics, session_paths)): return
        self._release_current_inputs()
        self.setCentralWidget(ResultScreen(self, metrics, session_paths=session_paths))
