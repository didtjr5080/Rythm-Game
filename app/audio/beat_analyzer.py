import sys
import math
from pathlib import Path


LEGACY_BACKEND = Path(__file__).resolve().parents[2] / "legacy_web" / "backend"
if str(LEGACY_BACKEND) not in sys.path:
    sys.path.insert(0, str(LEGACY_BACKEND))


def analyze_audio_file(file_path: str) -> dict:
    try:
        from audio_analyzer import analyze_audio
        from app.audio.note_generator_adapter import audio_signature

        signature = audio_signature(file_path)
        analysis = analyze_audio(file_path)
        if signature != audio_signature(file_path):
            raise ValueError('Song changed during analysis. Generate Notes again.')
        duration = float(analysis.get('duration', 0))
        rate = int(analysis.get('sample_rate', 0))
        if not math.isfinite(duration) or duration <= 0 or rate <= 0:
            raise ValueError('Audio analysis returned no valid decoded audio.')
        analysis['audio_signature'] = signature
        analysis['audio_source'] = {
            'path': str(Path(file_path).resolve()),
            'analyzer_module': str(Path(sys.modules['audio_analyzer'].__file__).resolve()),
            'sample_rate': rate,
            'decoded_frames': round(duration * rate),
            'duration_basis': 'decoded_pcm',
        }
        return analysis
    except Exception as exc:
        raise RuntimeError(f'Audio analysis failed: {exc}') from exc

