import threading
from pathlib import Path


class AudioPlayer:
    def __init__(self, path: str | None, volume: float = 0.85):
        self.path = Path(path) if path else None
        self.volume = max(0.0, min(1.0, float(volume)))
        self._sd = None
        self._thread: threading.Thread | None = None
        self.error: str | None = None

    def play(self):
        if self.path is None:
            return
        if not self.path.exists():
            self.error = f"Audio file not found: {self.path}"
            print(self.error)
            return
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
            if data.ndim == 1:
                data = np.column_stack([data, data])
            data = np.clip(data * self.volume, -1.0, 1.0)
            sd.play(data, sample_rate, blocking=False)
        except Exception as exc:
            self.error = f"Audio playback failed: {exc}"
            print(self.error)

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
        try:
            if self._sd is not None:
                self._sd.stop()
        except Exception:
            pass
