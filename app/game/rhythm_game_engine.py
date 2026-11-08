import json
from dataclasses import replace
from pathlib import Path

from app import config
from app.game.judge import judge_note
from app.game.note import Note
from app.game.score import ScoreState


class RhythmGameEngine:
    def __init__(self, notes: list[Note] | None = None):
        self.notes = notes or self.generate_sample_notes()
        self.score_state = ScoreState()
        self._previous_activation = False
        self.last_result = ""
        self.last_judged_note_index = -1

    @staticmethod
    def generate_sample_notes() -> list[Note]:
        lanes = [0, 1, 2, 3, 4, 3, 2, 1, 0, 2, 4, 1]
        return [Note(note_id=i, lane=lane, hit_time_ms=2500 + i * 950) for i, lane in enumerate(lanes)]

    @staticmethod
    def normalize_note_dict(raw_note: dict, index: int) -> Note:
        raw_time = raw_note.get("hit_time_ms", raw_note.get("time", 0))
        hit_time_ms = int(float(raw_note["hit_time_ms"])) if "hit_time_ms" in raw_note else int(float(raw_time)*1000)
        return Note(
            note_id=int(raw_note.get("note_id", index)),
            lane=int(raw_note.get("lane", 0)) % config.LANE_COUNT,
            hit_time_ms=hit_time_ms,
        )

    @classmethod
    def from_json_file(cls, path: str | Path):
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        raw_notes = payload.get("notes", payload) if isinstance(payload, dict) else payload
        source_lanes = payload.get("lane_count", 3) if isinstance(payload, dict) else 3
        if any(int(item.get("lane", 0)) >= 3 for item in raw_notes):
            source_lanes = config.LANE_COUNT
        notes = [cls.normalize_note_dict(item, i) for i, item in enumerate(raw_notes)]
        if source_lanes == 3 and config.LANE_COUNT == 5:
            for note in notes:
                note.lane *= 2
        return cls(notes=notes or cls.generate_sample_notes())

    def visible_notes(
        self,
        current_time_ms: int,
        height: int,
        note_speed: int = config.NOTE_SPEED,
        judgement_line_y_ratio: float = config.JUDGEMENT_LINE_Y_RATIO,
    ) -> list[tuple[Note, float]]:
        judge_y = height * judgement_line_y_ratio
        visible = []
        for note in self.notes:
            if note.judged:
                continue
            delta_sec = (note.hit_time_ms - current_time_ms) / 1000.0
            y = judge_y - delta_sec * note_speed
            if -40 <= y <= height + 40:
                visible.append((note, y))
        return visible

    def update(self, input_state, current_time_ms: int):
        active = bool(input_state.emg_activated)
        triggered = active and not self._previous_activation
        self._previous_activation = active
        input_state = replace(input_state, emg_activated=triggered)
        result = None
        for index, note in enumerate(self.notes):
            if note.judged:
                continue
            result = judge_note(note, input_state, current_time_ms, config)
            if result:
                self.score_state.apply_result(result)
                self.last_result = result
                self.last_judged_note_index = index
                break
            if current_time_ms < note.hit_time_ms - config.JUDGE_WINDOW_MS:
                break
        return result

    def is_finished(self, current_time_ms: int) -> bool:
        if not self.notes:
            return True
        return all(note.judged for note in self.notes) or current_time_ms > self.notes[-1].hit_time_ms + 1500
