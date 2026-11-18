"""python -m unittest docs.check_leap_only_pinch -q; no hardware access."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PyQt6.QtWidgets import QApplication,QWidget,QCheckBox
from app.ui.leap_calibration_dialog import LeapCalibrationDialog
from app.ui.game_selection_screen import GameSelectionScreen
from app.ui.main_window import MainWindow
from app.ui.game_widget import GameWidget
from app.game.rhythm_game_engine import RhythmGameEngine
from app.game.note import Note


class LeapOnlyPinchChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def test_calibration_does_not_request_armband_and_test_toggle_is_removed(self):
        parent=QWidget()
        parent.emg_session=Mock()
        parent.emg_session.acquire.side_effect=AssertionError('Armband opened')
        tracker=Mock(status='TEST LEAP')
        dialog=LeapCalibrationDialog(parent,tracker_factory=lambda:tracker)
        try:
            parent.emg_session.acquire.assert_not_called()
            self.assertNotIn('armband',dialog.windowTitle())
            self.assertFalse(hasattr(dialog,'armband_samples'))
            self.assertFalse(dialog.grab().isNull())
        finally:
            dialog.reject()
            dialog.deleteLater()
            parent.deleteLater()
        owner=SimpleNamespace(selected_song_path=None,show_game_widget=Mock(),show_start_screen=Mock())
        selection=GameSelectionScreen(owner)
        try:
            self.assertEqual(selection.findChildren(QCheckBox),[])
            selection.mode_buttons['pinch'].click()
            owner.show_game_widget.assert_called_once_with('pinch')
        finally: selection.close()

    def test_entering_pinch_preserves_emg_connection_without_using_it(self):
        owner=SimpleNamespace(game_mode='pinch',selected_song_path=None,notes_path=None,
            emg_session=Mock(),_defer_hand_navigation=lambda callback:False,
            _release_current_inputs=Mock(),setCentralWidget=Mock(),_attach_navigation_camera=Mock())
        with patch('app.ui.main_window.LeapCalibrationDialog') as dialog,patch('app.ui.main_window.GameWidget') as game:
            dialog.return_value.exec.return_value=0
            MainWindow.show_game_widget(owner,'pinch')
            owner.emg_session.shutdown.assert_not_called()
            owner.emg_session.acquire.assert_not_called()
            game.assert_not_called()

    def test_leap_alone_scores_and_renders_without_any_emg_reader(self):
        class Tracker:
            status='LEAP RIGHT / INDEX'
            last_error=None
            visible=True
            def track(self,frame):
                return {'lane':0 if self.visible else None,'hand_visible':self.visible,'hand_label':'INDEX'}
            def close(self): pass
        tracker=Tracker()
        owner=SimpleNamespace(emg_session=Mock())
        owner.emg_session.acquire.side_effect=AssertionError('Armband opened')
        with patch('app.input.input_fusion.LeapPinchTracker',return_value=tracker), \
             patch('app.input.input_fusion.create_emg_reader',side_effect=AssertionError('Armband opened')):
            game=GameWidget(owner)
            try:
                game.timer.stop()
                self.assertIsNone(game.input_fusion.emg_reader)
                owner.emg_session.acquire.assert_not_called()
                game.engine=RhythmGameEngine([Note(0,0,1000),Note(1,0,2000),Note(2,0,5000)])
                game._playback_time_ms=lambda:1000
                game.game_loop()
                self.assertEqual(game.engine.score_state.score,1000)
                self.assertEqual(game.current_input.pinch_input_source,'leap_only')
                tracker.visible=False
                game._playback_time_ms=lambda:2101
                game.game_loop()
                self.assertEqual(game.engine.score_state.score,1000)
                self.assertFalse(game.grab().isNull())
            finally: game.close()
