import os

import librosa
import numpy as np


def _to_list(values):
    return [float(v) for v in values]


def analyze_audio(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load audio file. Ensure it is a valid mp3/wav/ogg. ({exc})"
        ) from exc

    try:
        duration = float(librosa.get_duration(y=y, sr=sr))
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if tempo.size else 0.0
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            backtrack=True,
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        onset_strengths = onset_env[onset_frames] if len(onset_frames) else []
        rms = librosa.feature.rms(y=y)[0]
        energy_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    except Exception as exc:
        raise RuntimeError(f"Audio analysis failed. The file may be too long or corrupted. ({exc})") from exc

    return {
        "duration": duration,
        "sample_rate": int(sr),
        "bpm": float(tempo),
        "beats": _to_list(beat_times),
        "onsets": _to_list(onset_times),
        "onset_strengths": _to_list(onset_strengths),
        "energy_times": _to_list(energy_times),
        "energy": _to_list(rms),
    }
