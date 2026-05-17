import json
import time
from pathlib import Path

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ResultScreen(QWidget):
    def __init__(self, main_window, metrics: dict, session_paths: tuple | None = None):
        super().__init__()
        self.main_window = main_window
        self.metrics = metrics
        self.session_paths = session_paths
        self._save_result()
        self._build()

    def _save_result(self):
        result_dir = Path(__file__).resolve().parents[1] / "data" / "results"
        result_dir.mkdir(parents=True, exist_ok=True)
        path = result_dir / f"result_{time.strftime('%Y%m%d_%H%M%S')}.json"
        payload = dict(self.metrics)
        if self.session_paths:
            payload["session_json"] = str(self.session_paths[0])
            payload["session_csv"] = str(self.session_paths[1])
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        self.result_path = path

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 30, 36, 30)
        outer.setSpacing(18)
        title = QLabel("Play Result")
        title.setObjectName("title")
        saved = QLabel(f"Saved result: {self.result_path}")
        saved.setObjectName("muted")
        outer.addWidget(title)
        outer.addWidget(saved)

        panel = QFrame()
        panel.setObjectName("panel")
        grid = QGridLayout(panel)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(12)
        keys = (
            "score",
            "combo",
            "max_combo",
            "hit_count",
            "miss_count",
            "perfect_count",
            "good_count",
            "accuracy",
            "avg_emg",
            "max_emg",
            "activation_count",
            "avg_input_delay_ms",
            "emg_drop_rate",
        )
        for index, key in enumerate(keys):
            label = QLabel(key)
            label.setObjectName("muted")
            value = self.metrics.get(key, 0)
            if isinstance(value, float):
                value = f"{value:.2f}"
            value_label = QLabel(str(value))
            value_label.setObjectName("sectionTitle")
            row = index // 3
            col = (index % 3) * 2
            grid.addWidget(label, row, col)
            grid.addWidget(value_label, row, col + 1)
        outer.addWidget(panel)

        back = QPushButton("Back to Start")
        back.setObjectName("primary")
        if hasattr(self.main_window, "show_start_screen"):
            back.clicked.connect(self.main_window.show_start_screen)
        else:
            back.clicked.connect(self.close)
        outer.addWidget(back)
        outer.addStretch(1)

