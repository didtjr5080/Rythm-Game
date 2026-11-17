"""Activity-envelope conditioning; input is already rectified by the sensor/firmware."""
import math
from collections import deque
from statistics import median


class ActivityFilter:
    def __init__(self):
        self.window = deque(maxlen=3)
        self.value = None

    def update(self, value):
        if not math.isfinite(value) or not 0 <= value <= 1023:
            raise ValueError('Invalid EMG activity sample')
        self.window.append(value)
        level = median(self.window)
        self.value = level if self.value is None else self.value + .4 * (level-self.value)
        return self.value


def calibration_thresholds(rest, contractions, recoveries):
    if not rest or len(contractions) != 3 or len(recoveries) != 3 or any(
            not block for block in (*contractions, *recoveries)):
        raise ValueError('측정값이 없는 구간이 있습니다. 연결을 확인하고 다시 측정하세요.')
    blocks = [rest, *recoveries, *contractions]
    if any(not math.isfinite(v) or not 0 <= v <= 1023 for block in blocks for v in block):
        raise ValueError('잘못된 EMG 숫자입니다. 연결을 확인하세요.')
    rest_level = median(median(block) for block in [rest, *recoveries])
    active_level = median(median(block) for block in contractions)
    difference = active_level-rest_level
    # Use the measured direction and levels directly, without a signal-quality gate.
    return round(rest_level+.6*difference, 3), round(rest_level+.2*difference, 3)
