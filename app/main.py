import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.main_window import MainWindow
from app.ui.theme import APP_STYLE


def main() -> int:
    qt_app = QApplication(sys.argv)
    qt_app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
