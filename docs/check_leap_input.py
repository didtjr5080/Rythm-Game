"""Run from repository root: .venv311\Scripts\python.exe -m unittest docs.check_leap_input -v"""
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.leap_tracker import LeapPinchTracker
from app.input.pinch_classifier import HandSample, NAMES, PinchClassifier


def sample(finger, stamp):
    tips = [(0, 0, 0)] + [(80 + i * 30, 0, 0) for i in range(4)]
    if finger is not None:
        tips[finger + 1] = (10, 0, 0)
    return HandSample(1, stamp, 1, 'RIGHT', (0, 0, 0), 80, tips, [],
                      [[(0, 0, 0), (0, 1, 0), (0, 2, 0)]] * 5)


class LeapInputChecks(unittest.TestCase):
    def test_gameplay_never_opens_webcam_with_menu_camera_disabled(self):
        import os
        import sys
        from unittest.mock import patch
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from app.ui.main_window import MainWindow
        app = QApplication.instance() or QApplication([])
        with patch('app.config.USE_MOCK_EMG', True), patch('app.config.USE_CAMERA', False), \
                patch('cv2.VideoCapture', side_effect=AssertionError('Webcam opened')), \
                patch('app.input.mediapipe_tracker.MediaPipeHandTracker',
                      side_effect=AssertionError('MediaPipe started')):
            window = MainWindow()
            try:
                app.processEvents()
                window.show_settings_screen()
                app.processEvents()
                settings = window.centralWidget()
                self.assertTrue(settings.camera_enabled_checkbox.isVisible())
                settings.start_camera_preview()
                window.show_calibration_screen()
                app.processEvents()
                from PyQt6.QtWidgets import QDialog
                with patch('app.ui.main_window.LeapCalibrationDialog') as calibration:
                    calibration.return_value.exec.return_value = QDialog.DialogCode.Accepted
                    window.show_game_widget()
                app.processEvents()
                self.assertIsNone(window.selected_song_path)
                self.assertIsNone(window.notes_path)
                notes = window.centralWidget().engine.notes
                self.assertTrue(all((a.lane, b.lane) != (1, 2) for a, b in zip(notes, notes[1:])))
                self.assertFalse(window.centralWidget().grab().isNull())
            finally:
                window.close()

    def test_four_pinches_and_release(self):
        for finger, name in enumerate(NAMES):
            model = PinchClassifier()
            self.assertEqual(model.step(sample(finger, 1))[0], 'NONE')
            self.assertEqual(model.step(sample(finger, 1.1))[0], name)
            model.step(sample(None, 1.2))
            self.assertEqual(model.step(sample(None, 1.3))[0], 'NONE')
            self.assertEqual(model.step(None)[0], 'LOST')

    def test_worker_mapping_and_expiration(self):
        tracker = LeapPinchTracker.__new__(LeapPinchTracker)
        tracker._stop = threading.Event()
        tracker._lock = threading.Lock()
        tracker.last_error = None

        class Reader:
            def __enter__(self):
                self.index = 0
                return self

            def __exit__(self, *args):
                pass

            def poll(self, side, timeout):
                finger = self.index // 2
                stamp = 1 + finger + (self.index % 2) * .1
                tracker._snapshot = None
                self.index += 1
                if self.index == 8:
                    tracker._stop.set()
                return True, sample(finger, stamp)

        # Capture every publication before the next poll, including the final one.
        published = []
        original = tracker._lock

        class Lock:
            def __enter__(self):
                original.acquire()

            def __exit__(self, *args):
                if tracker._snapshot is not None:
                    published.append(tracker._snapshot[1]['lane'])
                original.release()

        tracker._lock = Lock()
        tracker._run(Reader)
        self.assertEqual([v for v in published if v is not None], [0, 1, 2, 3])
        tracker._lock = original
        tracker._stop.clear()
        tracker._snapshot = (time.monotonic() - 1, {'lane': 3})
        self.assertIsNone(tracker.track()['lane'])

    def test_old_chart_and_sample_stay_in_four_lanes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'chart.json'
            path.write_text(json.dumps({'lane_count': 5, 'notes': [
                {'lane': i, 'hit_time_ms': 1000 + i * 2000} for i in range(5)]}))
            engine = RhythmGameEngine.from_json_file(path)
        self.assertEqual([n.lane for n in engine.notes], [0, 1, 0, 3, 0])
        self.assertTrue(all(0 <= n.lane < 4 for n in engine.generate_sample_notes()))
