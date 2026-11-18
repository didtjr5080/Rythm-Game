"""python -m unittest docs.check_miss_limit -v"""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from docs.check_pinch_judgement import pinch


def game(mode='pinch'):
    return RhythmGameEngine([Note(i, 0, (i+1)*1000) for i in range(30)], mode=mode)


class MissLimitChecks(unittest.TestCase):
    def test_tenth_miss_ends_pinch_and_freezes_further_scoring(self):
        engine = game()
        for i in range(9):
            self.assertEqual(engine.update(pinch(None, False), (i+1)*1000+101), 'MISS')
            self.assertFalse(engine.miss_limit_reached)
        self.assertEqual(engine.update(pinch(None, False), 10101), 'MISS')
        self.assertTrue(engine.miss_limit_reached)
        self.assertTrue(engine.is_finished(10101))
        self.assertIsNone(engine.update(pinch(), 11000))
        self.assertFalse(engine.notes[10].judged)
        self.assertEqual(engine.score_state.miss_count, 10)

    def test_success_resets_streak_and_idle_frames_do_not_count(self):
        for offset, expected in ((0, 'PERFECT'), (60, 'GOOD')):
            engine = game()
            for i in range(9):
                engine.update(pinch(None, False), (i+1)*1000+101)
            self.assertIsNone(engine.update(pinch(None, False), 9500))
            self.assertEqual(engine.consecutive_misses, 9)
            self.assertEqual(engine.update(pinch(), 10000+offset), expected)
            self.assertEqual(engine.consecutive_misses, 0)
            for i in range(9):
                engine.update(pinch(None, False), 11000+i*1000+101)
            self.assertFalse(engine.miss_limit_reached)

    def test_emg_mode_is_unchanged(self):
        engine = game('emg')
        for i in range(12):
            engine.update(pinch(None, False), (i+1)*1000+351)
        self.assertEqual(engine.score_state.miss_count, 12)
        self.assertFalse(engine.miss_limit_reached)
        self.assertFalse(engine.is_finished(12351))

    def test_music_does_not_delay_game_over_and_result_is_saved(self):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from app.ui.game_widget import GameWidget
        app = QApplication.instance() or QApplication([])
        results = []
        owner = SimpleNamespace(show_result_screen=lambda metrics, **kwargs: results.append(metrics))
        widget = GameWidget(owner)
        try:
            widget.timer.stop()
            widget.engine = game()
            for i in range(9):
                widget.engine.update(pinch(None, False), (i+1)*1000+101)
            widget.song_path = 'playing-song.wav'
            widget.audio_player.stop()
            stopped = []
            widget.audio_player = SimpleNamespace(error=None, finished=False, loading=False,
                                                   stop=lambda: stopped.append(True))
            widget._playback_time_ms = lambda: 10101
            widget.input_fusion.read = lambda frame=None: (pinch(None, False), None)
            with patch('app.config.SAVE_SESSION_LOG', False):
                widget.game_loop()
            self.assertTrue(widget.finished)
            self.assertTrue(stopped)
            self.assertEqual(results[0]['end_reason'], '10_consecutive_misses')
            self.assertEqual(results[0]['miss_count'], 10)
        finally:
            widget.close()
