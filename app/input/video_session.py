"""Reuse one native camera across GUI pages without delaying the GUI on close."""
from PyQt6.QtCore import QObject, QTimer

from app.input.live_video import LiveVideoWorker
from app.input.mediapipe_tracker import MediaPipeHandTracker


class VideoLease:
    def __init__(self, session, worker):
        self._session, self._worker = session, worker
        self._closed = False

    def __getattr__(self, name):
        return getattr(self._worker, name)

    def read(self):
        return None if self._closed else self._worker.read()

    def track(self, frame):
        return MediaPipeHandTracker._empty_result(None) if self._closed else self._worker.track(frame)

    def hand_sample(self):
        return None if self._closed else self._worker.hand_sample()

    def close(self):
        if not self._closed:
            self._closed = True
            self._session.release(self._worker)

    release = close


class VideoSession(QObject):
    IDLE_MS = 500

    def __init__(self, parent=None, worker_factory=None):
        super().__init__(parent)
        self._factory = worker_factory or LiveVideoWorker
        self._worker = self._key = None
        self._leases = 0
        self._retiring = []
        self._idle = QTimer(self)
        self._idle.setSingleShot(True)
        self._idle.timeout.connect(self.stop)

    def acquire(self, settings, enabled=True):
        self._idle.stop()
        key = (bool(enabled and settings.get('camera_enabled', True)),
               settings.get('camera_index', 0), settings.get('camera_resolution', '1280x720'))
        thread = getattr(self._worker, '_thread', None)
        finished = thread is not None and not thread.is_alive()
        if self._worker is None or self._key != key or finished:
            self.stop()
            self._worker = self._factory(settings, enabled=enabled)
            self._key = key
        self._worker.set_flip(settings.get('camera_flip', True))
        self._leases += 1
        return VideoLease(self, self._worker)

    def release(self, worker):
        if worker is self._worker:
            self._leases -= 1
            if self._leases == 0:
                self._idle.start(self.IDLE_MS)

    def stop(self):
        self._idle.stop()
        worker, self._worker = self._worker, None
        self._key = None
        self._leases = 0
        if worker is not None:
            worker.close()
            self._retiring = [item for item in self._retiring if item._thread.is_alive()]
            if getattr(worker, '_thread', None) is not None:
                self._retiring.append(worker)

    def shutdown(self):
        self.stop()
        # At application exit, let native camera teardown finish before DLL unload.
        for worker in self._retiring:
            worker._thread.join(2)
        self._retiring = [item for item in self._retiring if item._thread.is_alive()]
