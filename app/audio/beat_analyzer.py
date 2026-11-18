import sys
from pathlib import Path


LEGACY_BACKEND = Path(__file__).resolve().parents[2] / "legacy_web" / "backend"
if str(LEGACY_BACKEND) not in sys.path:
    sys.path.insert(0, str(LEGACY_BACKEND))


def analyze_audio_file(file_path: str) -> dict:
    try:
        from audio_analyzer import analyze_audio

        return analyze_audio(file_path)
    except Exception as exc:
        raise RuntimeError(f'Audio analysis failed: {exc}') from exc

