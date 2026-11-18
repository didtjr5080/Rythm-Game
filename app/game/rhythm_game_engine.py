import json
from bisect import bisect_left, bisect_right
from pathlib import Path

from app import config
from app.game.judge import judge_note, judge_emg_note
from app.game.emg_chart import generate_emg_notes
from app.game.note import Note
from app.game.score import ScoreState


class RhythmGameEngine:
    def __init__(self, notes: list[Note] | None = None, mode='pinch'):
        if mode not in ('pinch', 'emg', 'pinch_extension'):
            raise ValueError('Unknown game mode.')
        self.mode = mode
        self._previous_activation = False
        self.notes = sorted(notes if notes is not None else self.generate_sample_notes(mode), key=lambda note: note.hit_time_ms)
        if mode != 'emg':
            for previous, current in zip(self.notes, self.notes[1:]):
                if previous.lane == 1 and current.lane == 2:
                    current.lane = 0
        else:
            for note in self.notes:
                note.lane = 0
        self._last_end_time = max((n.end_time_ms for n in self.notes), default=0)
        self._max_duration = max((n.duration_ms for n in self.notes), default=0)
        self._note_times = [note.hit_time_ms for note in self.notes]
        self._next_note_index = 0
        self.score_state = ScoreState()
        self.last_result = ""
        self.last_judged_note_index = -1
        self.consecutive_misses = 0

    @property
    def miss_limit_reached(self):
        return self.consecutive_misses >= 10

    @staticmethod
    def generate_sample_notes(mode='pinch') -> list[Note]:
        lanes = [0, 1, 0, 3, 2, 1, 0, 1, 3, 2, 0, 3]
        notes = [Note(note_id=i, lane=lane, hit_time_ms=2500 + i * 1900) for i, lane in enumerate(lanes)]
        if mode == 'emg':
            return [RhythmGameEngine.normalize_note_dict(n, i) for i, n in enumerate(generate_emg_notes(
                [{'lane': n.lane, 'hit_time_ms': n.hit_time_ms} for n in notes]))]
        return notes

    @staticmethod
    def normalize_note_dict(raw_note: dict, index: int) -> Note:
        raw_time = raw_note.get("hit_time_ms", raw_note.get("time", 0))
        hit_time_ms = int(float(raw_note["hit_time_ms"])) if "hit_time_ms" in raw_note else int(float(raw_time)*1000)
        return Note(
            note_id=int(raw_note.get("note_id", index)),
            lane=int(raw_note.get("lane", 0)) % config.LANE_COUNT,
            hit_time_ms=hit_time_ms,
            duration_ms=max(0, int(raw_note.get('duration_ms', 0))),
        )

    @classmethod
    def from_json_file(cls, path: str | Path, mode='pinch'):
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        raw_notes = payload.get("notes", payload) if isinstance(payload, dict) else payload
        if mode == 'emg':
            saved = payload.get('emg_notes') if isinstance(payload, dict) else None
            raw_notes = (saved if saved and all(int(n.get('duration_ms', 0)) >= 1000 for n in saved)
                         else generate_emg_notes(raw_notes, dict(payload, duration=payload.get('duration_seconds', 0)) if isinstance(payload, dict) else None))
        notes = [cls.normalize_note_dict(item, i) for i, item in enumerate(raw_notes)]
        if mode != 'emg':
            for note in notes:
                note.duration_ms = 0
        # Apply the same density to old cached charts without rewriting personal files.
        spaced = []
        for note in sorted(notes, key=lambda item: item.hit_time_ms):
            previous_end = spaced[-1].end_time_ms if spaced else None
            if previous_end is None or note.hit_time_ms - previous_end >= config.MIN_NOTE_INTERVAL_MS:
                spaced.append(note)
        return cls(notes=spaced, mode=mode)

    def visible_notes(
        self,
        current_time_ms: int,
        height: int,
        note_speed: int = config.NOTE_SPEED,
        judgement_line_y_ratio: float = config.JUDGEMENT_LINE_Y_RATIO,
    ) -> list[tuple[Note, float]]:
        judge_y = height * judgement_line_y_ratio
        visible = []
        first_time = current_time_ms - (height+40-judge_y)/note_speed*1000
        last_time = current_time_ms + (judge_y+40)/note_speed*1000
        for note in self.notes_in_time_range(first_time, last_time):
            if note.judged:
                continue
            delta_sec = (note.hit_time_ms - current_time_ms) / 1000.0
            y = judge_y if note.duration_ms and current_time_ms >= note.hit_time_ms else judge_y - delta_sec * note_speed
            if -40 <= y <= height + 40:
                visible.append((note, y))
        return visible

    def notes_in_time_range(self, first_time, last_time):
        start = bisect_left(self._note_times, first_time - self._max_duration)
        stop = bisect_right(self._note_times, last_time)
        return [note for note in self.notes[start:stop] if note.end_time_ms >= first_time]

    def _advance_cursor(self):
        while self._next_note_index < len(self.notes) and self.notes[self._next_note_index].judged:
            self._next_note_index += 1

    def update(self, input_state, current_time_ms: int):
        if self.miss_limit_reached:
            return None
        active = bool(input_state.emg_activated)
        triggered = active and not self._previous_activation
        self._previous_activation = active
        result = None
        self._advance_cursor()
        if self._next_note_index < len(self.notes):
            index = self._next_note_index
            note = self.notes[index]
            result = (judge_emg_note(note, input_state, current_time_ms, config, triggered)
                      if self.mode == 'emg' else judge_note(note, input_state, current_time_ms, config,
                                                           require_extension=self.mode == 'pinch_extension'))
            if result:
                self.consecutive_misses = self.consecutive_misses + 1 if result == 'MISS' else 0
                self.score_state.apply_result(result)
                self.last_result = result
                self.last_judged_note_index = index
                self._advance_cursor()
        return result

    def is_finished(self, current_time_ms: int) -> bool:
        if self.miss_limit_reached:
            return True
        if not self.notes:
            return True
        self._advance_cursor()
        return self._next_note_index == len(self.notes) or current_time_ms > self._last_end_time + 1500

    def finalize_unjudged_notes(self):
        """Account for every remaining note when a real track ends naturally."""
        for index, note in enumerate(self.notes):
            if self.miss_limit_reached:
                break
            if note.judged:
                continue
            note.judged = True
            note.holding = False
            note.result = 'MISS'
            self.consecutive_misses += 1
            self.score_state.apply_result('MISS')
            self.last_result = 'MISS'
            self.last_judged_note_index = index
        self._advance_cursor()
