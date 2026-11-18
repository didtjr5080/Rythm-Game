"""python -m unittest docs.check_menu_camera -q; camera lifecycle uses fake workers."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
from PyQt6.QtCore import QPointF
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication,QDialog
from app.settings import DEFAULT_SETTINGS
from app.ui.main_window import MainWindow
from app.ui.game_widget import GameWidget
from app.ui.result_screen import ResultScreen


class ThreadFlag:
    alive=True
    def is_alive(self): return self.alive
    def join(self,timeout=None): self.alive=False


class CameraWorker:
    status='FAKE MEDIAPIPE CAMERA'
    diagnostic_summary='FAKE MEDIAPIPE READY'
    last_error=None
    def __init__(self,settings,enabled=True):
        self._thread=ThreadFlag()
        self.hold_close=False
        self.closed=False
    def set_flip(self,flip): pass
    def hand_sample(self): return None
    def close(self):
        self.closed=True
        if not self.hold_close: self._thread.alive=False


class MenuCameraChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        tracker=Mock(status='TEST LEAP',last_error=None)
        tracker.track.return_value={'hand_visible':False,'lane':None}
        self.patches=[patch('app.config.USE_MOCK_EMG',True),
            patch('app.ui.main_window.load_settings',return_value=dict(DEFAULT_SETTINGS,camera_enabled=True)),
            patch('app.input.video_session.LiveVideoWorker',CameraWorker),
            patch('app.input.input_fusion.LeapPinchTracker',return_value=tracker),
            patch('app.ui.result_screen.ResultScreen._save_result',lambda screen:setattr(screen,'result_path',Path('test-result.json')))]
        for item in self.patches:item.start()
        self.window=MainWindow()

    def tearDown(self):
        self.window.close()
        for item in reversed(self.patches):item.stop()

    def test_all_navigation_pages_attach_and_share_camera(self):
        window=self.window
        first=window.video_session._worker
        for navigate in (window.show_game_selection,window.show_settings_screen,
                         window.show_results_browser_screen,lambda:window.show_result_screen({}),window.show_start_screen):
            navigate()
            self.assertIs(window.hand_cursor.screen,window.centralWidget())
            self.assertIsNotNone(window._navigation_video)
            self.assertIs(window.video_session._worker,first)
            self.assertTrue(window.hand_cursor.timer.isActive())

    def test_game_waits_for_worker_exit_then_result_resumes_camera(self):
        window=self.window
        window.show_game_selection()
        old=window.video_session._worker
        old.hold_close=True
        window.show_game_widget('emg')
        self.assertTrue(old.closed)
        self.assertFalse(isinstance(window.centralWidget(),GameWidget))
        self.assertIsNone(window.hand_cursor.screen)
        QTest.qWait(40)
        self.assertFalse(isinstance(window.centralWidget(),GameWidget))
        old._thread.alive=False
        QTest.qWait(70)
        game=window.centralWidget()
        self.assertIsInstance(game,GameWidget)
        game.timer.stop()
        self.assertTrue(window.video_session.is_stopped)
        self.assertIsNone(window._navigation_video)
        self.assertIsNone(window.hand_cursor.screen)
        self.assertIsNone(game.input_fusion.tracker)
        self.assertIsNotNone(game.input_fusion.emg_reader)
        game.close()
        window.show_result_screen({})
        self.assertIsInstance(window.centralWidget(),ResultScreen)
        self.assertIs(window.hand_cursor.screen,window.centralWidget())
        self.assertIsNotNone(window._navigation_video)

    def test_pinch_calibration_cancel_reopens_menu_camera(self):
        window=self.window
        window.show_game_selection()
        old=window.video_session._worker
        with patch('app.ui.main_window.LeapCalibrationDialog') as dialog:
            dialog.return_value.exec.return_value=QDialog.DialogCode.Rejected
            window.show_game_widget('pinch')
        self.assertTrue(old.closed)
        self.assertFalse(isinstance(window.centralWidget(),GameWidget))
        self.assertIsNotNone(window._navigation_video)
        self.assertIs(window.hand_cursor.screen,window.centralWidget())

    def test_camera_disabled_setting_does_not_start_menu_worker(self):
        with patch('app.ui.main_window.load_settings',return_value=dict(DEFAULT_SETTINGS,camera_enabled=False)):
            self.window.show_game_selection()
            self.assertIsNone(self.window._navigation_video)
            self.assertIsNone(self.window.hand_cursor.screen)

    def test_hand_click_on_mode_card_finishes_release_before_game_transition(self):
        window=self.window
        window.show_game_selection()
        self.app.processEvents()
        screen=window.centralWidget()
        old=window.video_session._worker
        cursor=window.hand_cursor
        cursor.timer.stop()
        button=screen.mode_buttons['emg']
        cursor.position=QPointF(button.mapTo(screen,button.rect().center()))
        with patch.object(cursor,'_can_control',return_value=True):
            cursor._click(cursor.position)
            self.assertIs(window.centralWidget(),screen)
            self.assertFalse(old.closed)
            QTest.qWait(60)
        self.assertIsInstance(window.centralWidget(),GameWidget)
        window.centralWidget().timer.stop()
        self.assertTrue(old.closed)
        self.assertTrue(window.video_session.is_stopped)
