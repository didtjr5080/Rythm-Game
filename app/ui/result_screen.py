import json
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from uuid import uuid4
from app.background import jobs
from app.atomic_io import atomic_text
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
        self.save_timer=QTimer(self)
        self.save_timer.timeout.connect(self._poll_save)
        if hasattr(self, '_save_future'): self.save_timer.start(100)

    def _save_result(self):
        result_dir = Path(__file__).resolve().parents[1] / "data" / "results"
        path = result_dir / f"result_{time.strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:12]}.json"
        payload = dict(self.metrics)
        self.result_path = path
        session_paths=self.session_paths
        def write():
            paths=session_paths.result() if hasattr(session_paths,'result') else session_paths
            if paths:
                payload['session_json'],payload['session_csv']=map(str,paths)
            atomic_text(path,json.dumps(payload,indent=2))
        self._save_future=jobs.submit(write)

    def _poll_save(self):
        if not self._save_future.done(): return
        self.save_timer.stop()
        try:
            self._save_future.result()
            self.save_status.setText(f'SAVED / {self.result_path.name}')
        except Exception as exc:
            self.save_status.setText(f'SAVE FAILED: {exc}')
            self.retry_save.show()

    def _retry_save(self):
        self.retry_save.hide()
        paths=self.session_paths
        if hasattr(paths,'exception') and paths.done() and paths.exception() is not None:
            logger=getattr(self.main_window,'_last_session_logger',None)
            if logger is not None: self.session_paths=jobs.submit(logger.save)
        self._save_result()
        self.save_status.setText('SAVING...')
        self.save_timer.start(100)

    def _build(self):
        outer=QVBoxLayout(self); outer.setContentsMargins(50,28,50,24)
        title=QLabel('POST-GAME REHABILITATION ANALYTICS'); title.setObjectName('title'); title.setAlignment(Qt.AlignmentFlag.AlignCenter); outer.addWidget(title)
        self.save_status=QLabel(f'SAVING / {self.result_path.name}'); self.save_status.setObjectName('subtitle'); outer.addWidget(self.save_status)
        self.retry_save=QPushButton('Retry Save'); self.retry_save.clicked.connect(self._retry_save); self.retry_save.hide(); outer.addWidget(self.retry_save)
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
