"""Run: python -m unittest docs.check_pre_game_calibration -q"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QDialog
from app.ui.main_window import MainWindow
from app.ui.leap_calibration_dialog import LeapCalibrationDialog
from app.input.leap_calibration import LABELS


class PreGameCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def owner(self):
        return SimpleNamespace(game_mode='pinch', selected_song_path=None, notes_path=None,
                               _defer_hand_navigation=lambda callback: False,
                               _release_current_inputs=Mock(), setCentralWidget=Mock(), _attach_navigation_camera=Mock())

    def test_each_start_and_retry_requires_calibration(self):
        owner = self.owner()
        with patch('app.ui.main_window.LeapCalibrationDialog') as dialog, patch('app.ui.main_window.GameWidget') as game:
            dialog.return_value.exec.return_value = QDialog.DialogCode.Rejected
            MainWindow.show_game_widget(owner, 'pinch')
            game.assert_not_called()
            dialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            MainWindow.show_game_widget(owner, 'pinch')
            MainWindow.show_game_widget(owner)
            self.assertEqual(dialog.call_count, 3)
            self.assertEqual(game.call_count, 2)
            self.assertEqual(dialog.return_value.deleteLater.call_count, 3)

    def test_emg_keeps_its_own_preparation(self):
        with patch('app.ui.main_window.LeapCalibrationDialog') as dialog, patch('app.ui.main_window.GameWidget') as game:
            MainWindow.show_game_widget(self.owner(), 'emg')
            dialog.assert_not_called()
            self.assertEqual(game.call_args.kwargs['mode'], 'emg')

    def test_new_measurements_required_even_with_saved_profile(self):
        tracker = Mock(status='test')
        data = {'active': 'Existing', 'profiles': {'Existing': {}}}
        with patch('app.ui.leap_calibration_dialog.load_profiles', return_value=data), patch('app.ui.leap_calibration_dialog.save_profile') as save:
            dialog = LeapCalibrationDialog(tracker_factory=lambda: tracker)
            try:
                self.assertFalse(dialog.save.isEnabled())
                dialog.save_capture()
                save.assert_not_called()
                self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
                dialog.samples = {label: [[.8]*4 for _ in range(25)] for label in LABELS}
                for index, label in enumerate(LABELS[1:]):
                    dialog.samples[label] = [[.2 if i == index else .8 for i in range(4)] for _ in range(25)]
                dialog.refresh_progress()
                self.assertTrue(dialog.save.isEnabled())
                dialog.save_capture()
                save.assert_called_once()
                self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
                tracker.close.assert_called_once()
                self.assertFalse(dialog.timer.isActive())
            finally:
                dialog.deleteLater()
