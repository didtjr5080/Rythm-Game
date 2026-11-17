"""Faults and cancellation in preparation/persistence must not block Qt."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys
import tempfile
import threading
import json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from app import config
config.USE_CAMERA=False; config.USE_MOCK_EMG=True
from app.ui.main_window import MainWindow
from app.ui.result_screen import ResultScreen
from app.analytics.session_logger import SessionLogger
from app.atomic_io import atomic_text

app=QApplication([])
gate=threading.Event()
window=MainWindow(); window.show(); app.processEvents()
screen=window.centralWidget(); window.selected_song_path='old.wav'
with patch('app.ui.start_screen.analyze_audio_file',side_effect=lambda song:(gate.wait(3) or True) and {}), patch('app.ui.start_screen.save_notes_json',return_value=Path('fake.json')):
    screen.generate_notes()
    assert screen._generation is not None
    window.selected_song_path='new.wav'
    gate.set()
    for _ in range(100):
        QTest.qWait(10)
        if screen._generation is None: break
    assert screen._generation is None and window.notes_path is None
print('PASS: background chart generation remains responsive and changed selection rejects old completion')
with tempfile.TemporaryDirectory() as tmp:
    a,b=SessionLogger(tmp),SessionLogger(tmp)
    assert a.session_id!=b.session_id
    a.save(); b.save(); assert len(list(Path(tmp).glob('*.json')))==2
    target=Path(tmp)/'atomic.json'; atomic_text(target,'{"good":true}')
    with patch('app.atomic_io.os.replace',side_effect=OSError('injected write failure')):
        try: atomic_text(target,'broken')
        except OSError: pass
    assert json.loads(target.read_text())['good'] and not list(Path(tmp).glob('*.tmp'))
    with patch('app.ui.result_screen.atomic_text',side_effect=OSError('injected disk error')):
        result=ResultScreen(window,{'accuracy':100}); result.show()
        for _ in range(100):
            QTest.qWait(10)
            if result._save_future.done(): break
        result._poll_save()
        assert 'SAVE FAILED' in result.save_status.text() and not result.retry_save.isHidden()
    with patch('app.ui.result_screen.atomic_text') as write:
        result._retry_save(); result._save_future.result(timeout=3); result._poll_save()
        assert write.called and result.save_status.text().startswith('SAVED')
    result.close()
window.close()
print('PASS: unique session IDs, atomic write failure preserves original, result save failure and retry')
