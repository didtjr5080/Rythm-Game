from dataclasses import dataclass


@dataclass
class Note:
    note_id: int
    lane: int
    hit_time_ms: int
    judged: bool = False
    result: str | None = None
    duration_ms: int = 0
    holding: bool = False
    start_error_ms: int = 0
    last_hold_time_ms: int | None = None
    dropout_since_ms: int | None = None

    @property
    def end_time_ms(self):
        return self.hit_time_ms + self.duration_ms

