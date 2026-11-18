"""Three seconds of fresh rest samples, then one displayed cent above the mean."""
import math
from decimal import Decimal, ROUND_HALF_UP


def cents(value):
    if not math.isfinite(value) or not 0 <= value <= 4095:
        raise ValueError('Invalid EMG sample.')
    return int(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) * 100)


class RestBaseline:
    DURATION = 3.

    def __init__(self):
        self.started_at = None
        self.samples = []
        self.baseline_cents = None

    @property
    def ready(self):
        return self.baseline_cents is not None

    @property
    def baseline(self):
        return self.baseline_cents / 100 if self.ready else None

    @property
    def threshold(self):
        return (self.baseline_cents + 1) / 100 if self.ready else None

    def measure(self, samples, fresh, now):
        if self.ready:
            return
        if not fresh:
            self.started_at = None
            self.samples.clear()
            return
        for value in samples:
            cents(value)
        if samples and self.started_at is None:
            self.started_at = now
        self.samples.extend(samples)
        if self.started_at is not None and now-self.started_at >= self.DURATION and self.samples:
            self.baseline_cents = cents(math.fsum(self.samples)/len(self.samples))
            self.samples.clear()

    def active(self, value, fresh):
        return bool(self.ready and fresh and cents(value) >= self.baseline_cents + 1)

    def remaining(self, now):
        return self.DURATION if self.started_at is None else max(0., self.DURATION-(now-self.started_at))
