"""python -m unittest docs.check_oymotion -v"""
import ctypes as C
import math
import struct
import threading
import time
import unittest
from unittest.mock import patch

from app.input.oymotion_activity import OYMotionActivity
from app.input.oymotion_reader import OYMotionReader
from app.input.rest_baseline import RestBaseline


def packet(rows):
    return struct.pack('<'+'H'*(len(rows)*8), *(v for row in rows for v in row))


class OYMotionChecks(unittest.TestCase):
    def test_12bit_decode_and_malformed_packets(self):
        row = tuple((0, 1024, 2048, 3072, 4095, 1, 1234, 3456))
        self.assertEqual(OYMotionActivity.decode(packet([row])), [row])
        for raw in (b'', b'\0'*15, b'\0'*17, packet([(4096,)*8])):
            with self.assertRaises(ValueError):
                OYMotionActivity.decode(raw)

    def test_per_channel_dc_is_removed(self):
        processor = OYMotionActivity()
        output = processor.feed(packet([(100, 500, 1000, 1500, 2000, 2500, 3000, 4000)]*50))
        self.assertEqual(output, [0.])
        self.assertEqual(processor.channel_rms, (0.,)*8)

    def test_all_channels_contribute_without_cancelling(self):
        for channel in range(8):
            rows = []
            for index in range(50):
                row = [2048]*8
                row[channel] += 100 if index % 2 else -100
                rows.append(row)
            processor = OYMotionActivity()
            self.assertAlmostEqual(processor.feed(packet(rows))[-1], 100/math.sqrt(8))
            self.assertEqual(processor.channel_rms[channel], 100.)
        rows = [[2048+(100 if (i+channel)%2 else -100) for channel in range(8)] for i in range(50)]
        self.assertEqual(OYMotionActivity().feed(packet(rows))[-1], 100.)

    def test_every_sample_and_batch_boundary_are_preserved(self):
        rows = [[2048+(100 if i%2 else -100)]*8 for i in range(80)]
        entire = OYMotionActivity()
        expected = entire.feed(packet(rows))
        batched = OYMotionActivity()
        actual = []
        for i in range(0, 80, 8): actual.extend(batched.feed(packet(rows[i:i+8])))
        self.assertEqual(actual, expected)
        self.assertEqual(batched.sample_count, 80)
        self.assertEqual(len(actual), 4)

    def test_activity_above_old_10bit_limit_is_supported(self):
        rows = [[4095 if i%2 else 0]*8 for i in range(50)]
        value = OYMotionActivity().feed(packet(rows))[-1]
        self.assertEqual(value, 2047.5)
        baseline = RestBaseline()
        baseline.measure([value], True, 0.)
        baseline.measure([value], True, 3.)
        self.assertTrue(baseline.active(2047.51, True))

    def test_sdk_commands_acknowledgements_and_fresh_data(self):
        class SDK:
            calls = []
            def __init__(self, events):
                self.events = events
                self.dll = self
                self.result_type = lambda callback: callback
                self.sent = False
            def open(self, port): self.calls.append(('open', port))
            def hub_run(self, timeout):
                if not self.sent:
                    self.sent = True
                    self.events._found[1] = ('gForcePro+', 'test')
                    self.events.on_connected(1)
                    buffer = C.create_string_buffer(packet([[2048+(-100 if i%2 else 100)]*8 for i in range(64)]))
                    self.events.on_data(1, 8, 1024, C.addressof(buffer))
                time.sleep(.001)
                return 0
            def device_enable_data_notification(self, handle, enabled):
                self.calls.append(('notify', enabled)); return 0
            def device_set_emg_config(self, handle, rate, mask, length, bits, callback):
                self.calls.append(('config', rate, mask, length, bits))
                callback(handle, 0); return 0
            def device_set_data_switch(self, handle, flags, callback):
                self.calls.append(('switch', flags)); callback(handle, 0); return 0
            def device_disconnect(self, handle): return 0
            def close(self): self.calls.append(('close',))
            def check(self, result, operation):
                if result: raise RuntimeError(operation)
        with patch('app.input.oymotion_reader.OYMotionSDK', SDK):
            reader = OYMotionReader(port='COM4')
            try:
                deadline = time.monotonic()+2
                while not reader.sample_count and time.monotonic()<deadline: time.sleep(.005)
                self.assertIn(('config', 500, 255, 128, 12), SDK.calls)
                self.assertIn(('switch', 128), SDK.calls)
                self.assertTrue(reader.verified)
                self.assertEqual(reader.sample_count, 64)
                self.assertEqual(reader.read()[0], 100.)
                self.assertTrue(reader.signal_fresh)
                self.assertEqual(reader.channel_rms, (100.,)*8)
                reader.on_disconnected(1, 0)
                self.assertFalse(reader.signal_fresh)
            finally:
                reader.close()

    def test_configuration_failure_does_not_enable_raw_decoding(self):
        reader = OYMotionReader.__new__(OYMotionReader)
        reader._stop = threading.Event()
        reader._configured = False
        reader.sdk = type('SDK', (), {'check': staticmethod(lambda code, operation: (_ for _ in ()).throw(RuntimeError(operation)))})()
        reader._config_done(1, 4)
        self.assertTrue(reader._stop.is_set())
        self.assertFalse(reader._configured)
