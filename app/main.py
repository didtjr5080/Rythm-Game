import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# MediaPipe must load before PyQt's native DLLs on Windows.
from app.input.mediapipe_tracker import preload_mediapipe
preload_mediapipe()

from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.ui.theme import APP_STYLE, font_families
from app.ui.app_icon import apply_app_icon, set_windows_app_id


def main() -> int:
    if '--self-test' in sys.argv:
        from app.diagnostics import run_self_test
        index = sys.argv.index('--self-test')
        output = sys.argv[index+1] if len(sys.argv)>index+1 else 'self-test.json'
        return run_self_test(output)
    set_windows_app_id()
    qt_app = QApplication(sys.argv)
    apply_app_icon(qt_app)
    font_families()
    qt_app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
