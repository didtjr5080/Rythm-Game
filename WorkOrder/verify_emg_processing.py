"""Run: python -m unittest WorkOrder.verify_emg_processing"""
import unittest

from app.input.emg_processing import ActivityFilter, calibration_thresholds


class ProcessingChecks(unittest.TestCase):
    def test_isolated_spike_and_sustained_contraction(self):
        filt = ActivityFilter()
        for _ in range(10):
            self.assertEqual(filt.update(5), 5)
        self.assertEqual(filt.update(1023), 5)
        self.assertEqual(filt.update(5), 5)
        for _ in range(10):
            value = filt.update(100)
        self.assertGreater(value, 95)

    def test_invalid_samples(self):
        for value in (float('nan'), float('inf'), -1, 1024):
            with self.assertRaises(ValueError):
                ActivityFilter().update(value)

    def test_threshold_allows_release_and_contraction(self):
        rest, active = [8, 10, 12]*50, [75, 80, 85]*50
        threshold, release = calibration_thresholds(rest, [active]*3, [rest]*3)
        self.assertLess(max(rest), release)
        self.assertLess(release, threshold)
        self.assertLess(threshold, min(active))

    def test_high_rest_floor_does_not_require_zero_baseline(self):
        threshold, release = calibration_thresholds([300]*100, [[400]*100]*3, [[300]*100]*3)
        self.assertEqual((threshold, release), (360, 320))

    def test_refuses_only_missing_or_invalid_measurements(self):
        for rest, active in (([], [80]), ([float('nan')], [80]), ([-1], [80]), ([5], [1024])):
            with self.assertRaises(ValueError):
                calibration_thresholds(rest, [active]*3, [rest]*3)

    def test_small_measured_difference_is_applied(self):
        threshold, release = calibration_thresholds([8.4]*100, [[11.7]*80]*3, [[8.4]*80]*3)
        self.assertEqual((threshold, release), (10.38, 9.06))

    def test_noise_is_not_a_calibration_gate(self):
        self.assertEqual(calibration_thresholds([0, 8]*50, [[11.3]*80]*3, [[0, 8]*40]*3), (8.38, 5.46))

    def test_flat_falling_short_and_full_scale_measurements_are_applied(self):
        for rest, active, expected in ((8,8,(8,8)), (80,5,(35,65)), (1023,1023,(1023,1023))):
            self.assertEqual(calibration_thresholds([rest], [[active]]*3, [[rest]]*3), expected)

    def test_one_weak_repetition_is_not_rejected(self):
        self.assertEqual(calibration_thresholds([8]*100, [[12]*80,[12]*80,[8]*80], [[8]*80]*3), (10.4,8.8))


if __name__ == '__main__':
    unittest.main()
