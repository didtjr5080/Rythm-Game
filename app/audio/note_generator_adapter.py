import json
import sys
import time
from pathlib import Path

from app import config
from app.game.rhythm_game_engine import RhythmGameEngine


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
    return path if path.exists() else None


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
        occupied_buckets.add(bucket)
        simplified.append(
            {
                "note_id": len(simplified),
                "lane": int(note.get("lane", 0)) % config.LANE_COUNT,
                "hit_time_ms": hit_time_ms,
            }
        )
        last_time = hit_time_ms
    return simplified


def generate_notes_from_analysis(analysis: dict, difficulty: str = "normal") -> list[dict]:
    try:
        from note_generator import generate_notes

        chart = generate_notes(analysis, difficulty=difficulty, lanes=config.LANE_COUNT)
        converted = chart_to_motion_notes(chart)
        if converted:
            return converted
    except Exception as exc:
        print(f"Legacy note generation failed: {exc}")
    return [
        {"note_id": note.note_id, "lane": note.lane, "hit_time_ms": note.hit_time_ms}
        for note in RhythmGameEngine.generate_sample_notes()
    ]


def save_notes_json(notes: list[dict], output_dir: str | Path | None = None, song_path: str | Path | None = None) -> Path:
    target_dir = Path(output_dir) if output_dir is not None else notes_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    path = notes_path_for_song(song_path) if song_path else target_dir / f"notes_{int(time.time())}.json"
    notes = simplify_for_emg(notes)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"lane_count": config.LANE_COUNT, "notes": notes}, handle, indent=2)
    return path
