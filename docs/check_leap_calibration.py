"""python -m unittest docs.check_leap_calibration -v"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.input.leap_calibration import (
    LABELS, activate_profile, calculate_thresholds, load_profiles, save_profile,
)
from app.input.pinch_classifier import NAMES, PinchClassifier


def measurements():
    samples = {'NONE': [[1.] * 4 for _ in range(30)]}
    for i, name in enumerate(NAMES):
        row = [1.] * 4
        row[i] = .2
        samples[name] = [list(row) for _ in range(30)]
    return samples


class LeapCalibrationChecks(unittest.TestCase):
    def test_thresholds_and_incomplete_measurements(self):
        samples = measurements()
        self.assertEqual(calculate_thresholds(samples), dict.fromkeys(NAMES, .52))
        samples['INDEX'] = [[1.] * 4 for _ in range(30)]
        with self.assertRaisesRegex(ValueError, 'too similar'):
            calculate_thresholds(samples)
        samples['INDEX'] = []
        with self.assertRaisesRegex(ValueError, '25 fresh'):
            calculate_thresholds(samples)

    def test_profiles_validation_and_atomic_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'profiles.json'
            first = dict.fromkeys(NAMES, .3)
            second = dict.fromkeys(NAMES, .5)
            save_profile('person A', first, path)
            save_profile('person B', second, path)
            activate_profile('person A', path)
            self.assertEqual(load_profiles(path), {
                'active': 'person A', 'profiles': {'person A': first, 'person B': second}})
            before = path.read_text()
            with self.assertRaises(ValueError):
                save_profile('person A', dict.fromkeys(NAMES, float('nan')), path)
            self.assertEqual(path.read_text(), before)
            activate_profile(None, path)
            self.assertIsNone(load_profiles(path)['active'])
            path.write_text('{bad')
            with self.assertRaises(ValueError):
                save_profile('person C', first, path)
            self.assertEqual(path.read_text(), '{bad')

    def test_tracker_uses_active_profile(self):
        from app.input.leap_tracker import LeapPinchTracker
        values = dict.fromkeys(NAMES, .52)

        class Reader:
            def __enter__(self):
                raise RuntimeError('no hardware in test')

            def __exit__(self, *args):
                pass

        with patch('app.input.leap_tracker.load_profiles', return_value={
            'active': 'person A', 'profiles': {'person A': values}}), \
                patch('app.input.leap_tracker.PinchClassifier', wraps=PinchClassifier) as classifier:
            tracker = LeapPinchTracker(reader_factory=Reader)
            tracker.close()
            classifier.assert_called_once_with(values)

    def test_dialog_capture_save_apply_and_shutdown(self):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from app.ui.leap_calibration_dialog import LeapCalibrationDialog
        from docs.check_leap_input import sample
        app = QApplication.instance() or QApplication([])

        class Tracker:
            status = 'TEST RIGHT HAND'
            closed = False
            value = None

            def calibration_sample(self):
                return self.value

            def close(self):
                self.closed = True

        with tempfile.TemporaryDirectory() as folder, \
                patch('app.input.leap_calibration.profile_path', return_value=Path(folder)/'profiles.json'):
            tracker = Tracker()
            from unittest.mock import Mock
            dialog = LeapCalibrationDialog(tracker_factory=lambda: tracker)
            dialog.timer.stop()
            dialog.profile.setCurrentText('test person')
            with patch('app.ui.leap_calibration_dialog.time.monotonic', return_value=10.):
                dialog.start_capture()
            tracker.value = sample(None, 11.1)
            with patch('app.ui.leap_calibration_dialog.time.monotonic', return_value=11.2):
                dialog.tick()
                dialog.tick()
            self.assertEqual(len(dialog.samples['NONE']), 1)  # Same frame counts only once.
            with patch('app.ui.leap_calibration_dialog.time.monotonic', return_value=14.1):
                dialog.tick()
            self.assertIsNone(dialog.phase)
            dialog.samples = measurements()
            dialog.save_capture()
            self.assertEqual(load_profiles()['active'], 'test person')
            self.assertEqual(load_profiles()['profiles']['test person'], dict.fromkeys(NAMES, .52))
            from PyQt6.QtWidgets import QDialog
            self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
            self.assertTrue(tracker.closed)
