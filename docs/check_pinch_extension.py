"""Advanced mode must require the correct Leap pinch AND fresh EMG extension."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog
from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.input_fusion import GameInputState, InputFusion
from app.ui.game_widget import GameWidget
from app.ui.main_window import MainWindow
from app.ui.game_selection_screen import GameSelectionScreen
from app.player_profiles import ProfileStore
from app.input.pinch_classifier import NAMES


def state(lane=3, extension=True, fresh=True, visible=True, value=100.):
    return GameInputState(lane, value, extension, visible, .5, .5, 1, 0.,
                          emg_signal_fresh=fresh)


class PinchExtensionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.store = ProfileStore(Path(self.folder.name)/'players.json')
        self.profile_id = self.store.create('Advanced player')
        self.store.save_pinch(self.profile_id, dict.fromkeys(NAMES, .4))
        self.store.save_emg(self.profile_id, 100., [105., 100., 110.])
        for mode in ('pinch', 'emg'): self.store.record_completion(self.profile_id, mode)

    def test_only_simultaneous_correct_pinch_and_fresh_extension_scores(self):
        for sample, success in ((state(), True), (state(extension=False), False),
                                (state(fresh=False), False), (state(lane=1), False),
                                (state(visible=False), False)):
            with self.subTest(sample=sample):
                engine = RhythmGameEngine([Note(0, 3, 1000)], mode='pinch_extension')
                result = engine.update(sample, 1000)
                self.assertEqual(result, 'PERFECT' if success else None)
                if not success:
                    self.assertEqual(engine.update(sample, 1101), 'MISS')

    def test_extension_can_arrive_inside_window_but_never_after_it(self):
        for stamp, result in ((1060, 'GOOD'), (1101, 'MISS')):
            engine = RhythmGameEngine([Note(0, 3, 1000)], mode='pinch_extension')
            self.assertIsNone(engine.update(state(extension=False), 1000))
            self.assertEqual(engine.update(state(), stamp), result)
            self.assertIsNone(engine.update(state(), stamp+1))

    def test_plain_pinch_is_still_independent_of_armband(self):
        engine = RhythmGameEngine([Note(0, 3, 1000)], mode='pinch')
        self.assertEqual(engine.update(state(extension=False, fresh=False), 1000), 'PERFECT')

    def test_advanced_chart_uses_four_pinch_lanes_and_no_emg_holds(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'chart.json'
            path.write_text(json.dumps({'notes': [{'lane': 3, 'hit_time_ms': 1000, 'duration_ms': 2000}],
                                        'emg_notes': [{'lane': 0, 'hit_time_ms': 5000, 'duration_ms': 3000}]}))
            engine = RhythmGameEngine.from_json_file(path, mode='pinch_extension')
            self.assertEqual([(n.lane, n.hit_time_ms, n.duration_ms) for n in engine.notes], [(3, 1000, 0)])

    def test_advanced_mode_has_same_consecutive_miss_limit(self):
        engine = RhythmGameEngine([Note(i, 3, 1000+i*1000) for i in range(21)], mode='pinch_extension')
        for i in range(9): engine.update(state(extension=False), 1101+i*1000)
        self.assertEqual(engine.update(state(), 10000), 'PERFECT')
        for i in range(9): engine.update(state(extension=False), 11101+i*1000)
        self.assertFalse(engine.miss_limit_reached)
        engine.update(state(extension=False), 20101)
        self.assertTrue(engine.miss_limit_reached)
        self.assertEqual(engine.score_state.miss_count, 19)

    def test_game_reuses_profile_baseline_preserves_lane_and_records_new_mode(self):
        sample = state(extension=False, value=100.)
        reader = NS(samples=[105., 100., 110.], status='FAKE EMG')
        fusion = NS(read=lambda frame: (sample, None), emg_reader=reader,
                    close=Mock(), last_timing_error_ms=None, finger_states=None,
                    tracker=NS(status='FAKE LEAP', last_error=None))
        player = Mock(error=None, loading=False, finished=False, position_ms=0, duration_seconds=20.)
        owner = NS(show_start_screen=Mock(), show_result_screen=Mock(), emg_session=Mock(), profile_store=self.store)
        with patch('app.ui.game_widget.InputFusion', return_value=fusion) as create, \
             patch('app.ui.game_widget.AudioPlayer', return_value=player):
            game = GameWidget(owner, song_path='track.mp3', mode='pinch_extension', profile_id=self.profile_id)
            try:
                game.timer.stop()
                self.assertTrue(create.call_args.kwargs['use_leap'])
                self.assertTrue(create.call_args.kwargs['use_emg'])
                self.assertIs(create.call_args.kwargs['emg_session'], owner.emg_session)
                self.assertEqual(game.lane_count, 4)
                player.play.assert_called_once()
                self.assertTrue(game.rest_baseline.ready)
                self.assertEqual(game.rest_baseline.threshold, 100.)
                game.engine = RhythmGameEngine([Note(0, 3, 1000)], mode='pinch_extension')
                player.position_ms = 1000
                sample.lane = 3; sample.emg_value = 99.
                game.game_loop()
                self.assertEqual(game.engine.score_state.score, 0)
                self.assertEqual(game.current_input.lane, 3)
                sample.emg_value = 100.
                game.game_loop()
                self.assertEqual(game.engine.score_state.score, 1000)
                self.assertFalse(game.grab().isNull())
                with patch('app.config.SAVE_SESSION_LOG', False): game.finish_game()
                metrics = owner.show_result_screen.call_args.args[0]
                self.assertEqual(metrics['input_mode'], 'pinch_extension')
                self.assertEqual(metrics['pinch_input_source'], 'leap_and_emg_extension')
                self.assertEqual(metrics['emg_baseline_method'], 'minimum')
            finally: game.close()

    def test_third_selection_button_and_locked_profile(self):
        owner = NS(show_game_widget=Mock(), show_start_screen=Mock())
        selection = GameSelectionScreen(owner)
        try:
            selection.resize(800, 600)
            self.assertEqual(len(selection.mode_buttons), 3)
            self.assertFalse(selection.grab().isNull())
            selection.mode_buttons['pinch_extension'].click()
            owner.show_game_widget.assert_called_once_with('pinch_extension')
        finally: selection.close()
        self.store.create('New player')
        with patch('app.config.USE_CAMERA', False), patch('app.config.USE_MOCK_EMG', True), \
             patch('app.ui.main_window.ProfileStore', return_value=self.store), \
             patch('app.ui.main_window.QMessageBox.warning') as warning, \
             patch('app.ui.main_window.LeapCalibrationDialog') as dialog:
            window = MainWindow()
            try:
                window.show_game_selection()
                self.assertFalse(window.centralWidget().mode_buttons['pinch_extension'].isEnabled())
                window.show_game_widget('pinch_extension')
                dialog.assert_not_called()
                warning.assert_called_once()
                self.assertIsInstance(window.centralWidget(), GameSelectionScreen)
            finally: window.close()

    def test_saved_profile_opens_advanced_game_with_both_sensors_without_calibration(self):
        tracker = Mock(status='FAKE LEAP', last_error=None)
        tracker.track.return_value = {'hand_visible': False, 'lane': None}
        with patch('app.config.USE_CAMERA', False), patch('app.config.USE_MOCK_EMG', True), \
             patch('app.input.input_fusion.LeapPinchTracker', return_value=tracker), \
             patch('app.ui.main_window.ProfileStore', return_value=self.store), \
             patch('app.ui.main_window.LeapCalibrationDialog') as dialog:
            dialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            window = MainWindow()
            try:
                window.show_game_selection()
                window.centralWidget().mode_buttons['pinch_extension'].click()
                game = window.centralWidget(); game.timer.stop()
                self.assertIsInstance(game, GameWidget)
                self.assertEqual(window.game_mode, 'pinch_extension')
                self.assertIs(game.input_fusion.tracker, tracker)
                self.assertIsNotNone(game.input_fusion.emg_reader)
                self.assertTrue(game.rest_baseline.ready)
                self.assertIsNone(game.audio_player.started_at)
                dialog.assert_not_called()
            finally: window.close()

    def test_failed_armband_read_is_not_fresh_even_if_reader_claims_connection(self):
        reader = NS(read=Mock(side_effect=OSError('USB lost')), signal_fresh=True)
        fusion = InputFusion(use_camera=False, use_emg=False, use_leap=False)
        fusion.emg_reader = reader
        sample, _ = fusion.read()
        self.assertFalse(sample.emg_signal_fresh)
        self.assertFalse(sample.emg_activated)
