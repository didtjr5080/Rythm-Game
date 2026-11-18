"""python -m unittest docs.check_pinch_judgement -v"""
import os
import unittest
from unittest.mock import patch

from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.input_fusion import GameInputState, InputFusion


def pinch(lane=0, visible=True, emg=False):
    return GameInputState(lane, 0., emg, visible, .5, .5, None, 0.)


class PinchJudgementChecks(unittest.TestCase):
    def test_hold_hits_consecutive_notes_without_emg(self):
        engine = RhythmGameEngine([Note(0, 0, 1000), Note(1, 0, 2000)])
        state = pinch()
        self.assertIsNone(engine.update(state, 999))
        self.assertEqual(engine.update(state, 1000), 'PERFECT')
        self.assertIsNone(engine.update(state, 1000))
        self.assertIsNone(engine.update(state, 1999))
        self.assertEqual(engine.update(state, 2000), 'PERFECT')
        self.assertIsNone(engine.update(state, 2001))
        self.assertEqual(engine.score_state.score, 2000)
        self.assertEqual(engine.score_state.combo, 2)

    def test_wrong_lane_no_pinch_or_lost_hand_cannot_score_even_with_emg(self):
        for state in (pinch(1, emg=True), pinch(None, emg=True), pinch(0, False, True)):
            engine = RhythmGameEngine([Note(0, 0, 1000)])
            self.assertIsNone(engine.update(state, 1000))
            self.assertEqual(engine.update(state, 1101), 'MISS')
            self.assertEqual(engine.score_state.score, 0)

    def test_timing_boundaries_and_no_early_score(self):
        for stamp, expected in ((900, None), (999, None), (1000, 'PERFECT'),
                                (1050, 'PERFECT'), (1051, 'GOOD'), (1100, 'GOOD'), (1101, 'MISS')):
            engine = RhythmGameEngine([Note(0, 0, 1000)])
            self.assertEqual(engine.update(pinch(), stamp), expected)

    def test_releasing_before_line_misses(self):
        engine = RhythmGameEngine([Note(0, 0, 1000)])
        self.assertIsNone(engine.update(pinch(), 950))
        self.assertIsNone(engine.update(pinch(None), 1000))
        self.assertEqual(engine.update(pinch(None), 1101), 'MISS')

    def test_fusion_without_emg_never_opens_reader(self):
        class Tracker:
            def track(self, frame): return {'lane': 0, 'hand_visible': True}
            def close(self): pass
        with patch('app.input.input_fusion.SerialEMGReader', side_effect=AssertionError('EMG opened')), \
                patch('app.input.input_fusion.MockEMGReader', side_effect=AssertionError('Mock EMG opened')):
            fusion = InputFusion(hand_tracker=Tracker(), use_emg=False)
            try:
                state, _ = fusion.read()
                self.assertEqual((state.lane, state.emg_value, state.emg_activated), (0, 0., False))
                self.assertIsNone(fusion.emg_reader)
            finally:
                fusion.close()

    def test_actual_game_never_opens_emg_or_uses_keyboard_as_pinch(self):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from app.ui.game_widget import GameWidget
        app = QApplication.instance() or QApplication([])
        with patch('app.input.input_fusion.SerialEMGReader', side_effect=AssertionError('EMG opened')), \
                patch('app.input.input_fusion.MockEMGReader', side_effect=AssertionError('Mock EMG opened')):
            game = GameWidget(object())
            try:
                game.timer.stop()
                self.assertIsNone(game.input_fusion.emg_reader)
                game.input_fusion.read = lambda frame=None: (pinch(None, False), None)
                game.engine = RhythmGameEngine([Note(0, 0, 1000)])
                game._playback_time_ms = lambda: 1000
                game._handle_key(Qt.Key.Key_1, True)
                game._handle_key(Qt.Key.Key_Space, True)
                game.game_loop()
                self.assertEqual(game.engine.score_state.score, 0)
                self.assertFalse(game.grab().isNull())
            finally:
                game.close()
