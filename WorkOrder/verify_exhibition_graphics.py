"""Deterministic backing-store and real Save-path regressions."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PyQt6.QtCore import QPointF, QRect
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor
from app.ui.hand_cursor import CursorRing
from app import config
from app.settings import save_settings

app=QApplication([])
class Background(QWidget):
    def paintEvent(self,event):
        p=QPainter(self)
        p.fillRect(self.rect(),QColor('#123456'))
        p.fillRect(QRect(10,10,180,180),QColor('#abcdef'))

root=Background(); root.resize(640,400); root.show(); app.processEvents()
baseline=root.grab().toImage()
ring=CursorRing(root); ring.setGeometry(root.rect())
for i in range(20):
    for point,scroll,pending in [(QPointF(60,60),False,False),(QPointF(610,80),True,False),(QPointF(300,200),False,True)]:
        ring.move_ring(point,scroll,pending); app.processEvents()
    ring.hide(); app.processEvents()
    assert root.grab().toImage()==baseline, 'Cursor pixels were not restored'
root.resize(700,430); ring.setGeometry(root.rect()); app.processEvents()
baseline=root.grab().toImage(); ring.move_ring(QPointF(675,200),True); app.processEvents()
ring.hide(); app.processEvents(); assert root.grab().toImage()==baseline
root.close()
print('PASS: 20 cursor A/B/SCROLL/pending/hide cycles and resized edge restore background pixels')

config.USE_CAMERA=False; config.USE_MOCK_EMG=True
from app.ui.main_window import MainWindow
from app.ui.start_screen import StartScreen
with tempfile.TemporaryDirectory() as tmp, patch('app.settings.settings_path',return_value=Path(tmp)/'settings.json'):
    save_settings(dict(window_mode='windowed',resolution='800x600',camera_enabled=False,emg_input_mode='mock'))
    window=MainWindow(); window.show(); app.processEvents()
    window.resize(810,610); window.move(30,40); app.processEvents()
    for kind in ('unchanged','volume','camera'):
        for _ in range(5):
            geometry=window.geometry()
            window.show_settings_screen(); app.processEvents(); settings=window.centralWidget()
            if kind=='volume': settings.volume_slider.setValue(40)
            if kind=='camera': settings.camera_resolution_combo.setCurrentText('640x480')
            settings.save_and_back()
            assert isinstance(window.centralWidget(),StartScreen)
            window.grab(); app.processEvents()
            assert window.geometry()==geometry,(kind,geometry,window.geometry())
            assert window.hand_cursor.overlay.geometry()==window.centralWidget().rect()
    window.close()
print('PASS: actual Save path, 15 unchanged/volume/camera saves preserve geometry and pointer bounds')

# A split-color source proves mirror direction and full-frame aspect fit.
import numpy as np
import cv2
from app.ui.game_widget import GameWidget
from app.input.camera import draw_camera_frame
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QRectF
frame=np.zeros((120,240,3),dtype=np.uint8)
frame[:,:120,2]=255; frame[:,120:,0]=255
fake=type('Display',(),{})()
fake.ar_camera=True; fake.settings={}; fake.cv2=cv2
for flip in (False,True,False):
    fake.camera_flip=flip
    GameWidget._update_camera_pixmap(fake,frame)
    image=fake.camera_pixmap.toImage()
    assert image.pixelColor(20,20)==QColor('blue' if flip else 'red')
    canvas=QImage(300,300,QImage.Format.Format_RGB888); canvas.fill(QColor('black'))
    painter=QPainter(canvas)
    bounds=draw_camera_frame(painter,QRectF(0,0,300,300),fake.camera_pixmap); painter.end()
    assert bounds==QRectF(0,75,300,150)
GameWidget._update_camera_pixmap(fake,None)
assert fake.camera_pixmap is None
fake.settings={'show_game_hud':True,'show_camera_debug':False}; fake.ar_camera=False
GameWidget._update_camera_pixmap(fake,frame)
assert fake.camera_pixmap is None
print('PASS: asymmetric synthetic video mirror roundtrip, aspect fit, frame loss and hidden conversion')
