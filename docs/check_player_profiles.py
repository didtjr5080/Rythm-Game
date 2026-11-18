"""Profile isolation, saved calibration reuse and completion-gated advanced mode."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.player_profiles import ProfileStore
from app.input.pinch_classifier import NAMES
from app.input.input_fusion import GameInputState
from app.input.leap_tracker import LeapPinchTracker
from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.ui.game_widget import GameWidget
from app.ui.main_window import MainWindow
from app.ui.profile_dialog import ProfileDialog


class PlayerProfileChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name)/'players.json'
        self.store = ProfileStore(self.path)
        self.a = self.store.create('사람 A')
        self.b = self.store.create('사람 B')
        self.addCleanup(patch.stopall)
        patch('app.config.SAVE_SESSION_LOG', False).start()

    def calibrated(self, key):
        self.store.save_pinch(key, dict.fromkeys(NAMES, .4))
        self.store.save_emg(key, 100., [110., 100., 120.])

    def owner(self):
        return NS(profile_store=self.store, show_start_screen=Mock(), show_result_screen=Mock())

    def fake_game(self, key, mode='emg'):
        sample = GameInputState(0, 100., False, True, .5, .5, 1, 0.)
        fusion = NS(read=lambda frame:(sample,None), emg_reader=NS(samples=[110.,100.,120.],status='FAKE'),
                    close=Mock(), last_timing_error_ms=None, finger_states=None,
                    tracker=NS(status='FAKE LEAP',last_error=None))
        audio = Mock(error=None,finished=False,loading=False,position_ms=0,duration_seconds=20.)
        owner = self.owner()
        with patch('app.ui.game_widget.InputFusion',return_value=fusion) as factory, \
             patch('app.ui.game_widget.AudioPlayer',return_value=audio):
            game = GameWidget(owner,song_path='track.mp3',mode=mode,profile_id=key)
        game.timer.stop(); self.addCleanup(game.close)
        return game, owner, audio, factory

    def test_create_select_delete_and_duplicate_names(self):
        self.store.select(self.a)
        self.assertEqual(self.store.active()[0], self.a)
        with self.assertRaises(ValueError): self.store.create(' 사람 A ')
        self.store.delete(self.a)
        self.assertEqual(self.store.active(), (None,None))
        self.assertIsNotNone(self.store.get(self.b))
        self.assertIsNone(ProfileStore(self.path).get(self.a))
        with self.assertRaises(ValueError): self.store.record_completion(self.a,'pinch')

    def test_values_and_completion_are_isolated_per_person(self):
        self.calibrated(self.a)
        self.store.record_completion(self.a,'pinch')
        self.assertFalse(self.store.unlocked(self.a))
        self.store.record_completion(self.a,'emg')
        self.assertTrue(self.store.unlocked(self.a))
        self.assertFalse(self.store.unlocked(self.b))
        self.assertIsNone(self.store.get(self.b)['emg'])
        self.assertFalse(self.store.unlocked(None))

    def test_clearing_calibration_revokes_completion_and_unlock(self):
        self.calibrated(self.a)
        for mode in ('pinch','emg'): self.store.record_completion(self.a,mode)
        self.store.clear_calibration(self.a,'pinch')
        person = self.store.get(self.a)
        self.assertIsNone(person['pinch'])
        self.assertFalse(person['completed']['pinch'])
        self.assertTrue(person['completed']['emg'])
        self.assertFalse(self.store.unlocked(self.a))

    def test_invalid_and_corrupt_files_are_not_overwritten(self):
        previous = self.path.read_bytes()
        with self.assertRaises(ValueError): self.store.save_emg(self.a, 0., [100.])
        self.assertEqual(self.path.read_bytes(),previous)
        self.path.write_text('{broken')
        with self.assertRaises(ValueError): self.store.create('New')
        self.assertEqual(self.path.read_text(),'{broken')

    def test_atomic_save_failure_preserves_previous_profiles(self):
        previous = self.path.read_bytes()
        with patch('app.player_profiles.atomic_text',side_effect=OSError('disk failed')):
            with self.assertRaises(OSError): self.store.delete(self.a)
        self.assertEqual(self.path.read_bytes(),previous)

    def test_legacy_named_pinch_calibration_imports_without_success_or_emg(self):
        with patch('app.player_profiles.settings_path',return_value=Path(self.folder.name)/'settings.json'), \
             patch('app.player_profiles.load_profiles',return_value={'active':'Old','profiles':{'Old':dict.fromkeys(NAMES,.4)}}):
            store = ProfileStore()
            key, person = store.active()
            self.assertEqual(person['name'],'Old')
            self.assertIsNone(person['emg'])
            self.assertFalse(store.unlocked(key))
            self.assertEqual(store.active()[0],key)
            store.delete(key)
            self.assertEqual(store.load()['profiles'],{})  # Never reimport a deleted person.

    def test_saved_emg_starts_immediately_and_pinch_values_are_injected(self):
        self.calibrated(self.a)
        game, owner, audio, factory = self.fake_game(self.a)
        self.assertTrue(game.rest_baseline.ready)
        self.assertEqual(game.rest_baseline.threshold,100.)
        audio.play.assert_called_once()
        pinch_game, _, _, factory = self.fake_game(self.a,'pinch')
        self.assertEqual(factory.call_args.kwargs['leap_thresholds'],dict.fromkeys(NAMES,.4))
        self.assertIsNone(pinch_game.rest_baseline)

    def test_new_emg_measurement_is_saved_to_the_started_person_only(self):
        game, owner, audio, _ = self.fake_game(self.a)
        audio.play.assert_not_called()
        self.store.select(self.b)
        for stamp in (10.,13.):
            with patch('app.ui.game_widget.time.monotonic',return_value=stamp): game.game_loop()
        self.assertEqual(self.store.get(self.a)['emg']['minimum'],100.)
        self.assertIsNone(self.store.get(self.b)['emg'])
        self.assertFalse(self.store.get(self.a)['completed']['emg'])
        audio.play.assert_called_once()

    def test_only_real_natural_completion_unlocks_started_person(self):
        self.calibrated(self.a)
        game, owner, audio, _ = self.fake_game(self.a,'pinch')
        self.store.select(self.b)
        game.engine = RhythmGameEngine([Note(0,0,1000)],mode='pinch')
        game.engine.notes[0].judged = True
        game.engine.score_state.apply_result('PERFECT')
        audio.finished = True
        game.finish_game(reason='completed')
        self.assertTrue(self.store.get(self.a)['completed']['pinch'])
        self.assertFalse(self.store.get(self.b)['completed']['pinch'])
        metrics = owner.show_result_screen.call_args.args[0]
        self.assertTrue(metrics['completed_successfully'])
        self.assertEqual(metrics['player_profile_id'],self.a)

    def test_manual_exit_error_and_miss_limit_never_grant_completion(self):
        self.calibrated(self.a)
        for reason, error, streak, finished in (('manual',None,0,True),('completed','USB lost',0,True),
                                               ('completed',None,10,True),('completed',None,0,False)):
            game, owner, audio, _ = self.fake_game(self.a)
            game.engine.notes = [Note(0,0,1000,judged=True)]
            game.engine.consecutive_misses = streak
            audio.finished = finished; audio.error = error
            game.finish_game(reason=reason)
            self.assertFalse(self.store.get(self.a)['completed']['emg'])
            self.assertFalse(owner.show_result_screen.call_args.args[0]['completed_successfully'])

    def test_deleted_during_game_is_not_recreated_by_completion(self):
        self.calibrated(self.a)
        game, owner, audio, _ = self.fake_game(self.a)
        game.engine.notes = [Note(0,0,1000,judged=True)]
        audio.finished = True
        self.store.delete(self.a)
        game.finish_game(reason='completed')
        self.assertIsNone(self.store.get(self.a))
        self.assertIn('profile_save_error',owner.show_result_screen.call_args.args[0])

    def test_direct_advanced_constructor_is_also_locked(self):
        with self.assertRaises(ValueError): self.fake_game(self.a,'pinch_extension')
        with self.assertRaises(ValueError): GameWidget(NS(),mode='pinch_extension')

    def test_saved_profile_skips_leap_dialog_and_locked_mode_cannot_bypass_card(self):
        self.calibrated(self.a); self.store.select(self.a)
        with patch('app.ui.main_window.ProfileStore',return_value=self.store), \
             patch('app.config.USE_CAMERA',False),patch('app.config.USE_MOCK_EMG',True), \
             patch('app.ui.main_window.LeapCalibrationDialog') as dialog, \
             patch('app.ui.main_window.QMessageBox.warning') as warning, \
             patch('app.ui.game_widget.InputFusion') as make_fusion, \
             patch('app.ui.game_widget.AudioPlayer',return_value=Mock(error=None,loading=False,finished=False,position_ms=0,duration_seconds=20.)):
            window = MainWindow()
            try:
                window.show_game_selection()
                self.assertFalse(window.centralWidget().mode_buttons['pinch_extension'].isEnabled())
                window.show_game_widget('pinch_extension'); warning.assert_called_once()
                make_fusion.assert_not_called()
                window.show_game_widget('pinch')
                dialog.assert_not_called(); make_fusion.assert_called_once()
                self.assertIsInstance(window.centralWidget(),GameWidget)
            finally: window.close()

    def test_profile_dialog_creates_selects_and_deletes_the_chosen_person(self):
        with patch('app.ui.main_window.ProfileStore',return_value=self.store), \
             patch('app.config.USE_CAMERA',False),patch('app.config.USE_MOCK_EMG',True):
            window = MainWindow(); dialog = ProfileDialog(window)
            try:
                dialog.name.setText('사람 C'); dialog.create()
                key, person = self.store.active()
                self.assertEqual(person['name'],'사람 C')
                dialog.combo.setCurrentIndex(dialog.combo.findData(self.a))
                with patch('app.ui.profile_dialog.QMessageBox.question',return_value=QMessageBox.StandardButton.Yes): dialog.delete()
                self.assertIsNone(self.store.get(self.a))
                self.assertIsNotNone(self.store.get(key))
            finally: dialog.close(); window.close()

    def test_first_pinch_calibration_is_saved_to_selected_person(self):
        self.store.select(self.a)
        thresholds = dict.fromkeys(NAMES,.5)
        with patch('app.ui.main_window.ProfileStore',return_value=self.store), \
             patch('app.config.USE_CAMERA',False),patch('app.config.USE_MOCK_EMG',True), \
             patch('app.ui.main_window.LeapCalibrationDialog') as dialog, \
             patch('app.ui.game_widget.InputFusion') as fusion, \
             patch('app.ui.game_widget.AudioPlayer',return_value=Mock(error=None,finished=False,loading=False,position_ms=0,duration_seconds=20.)):
            from PyQt6.QtWidgets import QDialog
            dialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            dialog.return_value.calibrated_thresholds = thresholds
            window = MainWindow()
            try:
                window.show_game_widget('pinch')
                self.assertEqual(self.store.get(self.a)['pinch'],thresholds)
                self.assertIsNone(self.store.get(self.b)['pinch'])
                self.assertEqual(fusion.call_args.kwargs['leap_thresholds'],thresholds)
                self.assertFalse(self.store.get(self.a)['completed']['pinch'])
            finally: window.close()

    def test_tracker_uses_injected_person_thresholds_without_loading_legacy_active_person(self):
        class Reader:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def poll(self,*args): return False,None
        values = dict.fromkeys(NAMES,.6)
        from app.input.pinch_classifier import PinchClassifier
        with patch('app.input.leap_tracker.load_profiles',side_effect=AssertionError('Legacy profile leaked')), \
             patch('app.input.leap_tracker.PinchClassifier',wraps=PinchClassifier) as classifier:
            tracker = LeapPinchTracker(reader_factory=Reader,thresholds=values)
            tracker.close()
            classifier.assert_called_once_with(values)
