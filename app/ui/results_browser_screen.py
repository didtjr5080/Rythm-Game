import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.i18n import tr
from app.settings import load_settings


class ResultsBrowserScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.language = load_settings()["language"]
        self.result_list = QListWidget()
        self.detail_panel = QFrame()
        self.detail_grid = QGridLayout(self.detail_panel)
        self.empty_label = QLabel()
        self._build()
        self.refresh_results()

    @property
    def results_dir(self) -> Path:
        path = Path(__file__).resolve().parents[1] / "data" / "results"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel(tr("results", self.language))
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch(1)
        refresh = QPushButton(tr("refresh", self.language))
        back = QPushButton(tr("back", self.language))
        refresh.clicked.connect(self.refresh_results)
        back.clicked.connect(self.main_window.show_start_screen)
        header.addWidget(refresh)
        header.addWidget(back)
        outer.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(16)
        list_panel = QFrame()
        list_panel.setObjectName("panel")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_title = QLabel(tr("saved_results", self.language))
        list_title.setObjectName("sectionTitle")
        self.result_list.setObjectName("beatmapList")
        self.result_list.itemSelectionChanged.connect(self.show_selected_result)
        list_layout.addWidget(list_title)
        list_layout.addWidget(self.result_list, 1)

        self.detail_panel.setObjectName("heroPanel")
        self.detail_grid.setContentsMargins(22, 22, 22, 22)
        self.detail_grid.setSpacing(14)
        self.empty_label.setObjectName("heroTitle")
        self.empty_label.setWordWrap(True)
        body.addWidget(list_panel, 2)
        body.addWidget(self.detail_panel, 3)
        outer.addLayout(body, 1)

    def refresh_results(self):
        self.result_list.clear()
        files = sorted(self.results_dir.glob("result_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        for path in files:
            data = self.load_result(path)
            score = data.get("score", 0)
            accuracy = float(data.get("accuracy", 0.0))
            item = QListWidgetItem(f"{self.display_result_name(path)}\nScore {score}  |  Accuracy {accuracy:.2f}%")
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.result_list.addItem(item)
        if files:
            self.result_list.setCurrentRow(0)
        else:
            self.show_empty()

    @staticmethod
    def display_result_name(path: Path) -> str:
        name = path.stem.replace("result_", "")
        if len(name) == 15 and "_" in name:
            return f"{name[:4]}-{name[4:6]}-{name[6:8]} {name[9:11]}:{name[11:13]}:{name[13:15]}"
        return path.stem.replace("_", " ")

    @staticmethod
    def load_result(path: Path) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}

    def clear_detail(self):
        while self.detail_grid.count():
            item = self.detail_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_empty(self):
        self.clear_detail()
        self.empty_label.setText(tr("no_results", self.language))
        self.detail_grid.addWidget(self.empty_label, 0, 0)

    def show_selected_result(self):
        item = self.result_list.currentItem()
        if item is None:
            self.show_empty()
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        data = self.load_result(path)
        self.clear_detail()

        title = QLabel(self.display_result_name(path))
        title.setObjectName("heroTitle")
        title.setWordWrap(True)
        self.detail_grid.addWidget(title, 0, 0, 1, 4)

        metrics = (
            ("score", "score"),
            ("accuracy", "accuracy"),
            ("max_combo", "max_combo"),
            ("perfect_count", "perfect"),
            ("good_count", "good"),
            ("miss_count", "miss"),
            ("avg_emg", "avg_emg"),
            ("max_emg", "max_emg"),
            ("activation_count", "activation_count"),
            ("avg_input_delay_ms", "avg_input_delay_ms"),
            ("emg_drop_rate", "emg_drop_rate"),
        )
        for index, (key, label_key) in enumerate(metrics, start=1):
            label = QLabel(tr(label_key, self.language))
            label.setObjectName("muted")
            value = data.get(key, 0)
            if isinstance(value, float):
                value = f"{value:.2f}"
            value_label = QLabel(str(value))
            value_label.setObjectName("sectionTitle")
            row = 1 + (index - 1) // 2
            col = ((index - 1) % 2) * 2
            self.detail_grid.addWidget(label, row, col)
            self.detail_grid.addWidget(value_label, row, col + 1)

        file_label = QLabel(str(path))
        file_label.setObjectName("muted")
        file_label.setWordWrap(True)
        self.detail_grid.addWidget(file_label, 8, 0, 1, 4)

