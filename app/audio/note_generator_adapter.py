import json
import sys
import time
import hashlib
import math
from pathlib import Path

from app import config
from app.game.rhythm_game_engine import RhythmGameEngine
from app.game.emg_chart import generate_emg_notes


LEGACY_BACKEND = Path(__file__).resolve().parents[2] / "legacy_web" / "backend"
if str(LEGACY_BACKEND) not in sys.path:
    sys.path.insert(0, str(LEGACY_BACKEND))


def notes_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / "data" / "notes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def notes_path_for_song(song_path: str | Path) -> Path:
    return notes_dir() / f"{Path(song_path).stem}_notes.json"


def find_saved_notes_for_song(song_path: str | Path | None) -> Path | None:
    if not song_path:
        return None
    path = notes_path_for_song(song_path)
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if (payload.get('schema_version') == 3
                and payload.get('audio_signature') == audio_signature(song_path)
                and payload.get('notes') and payload.get('emg_notes')
                and all(int(n.get('duration_ms', 0)) >= 1000 for n in payload['emg_notes'])):
            for mode in ('pinch', 'emg'):
                engine = RhythmGameEngine.from_json_file(path, mode=mode)
                if not engine.notes or any(n.hit_time_ms < 0 for n in engine.notes):
                    return None
            return path
    except (OSError, ValueError, TypeError, AttributeError, KeyError, OverflowError):
        pass
    return None


def audio_signature(song_path):
    song = Path(song_path)
    info = song.stat()
    with song.open('rb') as stream:
        hasher = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
        digest = hasher.hexdigest()
    after = song.stat()
    if (info.st_size, info.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Song changed while reading. Generate Notes again.')
    return {'filename':song.name, 'size':info.st_size, 'mtime_ns':info.st_mtime_ns, 'sha256':digest}


def chart_to_motion_notes(chart: dict) -> list[dict]:
    raw_notes = chart.get("notes", [])
    notes = []
    for index, note in enumerate(raw_notes):
        raw_time = note.get("hit_time_ms", note.get("time", 0))
        hit_time_ms = int(float(note["hit_time_ms"])) if "hit_time_ms" in note else int(float(raw_time)*1000)
        notes.append(
            {
                "note_id": int(note.get("note_id", index)),
                "lane": int(note.get("lane", 0)) % config.LANE_COUNT,
                "hit_time_ms": hit_time_ms,
            }
        )
    return simplify_for_emg(notes)


def simplify_for_emg(notes: list[dict], min_interval_ms: int = config.MIN_NOTE_INTERVAL_MS) -> list[dict]:
    simplified = []
    last_time = -10**9
    occupied_buckets = set()
    for note in sorted(notes, key=lambda item: (int(item.get("hit_time_ms", 0)), int(item.get("lane", 0)))):
        hit_time_ms = int(note.get("hit_time_ms", 0))
        bucket = round(hit_time_ms / 120)
        if bucket in occupied_buckets:
            continue
        if hit_time_ms - last_time < min_interval_ms:
            continue
        lane = int(note.get("lane", 0)) % config.LANE_COUNT
        if simplified and simplified[-1]["lane"] == 1 and lane == 2:
            lane = 0  # Avoid the MIDDLE -> RING transition after timing simplification.
        occupied_buckets.add(bucket)
        simplified.append(
            {
                "note_id": len(simplified),
                "lane": lane,
                "hit_time_ms": hit_time_ms,
            }
        )
        last_time = hit_time_ms
    return simplified


def generate_notes_from_analysis(analysis: dict, difficulty: str = "normal") -> list[dict]:
    if analysis:
        duration = float(analysis.get('duration', 0))
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Selected song has no valid analysis. Generate Notes again.')
    try:
        from note_generator import generate_notes

        chart = generate_notes(analysis, difficulty=difficulty, lanes=config.LANE_COUNT)
        converted = chart_to_motion_notes(chart)
        if converted:
            return converted
    except Exception as exc:
        if analysis.get('duration', 0) > 0:
            raise RuntimeError(f'Song note generation failed: {exc}') from exc
        print(f"Legacy note generation failed: {exc}")
    if analysis.get('duration', 0) > 0:
        raise ValueError('No playable rhythm detected in the selected song. Generate Notes again or select another song.')
    return [
        {"note_id": note.note_id, "lane": note.lane, "hit_time_ms": note.hit_time_ms}
        for note in RhythmGameEngine.generate_sample_notes()
    ]


def save_notes_json(notes: list[dict], output_dir: str | Path | None = None, song_path: str | Path | None = None, analysis=None) -> Path:
    target_dir = Path(output_dir) if output_dir is not None else notes_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f'{Path(song_path).stem}_notes.json' if song_path else target_dir / f"notes_{int(time.time())}.json"
    notes = simplify_for_emg(notes)
    from app.atomic_io import atomic_text
    emg_notes = generate_emg_notes(notes, analysis)
    signature = audio_signature(song_path) if song_path else None
    analyzed_signature = (analysis or {}).get('audio_signature')
    if song_path and analyzed_signature is not None and analyzed_signature != signature:
        raise ValueError('Song changed after analysis. Generate Notes again.')
    if song_path and (not notes or not emg_notes):
        raise ValueError('Selected song has no playable chart.')
    atomic_text(path,json.dumps({'schema_version': 3, "lane_count": config.LANE_COUNT,
                                'audio_signature':signature,
                                'audio_source':(analysis or {}).get('audio_source'),
                                'duration_seconds':(analysis or {}).get('duration',0),
                                "notes": notes, 'emg_notes': emg_notes}, indent=2))
    return path
