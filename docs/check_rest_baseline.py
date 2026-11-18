"""python -m unittest docs.check_rest_baseline -v"""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.input.rest_baseline import RestBaseline
from docs.check_game_modes import emg


class RestBaselineChecks(unittest.TestCase):
    def test_delayed_tick_excludes_samples_after_three_seconds(self):
        baseline = RestBaseline()
        baseline.measure([300., 200.], True, 10.)
        baseline.measure([150.], True, 12.99)
        baseline.measure([0.], True, 13.1)
        self.assertTrue(baseline.ready)
        self.assertEqual(baseline.baseline, 150.)
        self.assertEqual(baseline.samples, [300., 200., 150.])

    def test_raw_minimum_is_not_rounded_for_classification(self):
        baseline = RestBaseline()
        baseline.measure([185.024, 185.029], True, 0.)
        baseline.measure([185.025], True, 3.)
        self.assertEqual(baseline.baseline, 185.024)
        self.assertFalse(baseline.active(185.0239, True))
        self.assertTrue(baseline.active(185.024, True))
        self.assertTrue(baseline.active(185.0241, True))
        baseline.measure([0.], True, 4.)
        self.assertEqual(baseline.baseline, 185.024)

    def test_no_samples_never_creates_an_artificial_zero_threshold(self):
        baseline = RestBaseline()
        baseline.measure([], True, 0.)
        baseline.measure([], True, 3.)
        self.assertFalse(baseline.ready)
        self.assertFalse(baseline.active(4095., True))

    def test_exact_three_seconds_minimum_and_inclusive_threshold(self):
        baseline = RestBaseline()
        baseline.measure([185.02, 185.04], True, 10.)
        baseline.measure([185.03], True, 12.99)
        self.assertFalse(baseline.ready)
        baseline.measure([185.03], True, 13.)
        self.assertEqual(baseline.baseline, 185.02)
        self.assertEqual(baseline.threshold, 185.02)
        self.assertTrue(baseline.active(185.03, True))
        self.assertTrue(baseline.active(185.04, True))
        self.assertTrue(baseline.active(185.05, True))
        self.assertTrue(baseline.active(185.02, True))
        self.assertFalse(baseline.active(185.019, True))
        self.assertEqual(baseline.samples, [185.02, 185.04, 185.03, 185.03])

    def test_display_cent_boundaries(self):
        for value in (0., .01, 100., 185.03, 1022.99):
            baseline = RestBaseline()
            baseline.measure([value], True, 0.)
            baseline.measure([value], True, 3.)
            self.assertTrue(baseline.active(value, True))
            self.assertTrue(baseline.active(round(value+.01, 2), True))

    def test_missing_signal_restarts_measurement_and_never_activates(self):
        baseline = RestBaseline()
        baseline.measure([100.], True, 0.)
        baseline.measure([], False, 2.)
        baseline.measure([200.], True, 3.)
        baseline.measure([200.], True, 5.9)
        self.assertFalse(baseline.ready)
        baseline.measure([200.], True, 6.)
        self.assertEqual(baseline.baseline, 200.)
        self.assertFalse(baseline.active(900., False))

    def test_each_new_game_has_a_new_baseline(self):
        first = RestBaseline()
        first.measure([270.], True, 0.)
        first.measure([270.], True, 3.)
        second = RestBaseline()
        self.assertFalse(second.ready)
        second.measure([185.03], True, 5.)
        second.measure([185.03], True, 8.)
        self.assertTrue(second.active(185.04, True))

    def test_game_defers_music_and_ignores_old_falling_activation(self):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        from app.ui.game_widget import GameWidget
        app = QApplication.instance() or QApplication([])
        state = emg(False)
        state.emg_value = 185.03
        reader = SimpleNamespace(samples=[190., 184.991, 185.03], status='TEST EMG', threshold=262.132)
        fusion = SimpleNamespace(emg_reader=reader, read=lambda frame=None: (state, None),
                                 close=lambda: None, last_timing_error_ms=None, finger_states=None)
        player = MagicMock(error=None, finished=False, loading=False, position_ms=0, duration_seconds=20.)
        with patch('app.ui.game_widget.InputFusion', return_value=fusion), \
                patch('app.ui.game_widget.AudioPlayer', return_value=player):
            game = GameWidget(object(), song_path='test.wav', mode='emg')
            try:
                game.timer.stop()
                player.play.assert_not_called()
                with patch('app.ui.game_widget.time.monotonic', return_value=100.):
                    game.game_loop()
                with patch('app.ui.game_widget.time.monotonic', return_value=102.99):
                    game.game_loop()
                player.play.assert_not_called()
                self.assertEqual(game.engine.score_state.score, 0)
                with patch('app.ui.game_widget.time.monotonic', return_value=103.):
                    game.game_loop()
                player.play.assert_called_once()
                self.assertEqual(game.rest_baseline.threshold, 184.991)
                state.emg_value = 184.991
                state.emg_activated = False  # Old reader gate must not block new recognition.
                player.position_ms = 2000
                game.game_loop()
                self.assertTrue(game.current_input.emg_activated)
                self.assertEqual(game.engine.score_state.score, 0)
                hold = game.engine.notes[0]
                self.assertTrue(hold.holding)
                for stamp in range(2100, hold.end_time_ms+1, 100):
                    player.position_ms = stamp
                    game.game_loop()
                self.assertEqual(game.engine.score_state.score, 1000)
                self.assertFalse(game.grab().isNull())
                game.main_window = SimpleNamespace(show_result_screen=MagicMock())
                with patch('app.config.SAVE_SESSION_LOG', False):
                    game.finish_game()
                metrics = game.main_window.show_result_screen.call_args.args[0]
                self.assertEqual(metrics['emg_rest_baseline'], 184.991)
                self.assertEqual(metrics['emg_activation_delta'], 0.)
                self.assertEqual(metrics['emg_baseline_duration_seconds'], 3.)
                self.assertEqual(min(metrics['emg_baseline_samples']), 184.991)
            finally:
                game.close()
