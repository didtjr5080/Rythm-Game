from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from app import config
from app.audio.note_generator_adapter import find_saved_notes_for_song
from app.settings import load_settings
from app.ui.calibration_screen import CalibrationScreen
from app.ui.game_widget import GameWidget
from app.ui.result_screen import ResultScreen
from app.ui.results_browser_screen import ResultsBrowserScreen
from app.ui.settings_screen import SettingsScreen
from app.ui.start_screen import StartScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_song_path: str | None = None
        self.notes_path: str | None = None
        self.setWindowTitle(config.PROJECT_NAME)
        self.apply_window_settings()
        self.show_start_screen()

    def apply_window_settings(self):
        settings = load_settings()
        width, height = (int(part) for part in settings["resolution"].split("x", 1))
        mode = settings["window_mode"]
        self.hide()
        if mode == "borderless":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
            self.resize(width, height)
            self.show()
        else:
            self.setWindowFlags(Qt.WindowType.Window)
            self.resize(width, height)
            if mode == "fullscreen":
                self.showFullScreen()
            else:
                self.show()

    def _release_current_inputs(self):
        current=self.centralWidget()
        if current is None: return
        bio=getattr(current,'bio',None)
        if bio is not None and hasattr(bio,'stop_live'): bio.stop_live()
        if isinstance(current,CalibrationScreen): current.stop()
        if isinstance(current,SettingsScreen): current.stop_camera_preview()

    def closeEvent(self,event):
        self._release_current_inputs()
        current=self.centralWidget()
        if isinstance(current,GameWidget): current.close()
        super().closeEvent(event)

    def show_start_screen(self):
        self._release_current_inputs()
        self.setCentralWidget(StartScreen(self))

    def show_calibration_screen(self):
        self._release_current_inputs()
        self.setCentralWidget(CalibrationScreen(self))

    def show_settings_screen(self):
        self._release_current_inputs()
        self.setCentralWidget(SettingsScreen(self))

    def show_results_browser_screen(self):
        self._release_current_inputs()
        self.setCentralWidget(ResultsBrowserScreen(self))

    def show_game_widget(self):
        self._release_current_inputs()
        if self.selected_song_path and not self.notes_path:
            saved_notes = find_saved_notes_for_song(self.selected_song_path)
            if saved_notes:
                self.notes_path = str(saved_notes)
        self.setCentralWidget(GameWidget(self, notes_path=self.notes_path, song_path=self.selected_song_path))

    def show_result_screen(self, metrics: dict, session_paths: tuple | None = None):
        self.setCentralWidget(ResultScreen(self, metrics, session_paths=session_paths))
