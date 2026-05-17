import shutil
import time
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.audio.beat_analyzer import analyze_audio_file
from app.audio.note_generator_adapter import (
    find_saved_notes_for_song,
    generate_notes_from_analysis,
    save_notes_json,
)
from app.i18n import tr
from app.settings import load_settings


class StartScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.language = load_settings()["language"]
        self.song_list = QListWidget()
        self.song_list.setAlternatingRowColors(True)
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(118)
        self.selected_title = QLabel("Sample Chart")
        self.selected_title.setObjectName("heroTitle")
        self.selected_title.setWordWrap(True)
        self.selected_title.setMinimumHeight(92)
        self.selected_meta = QLabel("No song selected")
        self.selected_meta.setObjectName("muted")
        self.selected_meta.setWordWrap(True)
        self.selected_notes = QLabel("Notes: sample")
        self.selected_notes.setObjectName("statusPill")
        self._build()
        self.refresh_saved_songs()
        self.update_selected_panel()

    @property
    def songs_dir(self) -> Path:
        path = Path(__file__).resolve().parents[1] / "data" / "songs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 18, 22, 18)
        outer.setSpacing(14)

        outer.addLayout(self._top_bar())

        body = QGridLayout()
        body.setSpacing(16)
        body.addWidget(self._selected_panel(), 0, 0)
        body.addWidget(self._browser_panel(), 0, 1)
        body.setColumnStretch(0, 5)
        body.setColumnStretch(1, 4)
        outer.addLayout(body, 1)

        outer.addWidget(self._bottom_bar())
        outer.addWidget(self.status)
        self._log("Saved notes are loaded automatically when a selected song already has a notes file.")

    def _top_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        brand = QLabel("EMG Motion Rhythm")
        brand.setObjectName("brand")
        subtitle = QLabel("Finger-count lane selection + EMG input")
        subtitle.setObjectName("subtitle")
        row.addWidget(brand)
        row.addSpacing(16)
        row.addWidget(subtitle)
        row.addStretch(1)
        badge = QLabel("MOTION RHYTHM")
        badge.setObjectName("topBadge")
        row.addWidget(badge)
        return row

    def _panel(self, object_name: str = "panel") -> QFrame:
        panel = QFrame()
        panel.setObjectName(object_name)
        return panel

    def _selected_panel(self) -> QFrame:
        panel = self._panel("heroPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        ranked = QLabel("READY")
        ranked.setObjectName("greenBadge")
        layout.addWidget(ranked, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(self.selected_title)
        layout.addWidget(self.selected_meta)
        stat_row = QHBoxLayout()
        for label in (self.selected_notes, self._small_stat("LANES", "3"), self._small_stat("INPUT", "FINGER + EMG")):
            stat_row.addWidget(label)
        stat_row.addStretch(1)
        layout.addLayout(stat_row)
        return panel

    def _small_stat(self, title: str, value: str) -> QLabel:
        label = QLabel(f"{title}  {value}")
        label.setObjectName("statusPill")
        return label

    def _browser_panel(self) -> QFrame:
        panel = self._panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        title = QLabel(tr("saved_music", self.language))
        title.setObjectName("sectionTitle")
        hint = QLabel("Double-click a song or use Load Selected.")
        hint.setObjectName("muted")
        self.song_list.setObjectName("beatmapList")
        self.song_list.setWordWrap(True)
        self.song_list.itemDoubleClicked.connect(self.load_saved_song_item)
        self.song_list.currentItemChanged.connect(lambda _current, _previous: self.preview_song_item(_current))
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.song_list, 1)

        row = QHBoxLayout()
        add_song = QPushButton(tr("add_song", self.language))
        load_song = QPushButton(tr("load_selected", self.language))
        refresh = QPushButton(tr("refresh", self.language))
        load_song.setObjectName("primary")
        add_song.clicked.connect(self.select_song)
        load_song.clicked.connect(self.load_selected_saved_song)
        refresh.clicked.connect(self.refresh_saved_songs)
        row.addWidget(add_song)
        row.addWidget(load_song)
        row.addWidget(refresh)
        layout.addLayout(row)
        return panel

    def _bottom_bar(self) -> QFrame:
        panel = self._panel("bottomBar")
        row = QHBoxLayout(panel)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(12)
        generate_notes = QPushButton(tr("generate_notes", self.language))
        settings = QPushButton(tr("settings", self.language))
        start_game = QPushButton(tr("start_game", self.language))
        view_results = QPushButton(tr("view_results", self.language))
        start_game.setObjectName("primary")
        generate_notes.clicked.connect(self.generate_notes)
        settings.clicked.connect(self.main_window.show_settings_screen)
        start_game.clicked.connect(self.main_window.show_game_widget)
        view_results.clicked.connect(self.main_window.show_results_browser_screen)
        for button in (generate_notes, settings, start_game, view_results):
            button.setMinimumHeight(44)
            row.addWidget(button)
        return panel

    def _log(self, message: str):
        self.status.append(message)

    def refresh_saved_songs(self):
        current = self.main_window.selected_song_path
        self.song_list.clear()
        for path in sorted(self.songs_dir.glob("*"), key=lambda item: item.stat().st_mtime, reverse=True):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            if path.suffix.lower() not in {".mp3", ".wav", ".ogg"}:
                continue
            notes_path = find_saved_notes_for_song(path)
            notes_state = "notes ready" if notes_path else "no notes"
            item = QListWidgetItem(f"{self.display_song_title(path)}\n{path.suffix.upper()[1:]}  |  {notes_state}")
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.song_list.addItem(item)
            if current and Path(current) == path:
                self.song_list.setCurrentItem(item)
        self.update_selected_panel()

    def select_song(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Song", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if path:
            saved_path = self.save_song_file(path)
            self.main_window.selected_song_path = str(saved_path)
            self.main_window.notes_path = None
            self.refresh_saved_songs()
            self._log(f"Selected song saved: {saved_path}")

    def save_song_file(self, source_path: str) -> Path:
        source = Path(source_path)
        safe_stem = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in source.stem)
        target = self.songs_dir / f"{safe_stem}_{int(time.time())}{source.suffix.lower()}"
        shutil.copy2(source, target)
        return target

    @staticmethod
    def display_song_title(path: Path) -> str:
        parts = path.stem.rsplit("_", 1)
        stem = parts[0] if len(parts) == 2 and parts[1].isdigit() else path.stem
        return stem.replace("_", " ")

    def preview_song_item(self, item: QListWidgetItem | None):
        if item is None:
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        self.update_selected_panel(path)

    def load_selected_saved_song(self):
        item = self.song_list.currentItem()
        if item is None:
            self._log("No saved song selected.")
            return
        self.load_saved_song_item(item)

    def load_saved_song_item(self, item: QListWidgetItem):
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        if not path.exists():
            self._log(f"Saved song is missing: {path}")
            self.refresh_saved_songs()
            return
        self.main_window.selected_song_path = str(path)
        saved_notes = find_saved_notes_for_song(path)
        self.main_window.notes_path = str(saved_notes) if saved_notes else None
        self.update_selected_panel(path)
        note_msg = f"Loaded notes: {saved_notes.name}" if saved_notes else "No saved notes yet. Generate Notes to save them."
        self._log(f"Loaded saved song: {path.name}. {note_msg}")

    def update_selected_panel(self, path: Path | None = None):
        selected = path or (Path(self.main_window.selected_song_path) if self.main_window.selected_song_path else None)
        if selected:
            notes_path = find_saved_notes_for_song(selected)
            self.selected_title.setText(self.display_song_title(selected))
            self.selected_meta.setText(f"{selected.suffix.upper()[1:]}  |  {selected}")
            self.selected_notes.setText(f"NOTES  {'READY' if notes_path else 'MISSING'}")
            self.selected_notes.setProperty("ready", bool(notes_path))
            self.selected_notes.style().unpolish(self.selected_notes)
            self.selected_notes.style().polish(self.selected_notes)
        else:
            self.selected_title.setText("Sample Chart")
            self.selected_meta.setText("No song selected")
            self.selected_notes.setText("NOTES  SAMPLE")

    def generate_notes(self):
        if not self.main_window.selected_song_path:
            notes = generate_notes_from_analysis({})
            path = save_notes_json(notes)
            self.main_window.notes_path = str(path)
            self._log(f"No song selected. Saved sample notes: {path}")
            return
        analysis = analyze_audio_file(self.main_window.selected_song_path)
        analysis["file_id"] = Path(self.main_window.selected_song_path).stem
        notes = generate_notes_from_analysis(analysis)
        path = save_notes_json(notes, song_path=self.main_window.selected_song_path)
        self.main_window.notes_path = str(path)
        self.refresh_saved_songs()
        self.update_selected_panel(Path(self.main_window.selected_song_path))
        self._log(f"Generated and saved notes: {path}")

    def view_results(self):
        result_dir = Path(__file__).resolve().parents[1] / "data" / "results"
        result_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(result_dir.glob("*.json"), reverse=True)
        if not files:
            self._log("No saved results yet.")
            return
        self._log(f"Latest result: {files[0]}")
