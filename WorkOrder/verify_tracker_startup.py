"""Verify the app imports MediaPipe before Qt and can run real Hands inference."""
import os
import sys
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
assert 'PyQt6.QtWidgets' not in sys.modules
import app.main
from app.input.mediapipe_tracker import MediaPipeHandTracker
from PyQt6.QtWidgets import QApplication
import numpy as np
app=QApplication([])
tracker=MediaPipeHandTracker()
assert tracker.available, tracker.last_error
frame=np.zeros((240,320,3),dtype=np.uint8)
result=tracker.track(frame)
assert tracker.status=='no hand',tracker.status
assert not result['hand_visible']
tracker.close()
print('PASS: app startup loaded native MediaPipe + Qt; real Hands model inference succeeded (blank frame correctly has no hand)')
