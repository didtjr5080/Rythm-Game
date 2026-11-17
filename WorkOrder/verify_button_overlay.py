"""Check native overlay isolation over styled buttons and stable camera rows."""
import os
import sys
if '--windows' not in sys.argv: os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PyQt6.QtCore import QPointF, Qt, QEvent
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QEnterEvent
from app.ui.hand_cursor import CursorRing
from app.ui.theme import APP_STYLE
app=QApplication([]); app.setStyleSheet(APP_STYLE)
root=QWidget(); row=QHBoxLayout(root)
for name in ('Settings','Start Game','View Results'):
    button=QPushButton(name)
    if name=='Start Game': button.setObjectName('primary')
    row.addWidget(button)
root.resize(900,160); root.show(); QTest.qWait(100)
ring=CursorRing(root); ring.setGeometry(root.rect())
assert ring.isWindow() and ring.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
assert ring.windowFlags() & Qt.WindowType.WindowTransparentForInput
for i in range(20):
    button=row.itemAt(i%3).widget()
    button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse,True)
    QApplication.sendEvent(button,QEnterEvent(QPointF(5,5),QPointF(5,5),QPointF(button.mapToGlobal(button.rect().center()))))
    ring.move_ring(QPointF(70,80),False); app.processEvents()
    ring.move_ring(QPointF(830,80),True); QTest.qWait(20)
    image=ring.grab().toImage()
    dpr=image.devicePixelRatio()
    assert image.pixelColor(round(70*dpr),round(80*dpr)).alpha()==0,'Previous circle remains in native alpha surface'
    assert image.pixelColor(round(830*dpr),round(80*dpr)).alpha()>0
    ring.hide(); app.processEvents()
    button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse,False)
    QApplication.sendEvent(button,QEvent(QEvent.Type.Leave))
ring.close(); root.close()
print('PASS: native click-through overlay, 20 button crossings, alpha clearing and hide')

from app import config
config.USE_CAMERA=False; config.USE_MOCK_EMG=True
from app.ui.main_window import MainWindow
window=MainWindow(); window.show_settings_screen(); window.show(); app.processEvents()
settings=window.centralWidget(); settings.stop_camera_preview()
class Video:
    status='LIVE CAMERA 0 / 1280x720'; error=''; backend_is_mediapipe=True
    diagnostic_summary='MEDIAPIPE READY / no hand'
    def set_flip(self,value): pass
    def read(self): return None
    def hand_sample(self): return None
    def close(self): pass
    release=close
video=Video(); settings.preview_source=settings.preview_tracker=video
baseline=settings.camera_status.geometry(),settings.camera_preview.geometry()
for i in range(40):
    video.error='Long diagnostic message '*30 if i%2 else ''
    settings.refresh_camera_preview(); app.processEvents()
    assert (settings.camera_status.geometry(),settings.camera_preview.geometry())==baseline
with patch.object(settings.camera_status,'setText',wraps=settings.camera_status.setText) as update:
    for _ in range(10): settings.refresh_camera_preview()
    assert update.call_count==0
window.close()
print('PASS: 40 short/long/error status transitions keep geometry; identical text is not rewritten')
