"""python -m unittest docs.check_pinch_switch -v"""
import itertools
import unittest

from app.input.pinch_classifier import HandSample, NAMES, PinchClassifier


def hand(ratios, stamp):
    return HandSample(1, stamp, 1, 'RIGHT', (0, 0, 0), 80,
                      [(0, 0, 0)] + [(v * 80, 0, 0) for v in ratios], [],
                      [[(0, 0, 0), (0, 1, 0), (0, 2, 0)]] * 5)


class PinchSwitchChecks(unittest.TestCase):
    def test_every_direct_switch_default_and_personal(self):
        for thresholds in (dict.fromkeys(NAMES, .36), dict.fromkeys(NAMES, .52),
                           dict(zip(NAMES, (.32, .52, .42, .60)))):
            for old, new in itertools.permutations(range(4), 2):
                with self.subTest(thresholds=thresholds, old=old, new=new):
                    model = PinchClassifier(thresholds)
                    ratios = [1.2] * 4
                    ratios[old] = .1
                    model.step(hand(ratios, 1.))
                    self.assertEqual(model.step(hand(ratios, 1.1))[0], NAMES[old])
                    ratios[old] = thresholds[NAMES[old]] * 1.1  # Still inside old release band.
                    ratios[new] = .1
                    current, candidate, _ = model.step(hand(ratios, 1.11))
                    self.assertEqual(candidate, NAMES[new])
                    self.assertEqual(current, NAMES[new])  # No open hand or 90ms wait.

    def test_ambiguous_fingers_keep_previous_pinch(self):
        model = PinchClassifier()
        model.step(hand([.1, 1., 1., 1.], 1.))
        model.step(hand([.1, 1., 1., 1.], 1.1))
        self.assertEqual(model.step(hand([.2, .21, 1., 1.], 1.11))[0], 'INDEX')

    def test_entry_release_and_tracking_loss(self):
        model = PinchClassifier()
        self.assertEqual(model.step(hand([.1, 1., 1., 1.], 1.))[0], 'NONE')
        self.assertEqual(model.step(hand([.1, 1., 1., 1.], 1.1))[0], 'INDEX')
        model.step(hand([1., 1., 1., 1.], 1.2))
        self.assertEqual(model.step(hand([1., 1., 1., 1.], 1.3))[0], 'NONE')
        self.assertEqual(model.step(None)[0], 'LOST')
        self.assertEqual(model.step(hand([1., .1, 1., 1.], 1.4))[0], 'NONE')
