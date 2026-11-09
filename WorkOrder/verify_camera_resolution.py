"""Deterministic camera integration and high-resolution UI checks; no hardware required."""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
os.environ['QT_QPA_PLATFORM']='offscreen'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from app.input.mediapipe_tracker import preload_mediapipe
preload_mediapipe()
from app.input.camera import CameraSource
from app import config
from app.settings import load_settings, save_settings, AVAILABLE_RESOLUTIONS

class Capture:
    def __init__(self, opened): self.opened=opened; self.released=False; self.properties={}
    def isOpened(self): return self.opened
    def set(self,key,value): self.properties[key]=value; return True
    def read(self): return True,np.full((720,1280,3),64,dtype=np.uint8)
    def release(self): self.released=True

failed,working=Capture(False),Capture(True)
with patch('cv2.VideoCapture',side_effect=[failed,working]) as factory:
    with patch('app.input.camera.sys.platform','win32'):
        camera=CameraSource(dict(camera_enabled=True,camera_index=2,camera_resolution='1920x1080'))
    assert factory.call_args.args[0]==2
    assert failed.released and camera.read().shape==(720,1280,3)
    import cv2
    assert working.properties[cv2.CAP_PROP_FRAME_WIDTH]==1920
    assert '1280x720' in camera.status  # Report the actual negotiated resolution.
    camera.release(); assert working.released
with patch('cv2.VideoCapture') as factory:
    CameraSource(dict(camera_enabled=False)); factory.assert_not_called()
with tempfile.TemporaryDirectory() as folder:
    with patch('app.settings.settings_path',return_value=Path(folder)/'settings.json'):
        save_settings(dict(resolution='1920x1080',camera_enabled=True,camera_index=2,camera_resolution='1920x1080'))
        settings=load_settings()
        assert settings['camera_index']==2 and settings['resolution']=='1920x1080'
        assert settings['camera_resolution']=='1920x1080'

config.USE_CAMERA=False; config.USE_MOCK_EMG=True
from PyQt6.QtWidgets import QApplication
from app.ui.theme import APP_STYLE,font_families
from app.ui.main_window import MainWindow
from app.ui.result_screen import ResultScreen
app=QApplication([]); font_families(); app.setStyleSheet(APP_STYLE)
window=MainWindow(); window.show()
for resolution in ('1920x1080','1440x900'):
    assert resolution in AVAILABLE_RESOLUTIONS
    with patch('app.ui.main_window.load_settings',return_value=dict(load_settings(),resolution=resolution)):
        window.apply_window_settings()
    assert (window.width(),window.height())==tuple(map(int,resolution.split('x')))
    for kind in ('lobby','calibration','game','settings','result'):
        if kind=='lobby': window.show_start_screen()
        elif kind=='calibration': window.show_calibration_screen()
        elif kind=='game':
            window.show_game_widget(); game=window.centralWidget(); game.timer.stop(); game.game_loop()
        elif kind=='settings':
            game.abort_game(); window.show_settings_screen()
            screen=window.centralWidget()
            # The preview reads the same real-camera pipeline used in gameplay.
            with patch('cv2.VideoCapture',return_value=Capture(True)):
                with patch('app.ui.settings_screen.config.USE_CAMERA',True):
                    screen.start_camera_preview()
                from PyQt6.QtTest import QTest
                import time
                deadline=time.monotonic()+5
                while screen.camera_preview.pixmap() is None or screen.camera_preview.pixmap().isNull():
                    assert time.monotonic()<deadline,screen.camera_status.text()
                    QTest.qWait(20)
                assert not screen.camera_preview.pixmap().isNull()
                worker=screen.preview_source
                screen.stop_camera_preview()
                window.video_session.stop()
                worker._thread.join(2)
                assert not worker._thread.is_alive()
        else:
            with patch.object(ResultScreen,'_save_result',lambda self:setattr(self,'result_path',Path('resolution_check.json'))):
                window.show_result_screen(dict(accuracy=96.8,perfect_count=384,good_count=21,miss_count=7))
        app.processEvents()
        pixmap=window.grab()
        assert pixmap.width()==window.width() and pixmap.height()==window.height()
        assert pixmap.save(str(ROOT/'WorkOrder'/f'{kind}_{resolution}.png'))
    print('PASS: camera preview and five screens at',resolution)
window.close()
print('PASS: selected camera index, backend fallback, negotiated capture size, disabled camera, release and persisted settings')
