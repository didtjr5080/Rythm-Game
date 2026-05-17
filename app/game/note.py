from dataclasses import dataclass


@dataclass
class Note:
    note_id: int
    lane: int
    hit_time_ms: int
    judged: bool = False
    result: str | None = None

