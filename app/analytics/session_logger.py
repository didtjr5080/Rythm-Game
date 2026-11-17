import csv
import json
import time
import io
from uuid import uuid4
from app.atomic_io import atomic_text
from pathlib import Path


class SessionLogger:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parents[1] / "data" / "sessions"
        self.rows: list[dict] = []
        self.session_id = time.strftime("%Y%m%d_%H%M%S")+'_'+uuid4().hex[:12]

    def log(self, current_time_ms: int, input_state, note_index: int, judge_result: str | None):
        self.rows.append(
            {
                "timestamp": input_state.timestamp,
                "current_time_ms": current_time_ms,
                "hand_visible": input_state.hand_visible,
                "hand_x": input_state.hand_x,
                "hand_y": input_state.hand_y,
                "finger_count": getattr(input_state, "finger_count", None),
                "lane": input_state.lane,
                "emg_value": input_state.emg_value,
                "emg_activated": input_state.emg_activated,
                "note_index": note_index,
                "judge_result": judge_result or "",
            }
        )

    def save(self) -> tuple[Path, Path]:
        json_path = self.base_dir / f"session_{self.session_id}.json"
        csv_path = self.base_dir / f"session_{self.session_id}.csv"
        atomic_text(json_path, json.dumps(self.rows, indent=2))
        with io.StringIO(newline='') as handle:
            fieldnames = [
                "timestamp",
                "current_time_ms",
                "hand_visible",
                "hand_x",
                "hand_y",
                "finger_count",
                "lane",
                "emg_value",
                "emg_activated",
                "note_index",
                "judge_result",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)
            atomic_text(csv_path,handle.getvalue())
        return json_path, csv_path
