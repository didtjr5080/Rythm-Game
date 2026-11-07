"""Run with .venv311/Scripts/python.exe WorkOrder/verify_ui.py (no hardware needed)."""
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

os.environ['QT_QPA_PLATFORM']='offscreen'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor
from app import config
config.USE_CAMERA=False
config.USE_MOCK_EMG=True
from app.ui.theme import APP_STYLE,font_families
from app.ui.main_window import MainWindow
from app.ui.result_screen import ResultScreen
from app.input.input_fusion import InputFusion

app=QApplication([])
font_families()
app.setStyleSheet(APP_STYLE)
window=MainWindow()
window.resize(1280,720)
window.show()
def capture(name):
    app.processEvents()
    assert window.grab().save(str(ROOT/'WorkOrder'/f'{name}_preview.png'))
capture('lobby')
window.show_calibration_screen()
cal=window.centralWidget()
cal.slider.setValue(500)
cal.fusion.set_space_pressed(True)
cal.refresh()
assert cal.reader.threshold==500 and cal.fusion.raw_emg_value>=500
with patch('app.ui.calibration_screen.save_settings') as save:
    cal.save_calibration()
    assert save.call_args.args[0]['emg_threshold']==500
capture('calibration')
window.show_game_widget()
game=window.centralWidget()
game.timer.stop()
game.manual_lane=0
game.input_fusion.set_space_pressed(True)
game.start_time=time.monotonic()-2.5
game.game_loop()
assert game.engine.last_result=='PERFECT'
assert abs(game.input_fusion.last_timing_error_ms)<20 and game.ripples
assert Qt.Key.Key_V in game._handled_keys()
game._handle_key(Qt.Key.Key_V,True)
assert game.ar_camera
# Exercise the actual RGB image / PIP / AR paint paths without camera hardware.
import numpy as np
frame=np.zeros((240,320,3),dtype=np.uint8)
frame[:,:,1]=90
state,_=game.input_fusion.read(frame)
assert game.input_fusion.latest_frame_rgb.shape==(240,320,3)
image=QImage(320,240,QImage.Format.Format_RGB888)
image.fill(QColor('#10252c'))
game.camera_pixmap=QPixmap.fromImage(image)
game.start_time=time.monotonic()-2.6
game.game_loop()
game.camera_pixmap=QPixmap.fromImage(image)
capture('game')
start=time.perf_counter()
for _ in range(90): game.grab()
print(f'1280x720 paint average (PIP + AR): {(time.perf_counter()-start)*1000/90:.2f} ms')
game.abort_game()
with patch.object(ResultScreen,'_save_result',lambda self:setattr(self,'result_path',Path('verification_only.json'))):
    window.show_result_screen(dict(accuracy=96.8,perfect_count=384,good_count=21,miss_count=7,score=394500,max_combo=152))
capture('result')
fusion=InputFusion(use_camera=False,use_mock_emg=True)
state,frame=fusion.read()
assert not state.hand_visible and frame is None and fusion.hand_landmarks_norm is None
for i in range(180):
    game.raw_history.append(i)
assert len(game.raw_history)==120
fusion.close()
window.close()
print('PASS: four screens; mock fallback; threshold save; perfect hit; timing; ripple; V toggle; RGB/PIP/AR; bounded history')
