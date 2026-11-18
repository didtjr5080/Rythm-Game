"""Poll Orion on a worker; the game only consumes fresh Python snapshots."""
import threading
import time

from app.input.orion_leapc import OrionReader
from app.input.pinch_classifier import NAMES, PinchClassifier
from app.input.leap_calibration import load_profiles


class LeapPinchTracker:
    MAX_AGE = .25

    def __init__(self, reader_factory=OrionReader):
        self.status = 'LEAP STARTING / RIGHT HAND'
        self.last_error = None
        self._snapshot = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(reader_factory,),
                                        name='leap-pinch', daemon=True)
        self._thread.start()

    def _run(self, reader_factory):
        self.profile_name = None
        try:
            profiles = load_profiles()
            self.profile_name = profiles['active']
            thresholds = profiles['profiles'].get(self.profile_name)
        except (OSError, ValueError) as exc:
            self.last_error = 'Leap profile: ' + str(exc)
            thresholds = None
        model = PinchClassifier(thresholds)
        try:
            with reader_factory() as reader:
                while not self._stop.is_set():
                    is_frame, sample = reader.poll('right', 20)
                    if not is_frame:
                        continue
                    current, _, _ = model.step(sample)
                    lane = NAMES.index(current) if current in NAMES else None
                    hand = {'hand_visible': sample is not None, 'lane': lane,
                            'x': (lane + .5) / 4 if lane is not None else None,
                            'y': .5 if sample is not None else None,
                            'hand_label': current, 'finger_count': None, '_sample': sample}
                    with self._lock:
                        self._snapshot = (time.monotonic(), hand)
                    self.status = 'LEAP RIGHT / ' + current
        except Exception as exc:
            self.last_error = str(exc)
            self.status = 'LEAP ERROR / ' + str(exc)
        finally:
            with self._lock:
                self._snapshot = None

    def track(self, frame=None):
        with self._lock:
            snapshot = self._snapshot
        if (self._stop.is_set() or snapshot is None
                or time.monotonic() - snapshot[0] > self.MAX_AGE):
            if not self.last_error:
                self.status = 'LEAP WAITING / RIGHT HAND'
            return {'hand_visible': False, 'lane': None, 'frame': frame}
        return dict(snapshot[1], frame=frame)

    def close(self):
        self._stop.set()
        self._thread.join(timeout=.5)

    def calibration_sample(self):
        return self.track().get('_sample')
