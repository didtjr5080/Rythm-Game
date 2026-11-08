"""Framed serial parsing, device selection and reconnection without hardware."""
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.input.emg_reader import SerialEMGReader
from app.input.emg_devices import discover_emg_devices
from app.settings import load_settings, save_settings


def device(port='COM5', identity='usb:10c4:ea60:0001'):
    return dict(port=port, identity=identity, candidate=True, description='CP210x')


class Wire:
    def __init__(self):
        self.data = b''
        self.closed = False
        self.broken = False
    @property
    def in_waiting(self):
        if self.broken: raise OSError('unplugged')
        return len(self.data)
    def read(self, count):
        data, self.data = self.data[:count], self.data[count:]
        return data
    def write(self, data): return len(data)
    def close(self): self.closed = True


class SerialChecks(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.wire = Wire()
        self.ports = [device()]
        self.clock = patch('app.input.emg_reader.time.monotonic', side_effect=lambda:self.now)
        self.discovery = patch('app.input.emg_reader.discover_emg_devices', side_effect=lambda:self.ports)
        self.factory = patch('app.input.emg_reader.serial.Serial', return_value=self.wire)
        self.clock.start(); self.discovery.start(); self.open = self.factory.start()
        self.reader = SerialEMGReader(threshold=40)
    def tearDown(self):
        self.reader.close()
        self.factory.stop(); self.discovery.stop(); self.clock.stop()
    def send(self, text):
        self.wire.data += text
        return self.reader.read()
    def test_esp8266_and_peak_between_frames(self):
        value, active = self.send(b'EMG_DEVICE:ESP8266_A0:1\nEMG1 raw:520 filtered:60 seq:1\nEMG1 raw:512 filtered:5 seq:2\n')
        self.assertEqual(value,5); self.assertTrue(active)
        self.assertIn('ESP8266_A0 CONNECTED',self.reader.status)
        self.now += .2
        self.assertFalse(self.reader.read()[1])
    def test_partial_frame_and_raw_mode(self):
        self.reader.signal='raw'
        self.assertEqual(self.send(b'EMG1 raw:123 filtered:')[0],0)
        self.assertEqual(self.send(b'9 seq:1\n')[0],123)
    def test_invalid_and_identity_lines_not_samples(self):
        self.send(b'EMG_DEVICE:NANO_A0:1\nBOOT 999\nEMG1 raw:4095 filtered:3 seq:1\n')
        self.assertEqual(self.reader.last_value,0)
        self.assertIsNone(self.reader._extract_value('EMG_DEVICE:NANO_A0:1'))
        self.assertIsNone(self.reader.parse_packet('EMG1 raw:1 filtered:3 seq:x'))
    def test_disconnect_clears_activation_and_reconnects(self):
        self.send(b'EMG1 raw:500 filtered:100 seq:1\n')
        self.wire.broken=True
        self.assertFalse(self.reader.read()[1]); self.assertEqual(self.reader.last_value,0)
        self.now+=2
        self.wire=Wire()
        self.open.return_value=self.wire
        self.reader.read()
        self.assertIs(self.reader.serial,self.wire)
    def test_stale_samples_do_not_keep_activation(self):
        self.send(b'EMG1 raw:500 filtered:100 seq:1\n')
        self.now+=1.1
        self.assertFalse(self.reader.read()[1]); self.assertIsNone(self.reader.serial)
    def test_identity_follows_com_number(self):
        self.reader.close()
        self.ports=[device('COM12')]
        self.reader=SerialEMGReader(port='COM5',device_id='usb:10c4:ea60:0001')
        self.assertEqual(self.reader.port,'COM12')
    def test_same_com_number_wrong_identity_not_opened(self):
        self.reader.close(); self.open.reset_mock()
        self.ports=[device('COM5','usb:10c4:ea60:DIFFERENT')]
        self.reader=SerialEMGReader(port='COM5',device_id='usb:10c4:ea60:0001')
        self.open.assert_not_called()
    def test_no_data_auto_skips_incompatible_device(self):
        self.now+=4
        self.reader.read()
        self.assertIsNone(self.reader.serial)
        self.assertIn('NO COMPATIBLE',self.reader.status)
    def test_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('app.settings.settings_path',return_value=Path(folder)/'settings.json'):
                save_settings(dict(emg_port='COM5',emg_device_id='usb:10c4:ea60:0001',emg_signal='raw'))
                saved=load_settings()
                self.assertEqual(saved['emg_signal'],'raw'); self.assertEqual(saved['emg_port'],'COM5')


if __name__ == '__main__': unittest.main()
