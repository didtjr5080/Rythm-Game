"""Offscreen calibration persistence and manual override, without hardware."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from app.settings import DEFAULT_SETTINGS, save_settings
from app.input.emg_reader import SerialEMGReader
from app.ui.settings_screen import SettingsScreen
from WorkOrder.verify_emg_serial import Wire, device


class CalibrationUiChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_measured_levels_apply_without_quality_rejection(self):
        clock = [100.0]
        with patch('app.ui.settings_screen.discover_emg_devices', return_value=[]), \
             patch('app.ui.settings_screen.load_settings', return_value=dict(DEFAULT_SETTINGS)), \
             patch('app.input.emg_reader.discover_emg_devices', return_value=[device()]), \
             patch('app.input.emg_reader.serial.Serial', return_value=Wire()), \
             patch('time.monotonic', side_effect=lambda:clock[0]):
            screen = SettingsScreen(SimpleNamespace(show_start_screen=lambda:None))
            screen.device_timer.stop()
            reader = SerialEMGReader()
            screen.emg_signal_combo.setCurrentIndex(screen.emg_signal_combo.findData('unfiltered'))
            screen.emg_test_reader = reader
            reader.board_name, reader.firmware_version = 'ESP8266_A0', 2
            reader.signal = 'unfiltered'
            reader._last_sample = clock[0]
            screen.start_emg_calibration('rest')
            self.assertIsNone(screen.emg_calibration_phase)
            reader.bypass_available = True
            try:
                def measure(phase, value, recovery=300):
                    reader._last_sample = clock[0]
                    screen.start_emg_calibration(phase)
                    self.assertEqual(screen.emg_calibration_phase, phase)
                    started = clock[0]
                    for _ in range(190 if phase == 'rest' else 610):
                        clock[0] += .02
                        level = value if phase == 'rest' or int((clock[0]-started)//2)%2 else recovery
                        reader._last_sample, reader.samples = clock[0], [level]
                        screen.collect_emg_calibration(reader)
                    self.assertIsNone(screen.emg_calibration_phase)
                measure('rest', 300)
                measure('active', 400)
                self.assertEqual(screen.emg_threshold_slider.value(), 360)
                self.assertEqual(screen.emg_release_threshold, 320)
                self.assertEqual(reader.release_level, 320)
                measure('active', 300)
                self.assertEqual((reader.threshold, reader.release_level), (300, 300))
                self.assertIn('측정값 보정 적용', screen.emg_calibration_status.text())
                measure('active', 200)
                self.assertEqual((reader.threshold, reader.release_level), (240, 280))
                self.assertTrue(reader.falling_activation)
                measure('rest', 8.4)
                measure('active', 11.7, recovery=8.4)
                self.assertEqual(screen.emg_threshold_slider.value(), 10.38)
                self.assertEqual(reader.release_level, 9.06)
                with patch('app.ui.settings_screen.save_settings') as save:
                    screen.save_and_back()
                    self.assertEqual(save.call_args.args[0]['emg_threshold'], 10.38)
                    self.assertEqual(save.call_args.args[0]['emg_release_threshold'], 9.06)
                screen.emg_threshold_slider.setValue(350)
                self.assertIsNone(screen.emg_release_threshold)
            finally:
                screen.stop_emg_test()
                screen.close()

    def test_game_reader_receives_saved_release_level(self):
        from app.input.input_fusion import InputFusion
        settings = dict(DEFAULT_SETTINGS, emg_threshold=360, emg_release_threshold=320)
        with patch('app.settings.load_settings', return_value=settings), \
             patch('app.input.emg_reader.discover_emg_devices', return_value=[]):
            fusion = InputFusion(use_camera=False, use_mock_emg=False, emg_threshold=360)
            try:
                self.assertEqual(fusion.emg_reader.release_level, 320)
            finally:
                fusion.close()

    def test_game_widget_keeps_fractional_calibration(self):
        from app.ui.game_widget import GameWidget
        settings = dict(DEFAULT_SETTINGS, emg_threshold=180.38, emg_release_threshold=195.06, camera_enabled=False)
        with patch('app.ui.game_widget.load_settings', return_value=settings), \
             patch('app.settings.load_settings', return_value=settings), \
             patch('app.ui.game_widget.config.USE_CAMERA', False), \
             patch('app.ui.game_widget.open_live_video', return_value=MagicMock()), \
             patch('app.ui.game_widget.AudioPlayer'), \
             patch('app.ui.game_widget.SessionLogger'), \
             patch('app.input.emg_reader.discover_emg_devices', return_value=[]):
            game = GameWidget(SimpleNamespace())
            game.timer.stop()
            try:
                self.assertEqual(game.input_fusion.emg_reader.threshold, 180.38)
                self.assertEqual(game.input_fusion.emg_reader.release_level, 195.06)
                self.assertTrue(game.input_fusion.emg_reader.falling_activation)
            finally:
                game.close()

    def test_saved_values_stay_unchanged_and_hud_shows_activity_not_percent(self):
        from app.ui.game_widget import GameWidget
        from PyQt6.QtGui import QImage, QPainter
        with tempfile.TemporaryDirectory() as folder, \
             patch('app.settings.settings_path', return_value=Path(folder)/'settings.json'), \
             patch('app.ui.game_widget.config.USE_CAMERA', False), \
             patch('app.ui.game_widget.open_live_video', return_value=MagicMock()), \
             patch('app.ui.game_widget.AudioPlayer'), \
             patch('app.ui.game_widget.SessionLogger'), \
             patch('app.input.emg_reader.discover_emg_devices', return_value=[]):
            for threshold, release in ((39.544,38.552),(180.38,195.06)):
                save_settings(dict(DEFAULT_SETTINGS,emg_threshold=threshold,emg_release_threshold=release,
                                   camera_enabled=False,show_camera_debug=False))
                before = (Path(folder)/'settings.json').read_bytes()
                game = GameWidget(SimpleNamespace())
                game.timer.stop()
                try:
                    self.assertEqual(game.input_fusion.emg_reader.threshold,threshold)
                    self.assertEqual(game.input_fusion.emg_reader.release_level,release)
                    game.current_input.emg_value = 200
                    game.current_input.emg_activated = False
                    canvas = QImage(1280,720,QImage.Format.Format_ARGB32)
                    painter = QPainter(canvas)
                    try:
                        with patch('app.ui.game_widget.draw_circular_gauge') as gauge, \
                             patch.object(game,'_draw_score_hud'):
                            game._draw_lab_hud(painter)
                            self.assertEqual(gauge.call_args.args[2:],(0.0,'200.00','REST'))
                    finally:
                        painter.end()
                    self.assertEqual((Path(folder)/'settings.json').read_bytes(),before)
                finally:
                    game.close()


if __name__ == '__main__':
    unittest.main()
