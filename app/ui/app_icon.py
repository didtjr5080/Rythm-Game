"""Application identity shared by source runs and the portable executable."""
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon

ICON_PATH=Path(__file__).resolve().parents[1]/'assets'/'app.ico'


def set_windows_app_id():
    if sys.platform=='win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('EMGMotionRhythm.SonicLab')


def apply_app_icon(application):
    icon=QIcon(str(ICON_PATH))
    application.setWindowIcon(icon)
    return icon
