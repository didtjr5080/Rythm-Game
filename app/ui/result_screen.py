import json
import time
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


from app.ui.theme import AuroraScreen, GlassPanel
from app.ui.dashboard import Instrument
from app.game.rhythm_game_engine import RhythmGameEngine
from app.settings import load_settings

class ResultScreen(AuroraScreen):
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
        outer=QVBoxLayout(self); outer.setContentsMargins(50,28,50,24)
        title=QLabel('POST-GAME REHABILITATION ANALYTICS'); title.setObjectName('title'); title.setAlignment(Qt.AlignmentFlag.AlignCenter); outer.addWidget(title)
        saved=QLabel(f'SESSION: COMPLETED / {self.result_path.name}'); saved.setObjectName('subtitle'); outer.addWidget(saved)
        hint=QLabel('HAND CURSOR: OPEN = MOVE / FIST = CLICK / DOUBLE FIST = SCROLL MODE / ESC = CANCEL')
        hint.setObjectName('subtitle'); hint.setWordWrap(True); outer.addWidget(hint)
        row=QHBoxLayout(); row.setSpacing(30)
        for kind,heading in (('song','SONG & BEAT DSP ANALYSIS'),('performance','NEURO-MOTOR PERFORMANCE REPORT'),('bio','LIVE BIO-CALIBRATION')):
            panel=GlassPanel(heading); layout=QVBoxLayout(panel); layout.setContentsMargins(16,44,16,18)
            instrument=Instrument(kind); instrument.metrics=self.metrics; instrument.threshold=load_settings()['emg_threshold']
            if kind=='song':
                instrument.analysis=getattr(self.main_window,'song_analyses',{}).get(getattr(self.main_window,'selected_song_path',None),{})
                path=getattr(self.main_window,'notes_path',None)
                try: instrument.notes=RhythmGameEngine.from_json_file(path).notes if path else RhythmGameEngine.generate_sample_notes()
                except (ValueError,OSError,TypeError): pass
            if kind=='bio': instrument.sensor_status='SESSION COMPLETE // PREVIEW'
            layout.addWidget(instrument,1)
            if kind=='performance':
                extra=QLabel(f"Avg EMG: {self.metrics.get('avg_emg',0):.1f}  /  Delay: {self.metrics.get('avg_input_delay_ms',0):+.1f}ms"); extra.setWordWrap(True); layout.addWidget(extra)
                retry=QPushButton('Play Again'); retry.setObjectName('primary'); retry.clicked.connect(self.main_window.show_game_widget); layout.addWidget(retry)
            row.addWidget(panel,1)
        outer.addLayout(row,1)
        back=QPushButton('Back to Start'); back.clicked.connect(self.main_window.show_start_screen); outer.addWidget(back)
