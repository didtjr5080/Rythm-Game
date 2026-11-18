"""python -m unittest docs.check_emg_assistance -v"""
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.emg_processing import ActivityFilter, calibration_thresholds
from app.input.emg_session import EMGSession
from app.settings import DEFAULT_SETTINGS
from docs.check_game_modes import emg


class FakeSerialReader:
    opened = 0

    def __init__(self, port, baudrate, threshold, device_id, signal, release_threshold):
        type(self).opened += 1
        self.serial = object()
        self.port = 'COM7'
        self.requested_port, self.device_id = port, device_id
        self.connected_identity = 'TEST_USB'
        self.threshold, self.release_threshold = threshold, release_threshold
        self.signal = signal
        self._last_sample = time.monotonic()
        self.filter = ActivityFilter()
        self.level = 20.
        self.raw_value = 20.
        self.verified = True
        self.status = 'TEST EMG'
        self.board_name = 'TEST'
        self.bypass_available = False
        self.samples = []

    @property
    def release_level(self):
        return self.release_threshold if self.release_threshold is not None else self.threshold*.6

    @property
    def falling_activation(self):
        return self.release_level > self.threshold

    def read(self):
        value = self.filter.update(self.level)
        self._last_sample = time.monotonic()
        self.samples = [value]
        return value, value >= self.threshold

    def set_thresholds(self, threshold, release=None):
        self.threshold, self.release_threshold = threshold, release

    def set_space_pressed(self, pressed):
        pass

    def close(self):
        self.serial = None


class EMGAssistanceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        FakeSerialReader.opened = 0
        self.settings = dict(DEFAULT_SETTINGS, emg_input_mode='serial', emg_port='auto',
                             emg_device_id='', emg_threshold=12., emg_release_threshold=8.)
        self.session = EMGSession(serial_factory=FakeSerialReader)

    def tearDown(self):
        self.session.shutdown()

    def test_screen_switch_preserves_port_filter_value_and_usb_identity(self):
        first = self.session.acquire(self.settings, use_mock_emg=False)
        reader = first.reader
        reader.level = 40.
        self.session.poll()
        first_value = first.read()
        second = self.session.acquire(dict(self.settings, emg_device_id='TEST_USB'), use_mock_emg=False)
        self.assertIs(reader, second.reader)
        self.assertEqual(FakeSerialReader.opened, 1)
        self.assertEqual(first_value, second.read())
        self.assertIs(reader.filter, second.reader.filter)
        first.close()
        self.assertIsNotNone(reader.serial)
        self.assertTrue(second.signal_fresh)

    def test_source_change_reopens_and_invalidates_old_lease(self):
        settings = dict(self.settings, emg_backend='legacy')
        first = self.session.acquire(settings, use_mock_emg=False)
        second = self.session.acquire(dict(settings, emg_signal='raw'), use_mock_emg=False)
        self.assertEqual(FakeSerialReader.opened, 2)
        self.assertEqual(first.read(), (0., False))
        self.assertFalse(first.signal_fresh)
        self.assertEqual(second.reader.signal, 'raw')

    def test_mock_reuse_keeps_activity_with_saved_release_threshold(self):
        first = self.session.acquire(self.settings, use_mock_emg=True)
        first.set_space_pressed(True)
        before = first.read()
        first.close()
        second = self.session.acquire(self.settings, use_mock_emg=True)
        self.assertEqual(second.read(), before)
        self.assertTrue(before[1])

    def test_samples_are_consumed_once_per_consumer_and_stale_signal_is_inactive(self):
        first = self.session.acquire(self.settings, use_mock_emg=False)
        second = self.session.acquire(self.settings, use_mock_emg=False)
        self.session.poll()
        first.read()
        self.assertEqual(len(first.samples), 1)
        first.read()
        self.assertEqual(first.samples, [])
        second.read()
        self.assertEqual(len(second.samples), 1)
        second.reader._last_sample = time.monotonic()-1
        self.assertFalse(second.read()[1])

    def test_weaker_calibration_for_both_signal_directions(self):
        self.assertEqual(calibration_thresholds([10.]*5, [[20.]*5]*3, [[10.]*5]*3), (13.5, 11.))
        self.assertEqual(calibration_thresholds([20.]*5, [[10.]*5]*3, [[20.]*5]*3), (16.5, 19.))

    def test_wider_emg_windows(self):
        for stamp, expected in ((649, None), (650, 'GOOD'), (850, 'PERFECT'),
                                (1150, 'PERFECT'), (1151, 'GOOD'), (1350, 'GOOD'), (1351, 'MISS')):
            engine = RhythmGameEngine([Note(0,0,1000)], mode='emg')
            self.assertEqual(engine.update(emg(True), stamp), expected)

    def test_short_dip_recovers_without_restarting_hold(self):
        engine = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
        engine.update(emg(True), 1000)
        for stamp in range(1100, 1500, 100):
            self.assertIsNone(engine.update(emg(False), stamp))
        for stamp in range(1500, 3000, 100):
            self.assertIsNone(engine.update(emg(True), stamp))
        self.assertEqual(engine.update(emg(True), 3000), 'PERFECT')

    def test_signal_loss_never_uses_dropout_grace(self):
        engine = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
        engine.update(emg(True), 1000)
        missing = emg(False)
        missing.emg_signal_fresh = False
        self.assertEqual(engine.update(missing, 1100), 'MISS')

    def test_audio_end_does_not_cut_off_final_hold_grace(self):
        from app.ui.game_widget import GameWidget
        with patch('app.config.USE_MOCK_EMG', True):
            game = GameWidget(object(), mode='emg')
            try:
                game.timer.stop()
                game.rest_baseline.baseline_cents = 0
                game.audio_player.stop()
                game.song_path = 'test-song.wav'
                game.audio_player = SimpleNamespace(error=None, finished=True, position_ms=3000, stop=lambda: None)
                game.engine = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
                game.engine.notes[0].holding = True
                with patch('app.ui.game_widget.time.monotonic', return_value=100.):
                    self.assertEqual(game._playback_time_ms(), 3000)
                with patch('app.ui.game_widget.time.monotonic', return_value=100.2):
                    self.assertGreaterEqual(game._playback_time_ms(), 3199)
                self.assertFalse(game._should_finish(3000))
                self.assertTrue(game._should_finish(3401))
            finally:
                game.close()

    def test_manual_emg_calibration_is_removed(self):
        from app.ui.settings_screen import SettingsScreen
        owner = SimpleNamespace(emg_session=self.session)
        with patch('app.config.USE_MOCK_EMG', False), \
                patch('app.ui.settings_screen.discover_emg_devices', return_value=[]), \
                patch('app.ui.settings_screen.load_settings', return_value=self.settings), \
                patch('app.ui.settings_screen.save_settings', side_effect=lambda data: data) as save:
            screen = SettingsScreen(owner)
            try:
                self.assertFalse(hasattr(screen, 'collect_emg_calibration'))
                self.assertFalse(hasattr(screen, 'start_emg_calibration'))
                self.assertTrue(screen.emg_threshold_slider.isHidden())
                save.assert_not_called()
            finally:
                screen.device_timer.stop()
                screen.stop_emg_test()
                screen.close()
