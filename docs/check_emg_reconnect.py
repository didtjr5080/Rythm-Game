"""python -m unittest docs.check_emg_reconnect -q"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from app.input.emg_session import EMGSession
from app.input.oymotion_sdk import OYMotionSDK
from app.settings import DEFAULT_SETTINGS
from docs.check_emg_assistance import FakeSerialReader


class ReconnectChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_failed_reader_is_replaced_even_with_identical_settings(self):
        session = EMGSession(serial_factory=FakeSerialReader)
        try:
            first = session.acquire(DEFAULT_SETTINGS,use_mock_emg=False)
            old = first.reader
            old.error = 'USB init failed'
            second = session.acquire(DEFAULT_SETTINGS,use_mock_emg=False)
            self.assertIsNot(second.reader,old)
            self.assertIsNone(old.serial)
            self.assertFalse(first.signal_fresh)
            self.assertEqual(first.read(),(0.,False))
            third = session.acquire(DEFAULT_SETTINGS,use_mock_emg=False)
            self.assertIs(third.reader,second.reader)
        finally:
            session.shutdown()

    def sdk(self):
        sdk = OYMotionSDK.__new__(OYMotionSDK)
        sdk.dll = Mock()
        sdk.initialized = sdk.registered = False
        return sdk

    def test_no_ports_or_outdated_com_reports_missing_port_before_sdk_init(self):
        for ports,port in (([],0),([SimpleNamespace(device='COM7')],4)):
            sdk = self.sdk()
            with patch('app.input.oymotion_sdk.comports',return_value=ports):
                with self.assertRaisesRegex(RuntimeError,'not detected'):
                    sdk.open(port)
            sdk.dll.hub_instance.assert_not_called()

    def test_visible_com_still_reports_native_error_without_asserting_its_cause(self):
        sdk = self.sdk()
        sdk.listener = __import__('ctypes').c_int()
        sdk.dll.hub_instance.return_value = 0
        sdk.dll.hub_register_listener.return_value = 0
        sdk.dll.hub_init.return_value = 1
        with patch('app.input.oymotion_sdk.comports',return_value=[SimpleNamespace(device='COM7')]):
            with self.assertRaisesRegex(RuntimeError,'code 1'):
                sdk.open(7)
        sdk.dll.hub_init.assert_called_once_with(7)
