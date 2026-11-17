"""Fist clicks and two-finger wrist-tilt scrolling."""
import math
from statistics import median


class WristTilt:
    def __init__(self):
        self.reset()

    def reset(self):
        self.reference = None
        self.direction = 0
        self.samples = []

    def feed(self, points, count, now):
        if count != 2:
            self.direction = 0
            self.samples = []
            return 0
        try:
            if points is None or len(points) != 21:
                raise ValueError()
            palm = [sum(points[i][axis] for i in (5,9,13,17))/4-points[0][axis] for axis in range(3)]
            if not all(math.isfinite(v) for v in palm) or math.sqrt(sum(v*v for v in palm)) < 1e-6:
                raise ValueError()
            angle = math.degrees(math.atan2(palm[2],math.hypot(palm[0],palm[1])))
        except (ValueError, TypeError, IndexError):
            self.reset()
            return 0
        if self.reference is None:
            self.samples.append((now,angle))
            angles = [sample[1] for sample in self.samples]
            if max(angles)-min(angles) > 8:
                self.samples = [(now,angle)]
            elif now-self.samples[0][0] >= .4 and len(self.samples) >= 4:
                self.reference = median(angles)
                self.samples = []
            return 0
        delta = angle-self.reference
        if delta >= 15:
            self.direction = -1  # Palm faces camera: extension moves finger bases away.
        elif delta <= -15:
            self.direction = 1
        elif abs(delta) <= 8:
            self.direction = 0
        return self.direction


class FoldGestures:
    OPEN_SECONDS = .09
    CLOSE_SECONDS = .08
    CLICK_DELAY_SECONDS = .45

    def __init__(self):
        self.reset()

    def reset(self):
        self.scrolling = False
        self._armed = False
        self._open_since = self._closed_since = None
        self._pending = None
        self._scroll_since = None
        self.scroll_direction = self._candidate_direction = 0

    @property
    def waiting_for_second_fold(self):
        return self._pending is not None

    def advance(self, now):
        if self._scroll_since is not None:
            return None
        if self._pending is not None and now >= self._pending[0]:
            _, point = self._pending
            self._pending = None
            if not self.scrolling:
                return 'click', point
        return None

    def feed(self, count, closed, now, point, scroll_direction=0):
        if count == 2 and scroll_direction:
            self._open_since = self._closed_since = None
            if self._scroll_since is None or scroll_direction != self._candidate_direction:
                self._scroll_since = now
                self._candidate_direction = scroll_direction
            if self.scrolling and scroll_direction != self.scroll_direction:
                self.scrolling = False
                self.scroll_direction = 0
                return 'scroll', point
            if not self.scrolling and now-self._scroll_since >= self.OPEN_SECONDS:
                self._pending = None
                self._armed = False
                self.scrolling = True
                self.scroll_direction = scroll_direction
                return 'scroll', point
            return None
        self._scroll_since = None
        self._candidate_direction = 0
        if self.scrolling:
            self.scrolling = False
            self.scroll_direction = 0
            self._armed = False
            self._open_since = self._closed_since = None
            return 'scroll', point
        expired = self.advance(now)
        if expired is not None:
            return expired
        if count is not None and count >= 3:
            self._closed_since = None
            if self._open_since is None:
                self._open_since = now
            if now-self._open_since >= self.OPEN_SECONDS:
                self._armed = True
        elif closed:
            self._open_since = None
            if self._closed_since is None:
                self._closed_since = now
            if self._armed and now-self._closed_since >= self.CLOSE_SECONDS:
                self._armed = False
                if self._pending is None:
                    self._pending = (now+self.CLICK_DELAY_SECONDS, point)
        else:
            self._open_since = self._closed_since = None
        return None
