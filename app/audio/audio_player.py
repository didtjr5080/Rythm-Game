import threading
import time
from pathlib import Path


class AudioPlayer:
    def __init__(self, path: str | None, volume: float = 0.85):
        self.path = Path(path) if path else None
        self.volume = max(0.0, min(1.0, float(volume)))
        self._sd = None
        self._thread: threading.Thread | None = None
        self.error: str | None = None
        self.duration_seconds = 0.0
        self.started_at: float | None = None
        self._loading = False
        self._finished = threading.Event()
        self._cancelled = threading.Event()
        self._play_lock = threading.Lock()

    @property
    def loading(self):
        return self._loading

    @property
    def finished(self):
        return self._finished.is_set()

    @property
    def position_ms(self):
        if self.started_at is None:
            return 0
        elapsed = max(0.0, time.monotonic()-self.started_at)
        return int(min(elapsed, self.duration_seconds)*1000)

    def play(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._cancelled.clear()
        self._finished.clear()
        self.started_at = None
        self.error = None
        if self.path is None:
            self._finished.set()
            return
        if not self.path.exists():
            self.error = f"Audio file not found: {self.path}"
            print(self.error)
            self._finished.set()
            return
        self._loading = True
        self._thread = threading.Thread(target=self._play_worker, daemon=True)
        self._thread.start()

    def _play_worker(self):
        try:
            import numpy as np
            import sounddevice as sd

            self._sd = sd
            data, sample_rate = self._load_audio()
            if data is None:
                return
            self.duration_seconds = len(data)/sample_rate
            if data.ndim == 1:
                data = np.column_stack([data, data])
            data = np.clip(data * self.volume, -1.0, 1.0)
            # A user can leave while decoding. Never start a stale track afterward.
            with self._play_lock:
                if self._cancelled.is_set():
                    return
                sd.play(data, sample_rate, blocking=False)
                self.started_at = time.monotonic()
                self._loading = False
            sd.wait()
        except Exception as exc:
            self.error = f"Audio playback failed: {exc}"
            print(self.error)
        finally:
            self._loading = False
            self._finished.set()

    def _load_audio(self):
        try:
            import soundfile as sf

            data, sample_rate = sf.read(str(self.path), always_2d=False, dtype="float32")
            return data, sample_rate
        except Exception:
            pass
        try:
            import librosa

            data, sample_rate = librosa.load(str(self.path), sr=None, mono=False)
            if data.ndim == 2:
                data = data.T
            return data.astype("float32"), sample_rate
        except Exception as exc:
            self.error = f"Audio decode failed: {exc}"
            print(self.error)
            return None, None

    def stop(self):
        self._cancelled.set()
        try:
            with self._play_lock:
                if self._sd is not None:
                    self._sd.stop()
        except Exception:
            pass
