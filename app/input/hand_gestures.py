"""Debounced fold gestures; a double fold never emits its first single click."""


class FoldGestures:
    OPEN_SECONDS = .09
    CLOSE_SECONDS = .08
    DOUBLE_SECONDS = .45

    def __init__(self):
        self.reset()

    def reset(self):
        self.scrolling = False
        self._armed = False
        self._open_since = self._closed_since = None
        self._pending = None

    @property
    def waiting_for_second_fold(self):
        return self._pending is not None

    def advance(self, now):
        if self._pending is not None and now >= self._pending[0]:
            _, point = self._pending
            self._pending = None
            if not self.scrolling:
                return 'click', point
        return None

    def feed(self, count, closed, now, point):
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
                if self._pending is not None:
                    self._pending = None
                    self.scrolling = not self.scrolling
                    return 'scroll', point
                self._pending = (now+self.DOUBLE_SECONDS, point)
        else:
            self._open_since = self._closed_since = None
        return None
