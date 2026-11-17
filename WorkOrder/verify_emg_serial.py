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
    def packet(self, value, count=1):
        return self.send(('EMG1 raw:512 filtered:%d seq:1\n' % value).encode()*count)
    def test_requires_rest_and_confirmed_contraction(self):
        self.send(b'EMG_DEVICE:ESP8266_A0:1\n')
        self.assertFalse(self.packet(100, 10)[1])  # High at startup never arms.
        self.assertFalse(self.packet(5, 12)[1])  # Allow the activity filter to settle.
        self.assertFalse(self.packet(100)[1])  # Single spike rejected.
        self.assertTrue(self.packet(100, 3)[1])
        self.assertIn('ESP8266_A0 CONNECTED', self.reader.status)
        self.now += .16
        self.assertFalse(self.reader.read()[1])  # Frozen last sample cannot hit.
        self.assertFalse(self.packet(100, 4)[1])  # Resuming high cannot retrigger.
        self.assertFalse(self.packet(5)[1])
    def test_no_keyboard_fallback_when_unplugged(self):
        self.reader.set_space_pressed(True)
        self.wire.broken = True
        self.assertEqual(self.reader.read(), (0.0, False))
    def test_zero_threshold_never_activates(self):
        self.reader.threshold = 0
        self.packet(0, 4)
        self.assertFalse(self.packet(100, 4)[1])
    def test_partial_frame_and_raw_mode(self):
        self.reader.signal='raw'
        self.assertEqual(self.send(b'EMG1 raw:123 filtered:')[0],0)
        self.assertEqual(self.send(b'9 seq:1\n')[0],123)
    def test_filter_rejects_spike_and_samples_are_fresh_only(self):
        self.packet(5, 10)
        self.assertEqual(self.packet(1023)[0], 5)
        self.assertEqual(self.reader.samples, [5])
        self.reader.read()
        self.assertEqual(self.reader.samples, [])
        self.assertTrue(self.packet(100, 8)[1])
        self.assertGreater(self.reader.last_value, 90)
    def test_invalid_legacy_activity_disables_input(self):
        self.reader.requested_port = 'COM5'
        self.assertEqual(self.send(b'-10\n'), (0.0, False))
        self.assertIsNone(self.reader.serial)
    def test_szh_firmware_profile_and_raw_diagnostic_guard(self):
        self.send(b'EMG_DEVICE:ESP8266_A0:2\n')
        self.assertEqual(self.reader.firmware_version, 2)
        self.packet(5, 10)
        self.assertTrue(self.packet(100, 8)[1])
        self.assertIn('SZH-GJD001 60-100Hz RMS', self.reader.status)
        self.reader.signal = 'raw'
        self.assertFalse(self.packet(100, 8)[1])
        self.assertIn('RAW DIAGNOSTIC ONLY', self.reader.status)
        self.wire.broken = True
        self.reader.read()
        self.assertEqual(self.reader.firmware_version, 0)
    def test_calibrated_release_at_high_rest_floor(self):
        self.reader.set_thresholds(360, 320)
        self.assertFalse(self.packet(300, 12)[1])
        self.assertTrue(self.packet(400, 12)[1])
        self.assertTrue(self.packet(400, 12)[1])
        self.assertFalse(self.packet(300, 12)[1])
        self.assertTrue(self.packet(400, 12)[1])
        self.reader.set_thresholds(360)
        self.assertEqual(self.reader.release_level, 216)
        self.assertFalse(self.packet(300, 12)[1])
        self.assertFalse(self.packet(400, 12)[1])
    def test_falling_calibration_activates_on_decrease_then_rearms_on_rest(self):
        self.reader.set_thresholds(180, 195)
        self.assertTrue(self.reader.falling_activation)
        self.assertFalse(self.packet(200, 12)[1])
        self.assertTrue(self.packet(170, 12)[1])
        self.assertFalse(self.packet(200, 12)[1])
        self.assertTrue(self.packet(170, 12)[1])
        self.reader.set_thresholds(180)
        self.assertFalse(self.reader.falling_activation)
    def test_comparison_packets_do_not_mix_filtered_and_bypass_samples(self):
        self.reader.signal = 'unfiltered'
        self.send(b'EMG_DEVICE:ESP8266_A0:2\n')
        def frames(level, count):
            return self.send((f'EMG1 raw:512 filtered:300 seq:1\nEMG1_BYPASS rms:{level} seq:1\n'.encode())*count)
        self.assertFalse(frames(5, 12)[1])
        self.assertEqual(len(self.reader.samples), 12)
        self.assertEqual(self.reader.last_value, 5)
        self.assertEqual(self.reader.envelope_value, 300)
        self.assertTrue(self.reader.bypass_available)
        self.assertTrue(frames(100, 12)[1])
        self.assertIn('NO BANDPASS', self.reader.status)
        self.assertIsNone(self.reader._extract_value('EMG1_BYPASS rms:123 seq:1'))
    def test_bypass_requires_extension_and_never_uses_legacy_or_filtered_values(self):
        self.reader.signal = 'unfiltered'
        self.reader.requested_port = 'COM5'
        self.packet(100, 12)
        self.assertEqual(self.reader.samples, [])
        self.send(b'900\nEMG1_BYPASS rms:1024 seq:1\n')
        self.assertEqual(self.reader.samples, [])
        self.now += 4
        self.assertEqual(self.reader.read(), (0.0, False))
        self.assertIn('UPDATE COMPARISON FIRMWARE', self.reader.status)
    def test_filtered_mode_ignores_bypass_for_activation(self):
        self.packet(5, 12)
        self.assertFalse(self.send(b'EMG1_BYPASS rms:1000 seq:1\n'*12)[1])
        self.assertEqual(self.reader.samples, [])
        self.assertEqual(self.reader.last_value, 5)
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
                save_settings(dict(emg_signal='unfiltered'))
                self.assertEqual(load_settings()['emg_signal'], 'unfiltered')
                save_settings(dict(emg_threshold=360,emg_release_threshold=320))
                self.assertEqual(load_settings()['emg_release_threshold'],320)
                save_settings(dict(emg_threshold=10.38,emg_release_threshold=9.06))
                self.assertEqual(load_settings()['emg_threshold'],10.38)
                self.assertEqual(load_settings()['emg_release_threshold'],9.06)
                save_settings(dict(emg_threshold=180,emg_release_threshold=195))
                self.assertEqual(load_settings()['emg_release_threshold'],195)
                for release in (-1, 1024, 'broken', float('nan')):
                    save_settings(dict(emg_threshold=360,emg_release_threshold=release))
                    self.assertIsNone(load_settings()['emg_release_threshold'])


if __name__ == '__main__': unittest.main()
