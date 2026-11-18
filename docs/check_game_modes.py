"""python -m unittest docs.check_game_modes -v"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.audio.note_generator_adapter import save_notes_json
from app.game.emg_chart import generate_emg_notes
from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.input_fusion import GameInputState


def emg(active):
    return GameInputState(None, 20. if active else 0., active, False, None, None, None, 0.)


class GameModeChecks(unittest.TestCase):
    def test_generation_beat_grid_holds_rest_and_song_end(self):
        analysis = {'bpm': 120., 'duration': 30., 'beats': [i*.5 for i in range(60)]}
        notes = generate_emg_notes([], analysis)
        self.assertTrue(any(n['duration_ms'] == 0 for n in notes))
        self.assertTrue(any(n['duration_ms'] >= 1000 for n in notes))
        for note in notes:
            self.assertEqual(note['lane'], 0)
            self.assertIn(note['hit_time_ms']/1000, analysis['beats'])
            self.assertLessEqual(note['duration_ms'], 4000)
            self.assertLessEqual(note['hit_time_ms'] + note['duration_ms'], 29800)
        for first, second in zip(notes, notes[1:]):
            self.assertGreaterEqual(second['hit_time_ms'] - first['hit_time_ms'] - first['duration_ms'], 1000)

    def test_both_modes_in_one_saved_chart(self):
        pinch_notes = [{'lane': i % 4, 'hit_time_ms': 2000 + i*1000} for i in range(20)]
        with tempfile.TemporaryDirectory() as folder:
            path = save_notes_json(pinch_notes, output_dir=folder,
                                   analysis={'bpm': 120., 'duration': 30., 'beats': []})
            payload = json.loads(path.read_text())
            self.assertIn('notes', payload)
            self.assertIn('emg_notes', payload)
            pinch_game = RhythmGameEngine.from_json_file(path, mode='pinch')
            emg_game = RhythmGameEngine.from_json_file(path, mode='emg')
            self.assertTrue(pinch_game.notes and emg_game.notes)
            self.assertTrue(all(n.duration_ms == 0 for n in pinch_game.notes))
            self.assertTrue(all(n.lane == 0 for n in emg_game.notes))
            self.assertTrue(any(n.duration_ms >= 1000 for n in emg_game.notes))
            self.assertEqual(RhythmGameEngine.from_json_file(path).mode, 'pinch')

    def test_old_flat_seconds_chart_and_mode_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'legacy.json'
            path.write_text(json.dumps([{'lane': 1, 'time': 3.}, {'lane': 2, 'time': 5.}]))
            self.assertTrue(RhythmGameEngine.from_json_file(path, 'pinch').notes)
            self.assertTrue(any(n.duration_ms for n in RhythmGameEngine.from_json_file(path, 'emg').notes))
        self.assertTrue(any(n.duration_ms for n in RhythmGameEngine(mode='emg').notes))

    def test_tap_requires_new_contraction_and_no_hand(self):
        engine = RhythmGameEngine([Note(0, 0, 1000), Note(1, 0, 2000)], mode='emg')
        engine.update(emg(False), 800)
        self.assertEqual(engine.update(emg(True), 1000), 'PERFECT')
        self.assertIsNone(engine.update(emg(True), 2000))
        engine.update(emg(False), 2020)
        self.assertEqual(engine.update(emg(True), 2151), 'GOOD')
        self.assertEqual(engine.score_state.score, 1500)

    def test_hold_scores_only_at_tail(self):
        note = Note(0, 0, 1000, duration_ms=2000)
        engine = RhythmGameEngine([note], mode='emg')
        self.assertIsNone(engine.update(emg(True), 1000))
        self.assertTrue(note.holding)
        for stamp in range(1100, 3000, 100):
            self.assertIsNone(engine.update(emg(True), stamp))
            self.assertEqual(engine.score_state.score, 0)
        self.assertEqual(engine.update(emg(True), 3000), 'PERFECT')
        self.assertIsNone(engine.update(emg(True), 3010))
        self.assertEqual(engine.score_state.score, 1000)
        self.assertTrue(engine.is_finished(3010))

    def test_early_release_or_unobserved_gap_fails_hold(self):
        for stamp, active in ((1100, False), (1400, True)):
            engine = RhythmGameEngine([Note(0, 0, 1000, duration_ms=2000)], mode='emg')
            engine.update(emg(True), 1000)
            if active:
                self.assertEqual(engine.update(emg(active), stamp), 'MISS')
            else:
                for tick in range(stamp, 1501, 100):
                    self.assertIsNone(engine.update(emg(False), tick))
                self.assertEqual(engine.update(emg(False), 1601), 'MISS')
            self.assertEqual(engine.score_state.score, 0)

    def test_held_before_beat_or_absent_emg_misses(self):
        engine = RhythmGameEngine([Note(0, 0, 1000)], mode='emg')
        engine.update(emg(True), 0)
        self.assertIsNone(engine.update(emg(True), 1000))
        self.assertEqual(engine.update(emg(True), 1351), 'MISS')
        engine = RhythmGameEngine([Note(0, 0, 1000)], mode='emg')
        self.assertEqual(engine.update(emg(False), 1351), 'MISS')

    def test_holding_note_stays_in_visible_query_and_game_not_finished(self):
        note = Note(0, 0, 1000, duration_ms=4000)
        engine = RhythmGameEngine([note], mode='emg')
        self.assertIn(note, engine.notes_in_time_range(3500, 4500))
        self.assertFalse(engine.is_finished(4000))
        self.assertTrue(engine.is_finished(6501))

    def test_selection_and_emg_ui_do_not_start_leap(self):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from app.ui.main_window import MainWindow
        from app.ui.game_selection_screen import GameSelectionScreen
        from app.i18n import tr
        app = QApplication.instance() or QApplication([])
        with patch('app.config.USE_MOCK_EMG', True), patch('app.config.USE_CAMERA', False):
            window = MainWindow()
            try:
                window.show_game_selection()
                self.assertIsInstance(window.centralWidget(), GameSelectionScreen)
                self.assertEqual(tr('start_game', 'ko'), '게임 선택')
                self.assertFalse(window.centralWidget().grab().isNull())
                with patch('app.input.input_fusion.LeapPinchTracker', side_effect=AssertionError('Leap opened')):
                    window.centralWidget().mode_buttons['emg'].click()
                    game = window.centralWidget()
                    game.timer.stop()
                    game.rest_baseline.baseline_cents = 5000
                    self.assertEqual(game.mode, 'emg')
                    self.assertEqual(game.lane_count, 1)
                    self.assertIsNone(game.input_fusion.tracker)
                    self.assertIsNotNone(game.input_fusion.emg_reader)
                    game._handle_key(Qt.Key.Key_Space, True)
                    self.assertTrue(game.input_fusion.read()[0].emg_activated)
                    game._handle_key(Qt.Key.Key_Space, False)
                    self.assertFalse(game.input_fusion.read()[0].emg_activated)
                    long_note = next(n for n in game.engine.notes if n.duration_ms)
                    long_note.holding = True
                    game._playback_time_ms = lambda: long_note.hit_time_ms + 500
                    self.assertFalse(game.grab().isNull())
                    game.close()
                window.show_game_selection()
                from PyQt6.QtWidgets import QDialog
                with patch('app.ui.main_window.LeapCalibrationDialog') as calibration:
                    calibration.return_value.exec.return_value = QDialog.DialogCode.Accepted
                    window.centralWidget().mode_buttons['pinch'].click()
                    calibration.assert_called_once()
                game = window.centralWidget()
                game.timer.stop()
                self.assertEqual(game.mode, 'pinch')
                self.assertEqual(game.lane_count, 4)
                self.assertIsNone(game.input_fusion.emg_reader)
            finally:
                window.close()
