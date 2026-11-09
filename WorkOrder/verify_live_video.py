"""Slow native camera/inference must never block GUI reads or leak stale hands."""
import sys
import time
import threading
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.input.live_video import LiveVideoWorker
from app.input.input_fusion import InputFusion
from app.game.rhythm_game_engine import RhythmGameEngine
from app.game.note import Note

owners = []
released = threading.Event()
closed = threading.Event()
blocked = threading.Event()
resume = threading.Event()
pause = threading.Event()

class Camera:
    capture = True
    status = 'TEST CAMERA'
    def __init__(self, settings):
        owners.append(threading.get_ident())
    def read(self):
        time.sleep(.03)
        return np.zeros((720,1280,3), dtype=np.uint8)
    def release(self):
        assert threading.get_ident() == owners[0]
        released.set()

class Tracker:
    diagnostic_summary = 'TEST TRACKER'
    backend_is_mediapipe = True
    last_error = None
    def __init__(self, flip):
        assert threading.get_ident() == owners[0]
        self.flip = flip
    def set_flip(self, flip): self.flip = flip
    def track(self, frame):
        assert max(frame.shape[:2]) <= 640
        if pause.is_set():
            blocked.set()
            assert resume.wait(3)
        time.sleep(.05)
        return dict(hand_visible=True, x=.5, y=.5, lane=4, finger_count=5,
                    finger_states={'thumb':True}, frame=frame, landmarks=[(.5,.5)])
    def close(self):
        assert threading.get_ident() == owners[0]
        closed.set()

worker = LiveVideoWorker(dict(camera_enabled=True,camera_flip=True), camera_factory=Camera, tracker_factory=Tracker)
try:
    deadline = time.monotonic()+3
    while worker.read() is None:
        assert time.monotonic() < deadline, worker.status
        time.sleep(.005)
    assert owners[0] != threading.get_ident()
    assert worker.hand_sample()[1]['lane']==4
    worker._backend_ready=False
    assert worker.hand_sample() is None  # Approximate fallback cannot navigate.
    worker._backend_ready=True
    fusion = InputFusion(use_camera=False, use_mock_emg=True, emg_threshold=12, hand_tracker=worker)
    durations = []
    for _ in range(200):
        start=time.perf_counter()
        frame=worker.read()
        state,_=fusion.read(frame)
        durations.append((time.perf_counter()-start)*1000)
        assert state.hand_visible and state.lane==4
    # Compare with the same deliberately slow native operations run synchronously.
    start=time.perf_counter(); time.sleep(.03); time.sleep(.05)
    synchronous_ms=(time.perf_counter()-start)*1000
    ordered=sorted(durations)
    p95=ordered[int(len(ordered)*.95)]
    assert p95 < 10 and p95 < synchronous_ms/4, durations
    worker.set_flip(False)
    assert worker.read() is None  # Old orientation must not be displayed.
    pause.set()
    assert blocked.wait(2)
    time.sleep(worker.MAX_AGE+.03)
    assert worker.read() is None
    assert worker.hand_sample() is None
    assert not worker.track(None)['hand_visible']
    start=time.perf_counter(); worker.close()
    assert time.perf_counter()-start < .05
    resume.set(); worker._thread.join(2)
    assert not worker._thread.is_alive() and released.is_set() and closed.is_set()
    assert worker.read() is None
    print(f'PASS: same slow camera/inference baseline {synchronous_ms:.2f} ms; async GUI input p95 {p95:.3f} ms; bounded latest slot; 640px tracking; stale/flip invalidation; nonblocking close; native resources released by owner')
finally:
    resume.set(); worker.close(); worker._thread.join(2)

# The search cost must depend on visible notes rather than a full-length chart.
engine=RhythmGameEngine([Note(i,i%5,i*1000) for i in range(100000)])
assert [n.hit_time_ms for n in engine.notes_in_time_range(900000,902000)] == [900000,901000,902000]
print('PASS: long-chart time range boundaries and five-lane note preservation')
