"""Regression: closing/opening DirectShow graphs must never overlap on page changes."""
import os
import sys
import threading
from pathlib import Path
from unittest.mock import patch

os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from PyQt6.QtCore import QPointF
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QPushButton, QScrollArea
from app.input.live_video import LiveVideoWorker
from app.input.video_session import VideoSession

entered=threading.Event(); resume=threading.Event(); opened_second=threading.Event(); released=threading.Event()

class SlowCamera:
    capture=True
    status='FAKE CAMERA'
    def __init__(self, settings): pass
    def read(self):
        entered.set()
        assert resume.wait(3)
        return np.zeros((40,60,3),dtype=np.uint8)
    def release(self): released.set()

class NextCamera:
    capture=True
    status='NEXT CAMERA'
    def __init__(self, settings):
        assert released.is_set(), 'Old native camera still owns its graph'
        opened_second.set()
    def read(self): return np.zeros((40,60,3),dtype=np.uint8)
    def release(self): pass

class Tracker:
    diagnostic_summary='FAKE';backend_is_mediapipe=True;last_error=None
    def __init__(self,flip): self.flip=flip
    def set_flip(self,flip): self.flip=flip
    def track(self,frame): return dict(hand_visible=False,frame=frame)
    def close(self): pass

a=LiveVideoWorker(dict(camera_enabled=True),camera_factory=SlowCamera,tracker_factory=Tracker)
b=None
try:
    assert entered.wait(2)
    a.close()
    b=LiveVideoWorker(dict(camera_enabled=True),camera_factory=NextCamera,tracker_factory=Tracker)
    assert not opened_second.wait(.12)
    resume.set()
    assert opened_second.wait(2)
finally:
    resume.set();a.close();a._thread.join(2)
    if b is not None:b.close();b._thread.join(2)
assert not a._thread.is_alive() and not b._thread.is_alive()
print('PASS: new native capture waits until previous capture releases; GUI close stays nonblocking')

app=QApplication([])
created=[]
class Worker:
    capture=None;_thread=None;last_error=None;error='';status='FAKE';diagnostic_summary='FAKE';backend_is_mediapipe=True
    def __init__(self,settings,enabled=True):
        self.closes=0;created.append(self)
    def set_flip(self,flip): self.flip=flip
    def read(self): return None
    def track(self,frame):return dict(hand_visible=False,frame=None)
    def hand_sample(self): return None
    def close(self):self.closes+=1

pool=VideoSession(worker_factory=Worker)
x=pool.acquire({});worker=x._worker;x.close();x.close()
y=pool.acquire({})
assert y._worker is worker and worker.closes==0 and x.read() is None
y.close();QTest.qWait(pool.IDLE_MS+30)
assert worker.closes==1
pool.stop()
assert worker.closes==1
print('PASS: shared worker reuse, idempotent leases, idle release and no double native close')

from app import config
config.USE_CAMERA=True;config.USE_MOCK_EMG=True
from app.i18n import tr
from app.ui.main_window import MainWindow
from app.ui.settings_screen import SettingsScreen
from app.ui.start_screen import StartScreen
from app.settings import load_settings
before=len(created)
with patch('app.input.video_session.LiveVideoWorker',Worker):
    window=MainWindow();window.activateWindow();app.processEvents();QTest.qWait(20)
    worker=window.centralWidget().bio.camera_source._worker
    for _ in range(20):
        cursor=window.hand_cursor;cursor.timer.stop()
        screen=window.centralWidget()
        button=next(b for b in screen.findChildren(QPushButton) if b.text()==tr('settings',screen.language))
        cursor.position=QPointF(button.mapTo(screen,button.rect().center()))
        cursor._move(cursor.position)
        cursor._click(cursor.position)
        assert window.centralWidget() is screen, 'Page was destroyed inside mouse release'
        app.processEvents();QTest.qWait(20)
        settings=window.centralWidget()
        assert isinstance(settings,SettingsScreen)
        assert settings.preview_source._worker is worker
        cursor.timer.stop()
        back=next(b for b in settings.findChildren(QPushButton) if b.text()==tr('back',settings.language))
        settings.findChild(QScrollArea).ensureWidgetVisible(back);app.processEvents();QTest.qWait(20)
        cursor.position=QPointF(back.mapTo(settings,back.rect().center()))
        cursor._move(cursor.position);cursor._click(cursor.position)
        assert window.centralWidget() is settings
        app.processEvents();QTest.qWait(20)
        assert window.centralWidget().bio.camera_source._worker is worker
        assert worker.closes==0
    assert len(created)==before+1
    for mode,resolution in (('windowed','1440x900'),('borderless','1920x1080')):
        window.show_settings_screen();window.activateWindow();QTest.qWait(30)
        QApplication.setActiveWindow(window)  # Offscreen plugin has no native focus restoration.
        screen=window.centralWidget();cursor=window.hand_cursor;cursor.timer.stop()
        save=next(b for b in screen.findChildren(QPushButton) if b.text()==tr('save',screen.language))
        screen.findChild(QScrollArea).ensureWidgetVisible(save);QTest.qWait(20)
        cursor.position=QPointF(save.mapTo(screen,save.rect().center()))
        with patch('app.ui.settings_screen.save_settings') as stored, patch('app.ui.main_window.load_settings',return_value=dict(load_settings(),window_mode=mode,resolution=resolution)):
            cursor._click(cursor.position)
            assert not stored.called
            QTest.qWait(100)
            assert stored.called and isinstance(window.centralWidget(),StartScreen)
            assert window.centralWidget().bio.camera_source._worker is worker
    window.close()
    assert worker.closes==1
print('PASS: 20 hand-click main/settings round trips reuse one capture; deferred Back/Save including mode/resolution changes; clean final release')
