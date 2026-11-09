"""Camera and hand inference off the GUI thread, with one latest-result slot."""
import threading
import time

from app.input.camera import CameraSource
from app.input.mediapipe_tracker import MediaPipeHandTracker

_camera_lifetime_lock = threading.Lock()


def open_live_video(owner, settings, enabled=True):
    session = getattr(owner, 'video_session', None)
    return session.acquire(settings, enabled) if session is not None else LiveVideoWorker(settings, enabled)


class LiveVideoWorker:
    MAX_AGE = .25

    def __init__(self, settings, enabled=True, camera_factory=None, tracker_factory=None):
        self.settings = dict(settings)
        self.flip = bool(settings.get('camera_flip', True))
        self.capture = None  # Native objects are owned and closed by the worker.
        self._camera_factory = camera_factory or CameraSource
        self._tracker_factory = tracker_factory or MediaPipeHandTracker
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._snapshot = None
        self._read_snapshot = None
        self._status = 'CAMERA STARTING'
        self._diagnostic = 'HAND TRACKER STARTING'
        self._backend_ready = False
        self.last_error = None
        self._thread = None
        if enabled and settings.get('camera_enabled', True):
            self._thread = threading.Thread(target=self._run, name='live-camera-tracking', daemon=True)
            self._thread.start()
        else:
            self._status = 'CAMERA DISABLED'

    @property
    def status(self):
        return self._status

    @property
    def error(self):
        return self.last_error or ''

    @property
    def backend_is_mediapipe(self):
        return self._backend_ready

    @property
    def diagnostic_summary(self):
        return self._diagnostic

    def _run(self):
        camera = tracker = None
        owns_camera_lock = False
        try:
            # Closing an old DirectShow graph and opening another must not overlap.
            self._status = 'WAITING FOR CAMERA'
            while not self._stop.is_set():
                if _camera_lifetime_lock.acquire(timeout=.05):
                    owns_camera_lock = True
                    break
            if not owns_camera_lock or self._stop.is_set(): return
            camera = self._camera_factory(self.settings)
            self._status = camera.status
            if camera.capture is None or self._stop.is_set():
                self._diagnostic = camera.status
                return
            tracker = self._tracker_factory(flip=self.flip)
            import cv2
            while not self._stop.is_set():
                started = time.monotonic()
                frame = camera.read()
                self._status = camera.status
                # Timestamp capture, not inference completion: slow results expire.
                captured = time.monotonic()
                tracker.set_flip(self.flip)
                small = frame
                if frame is not None and max(frame.shape[:2]) > 640:
                    height, width = frame.shape[:2]
                    scale = 640 / max(height, width)
                    small = cv2.resize(frame, (round(width*scale), round(height*scale)), interpolation=cv2.INTER_AREA)
                hand = tracker.track(small)
                self._diagnostic = tracker.diagnostic_summary
                self._backend_ready = tracker.backend_is_mediapipe
                self.last_error = tracker.last_error
                # Never publish a frame captured with the previous flip setting.
                with self._lock:
                    self._snapshot = (captured, frame, hand, tracker.flip)
                interval = 1/30 if hand.get('hand_visible') else 1/15
                self._stop.wait(max(0, interval-(time.monotonic()-started)))
        except Exception as exc:
            self.last_error = str(exc)
            self._status = 'CAMERA WORKER ERROR / ' + str(exc)
            self._diagnostic = self._status
            self._backend_ready = False
        finally:
            try:
                if tracker is not None:
                    tracker.close()
            finally:
                try:
                    if camera is not None:
                        camera.release()
                finally:
                    with self._lock:
                        self._snapshot = None
                    if owns_camera_lock:
                        _camera_lifetime_lock.release()

    def read(self):
        with self._lock:
            snapshot = self._snapshot
        if (self._stop.is_set() or snapshot is None
                or time.monotonic()-snapshot[0] > self.MAX_AGE or snapshot[3] != self.flip):
            snapshot = None
        self._read_snapshot = snapshot
        return snapshot[1] if snapshot is not None else None

    def track(self, frame):
        snapshot = self._read_snapshot
        if snapshot is None or frame is None or frame is not snapshot[1]:
            return MediaPipeHandTracker._empty_result(frame)
        # Return a copy; GUI and inference never mutate the same dictionary.
        return dict(snapshot[2])

    def hand_sample(self):
        """Independent navigation consumer; never infer again or accept OpenCV guesses."""
        with self._lock:
            snapshot = self._snapshot
        if (not self._backend_ready or self._stop.is_set() or snapshot is None
                or time.monotonic()-snapshot[0] > self.MAX_AGE or snapshot[3] != self.flip):
            return None
        return snapshot[0], dict(snapshot[2])

    def set_flip(self, enabled):
        self.flip = bool(enabled)

    def toggle_flip(self):
        self.set_flip(not self.flip)
        return self.flip

    def close(self):
        # Do not wait for a camera driver on the GUI thread. The owner releases it
        # in finally, even if shutdown was requested during a blocking read.
        self._stop.set()
        self._read_snapshot = None

    release = close
