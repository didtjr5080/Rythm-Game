"""Packaged executable self-test without camera, serial or speaker access."""
import json
import tempfile
from pathlib import Path


def run_self_test(output_path):
    report = {'ok': False, 'checks': []}
    try:
        import numpy as np
        import soundfile as sf
        import sounddevice
        import audio_analyzer
        import note_generator
        from PyQt6.QtWidgets import QApplication
        from app.input.mediapipe_tracker import MediaPipeHandTracker
        from app.ui.theme import APP_STYLE, font_families
        from app.ui.dashboard import Instrument
        from app.ui.app_icon import apply_app_icon, ICON_PATH
        from app.audio.audio_player import AudioPlayer
        from app.audio.note_generator_adapter import generate_notes_from_analysis
        from app import config
        from app.game.rhythm_game_engine import RhythmGameEngine
        app = QApplication.instance() or QApplication([])
        assert ICON_PATH.is_file() and not apply_app_icon(app).isNull()
        assert app.windowIcon().availableSizes()
        report['checks'].append('Application icon resource and Qt window icon')
        font_families()
        app.setStyleSheet(APP_STYLE)
        tracker = MediaPipeHandTracker()
        try:
            assert tracker.available, tracker.last_error
            assert not tracker.track(np.zeros((240,320,3),dtype=np.uint8))['hand_visible']
        finally:
            tracker.close()
        report['checks'].append('MediaPipe Hands native model inference with Qt')
        for size in ((1920,1080),(1440,900)):
            widget = Instrument('performance')
            widget.resize(*size)
            assert not widget.grab().isNull()
            widget.close()
        report['checks'].append('Qt rendering at 1920x1080 and 1440x900')
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder)/'self-test.wav'
            samples = np.zeros(8000*6,dtype=np.float32)
            for start in range(0,len(samples),4000): samples[start:start+80] = .5
            sf.write(wav,samples,8000)
            player = AudioPlayer(str(wav))
            data,rate = player._load_audio()
            assert len(data)==len(samples) and rate==8000, player.error
            analysis = audio_analyzer.analyze_audio(str(wav))
            assert abs(analysis['duration']-6)<.01
            notes = generate_notes_from_analysis(analysis)
            assert notes and all(0<=n['lane']<3 for n in notes)
        report['checks'].append('Full audio decode, librosa analysis, legacy note generation')
        from app.ui.game_widget import GameWidget
        from app.ui.start_screen import StartScreen
        from app.ui.settings_screen import SettingsScreen
        from app.ui.calibration_screen import CalibrationScreen
        from app.ui.result_screen import ResultScreen
        from app.input.emg_reader import SerialEMGReader
        from app.input.emg_devices import discover_emg_devices
        assert SerialEMGReader.parse_packet('EMG1 raw:512 filtered:40 seq:2') == (512,40,2)
        assert SerialEMGReader.parse_packet('EMG1 raw:9999 filtered:40 seq:2') is None
        report['checks'].append('EMG device discovery imports and framed serial protocol parser')
        report['checks'].append('All desktop screen imports and audio output library')
        report['ok'] = True
    except Exception:
        import traceback
        report['error'] = traceback.format_exc()
    Path(output_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['ok'] else 1
