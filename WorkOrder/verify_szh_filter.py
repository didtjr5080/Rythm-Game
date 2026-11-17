"""Validate the actual firmware coefficients against the sensor seller's response."""
import re
import unittest
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfreqz, sosfilt


class SzhFilterChecks(unittest.TestCase):
    def setUp(self):
        source = (Path(__file__).resolve().parents[1]/'firmware/esp8266_emg/szh_gjd001_filter.h').read_text()
        table = source.split('SZH_SOS[4][5] = {', 1)[1].split('};', 1)[0]
        rows = [[float(v) for v in re.findall(r'(-?\d+\.\d+)f', row)]
                for row in re.findall(r'\{([^{}]+)\}', table)]
        self.sos = np.array([[*r[:3], 1, *r[3:]] for r in rows])

    def test_seller_bandpass_response(self):
        expected = butter(4, [60, 100], fs=500, btype='bandpass', output='sos')
        np.testing.assert_allclose(self.sos, expected, atol=1e-8)
        _, response = sosfreqz(self.sos, worN=[0, 10, 80, 200], fs=500)
        self.assertGreater(abs(response[2]), .99)
        self.assertTrue(np.all(np.abs(response[[0, 1, 3]]) < .01))

    def test_dc_rejection_and_80hz_rms_amplitude(self):
        time = np.arange(5000)/500
        signal = 512+100*np.sin(2*np.pi*80*time)
        filtered = sosfilt(self.sos, signal)
        self.assertAlmostEqual(float(np.sqrt(np.mean(filtered[-1000:]**2))), 100/np.sqrt(2), delta=.2)
        self.assertLess(abs(float(np.mean(filtered[-1000:]))), .01)


if __name__ == '__main__':
    unittest.main()
