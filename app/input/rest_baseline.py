"""Record 3.0 seconds; extension is a fresh value at or above the minimum."""
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
        self.baseline_value = None

    @property
    def ready(self):
        return self.baseline_cents is not None

    @property
    def baseline(self):
        if self.baseline_value is not None:
            return self.baseline_value
        return self.baseline_cents / 100 if self.ready else None

    @property
    def threshold(self):
        return self.baseline

    def measure(self, samples, fresh, now):
        if self.ready:
            return
        if not fresh:
            self.started_at = None
            self.samples.clear()
            return
        # A delayed UI tick must not add samples from after the 3.0s window.
        if self.started_at is not None and now-self.started_at > self.DURATION:
            self._finish()
            return
        values = [float(value) for value in samples]
        for value in values:
            cents(value)
        if values and self.started_at is None:
            self.started_at = now
        self.samples.extend(values)
        if self.started_at is not None and now-self.started_at >= self.DURATION and self.samples:
            self._finish()

    def _finish(self):
        if self.samples:
            self.baseline_value = min(self.samples)
            self.baseline_cents = cents(self.baseline_value)

    @classmethod
    def from_saved(cls, data):
        result = cls()
        values = [float(v) for v in data['samples']]
        for value in values: cents(value)
        if not values or min(values) != data['minimum'] or data['duration_seconds'] != cls.DURATION:
            raise ValueError('Invalid saved EMG baseline.')
        result.samples = values
        result._finish()
        return result

    def active(self, value, fresh):
        if not self.ready or not fresh:
            return False
        cents(value)  # Validate without rounding the value used for comparison.
        return float(value) >= self.threshold

    def remaining(self, now):
        return self.DURATION if self.started_at is None else max(0., self.DURATION-(now-self.started_at))
