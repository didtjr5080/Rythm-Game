"""Packaged executable self-test without camera, serial or speaker access."""
import json
import tempfile
import shutil
import sys
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
        from app.input.mediapipe_tracker import MediaPipeHandTracker, preload_mediapipe
        from app.input.mediapipe_runtime import create_hands, cpp_runtime_origin, MODEL_FOLDERS
        from app.ui.theme import APP_STYLE, font_families
        from app.ui.dashboard import Instrument
        from app.ui.app_icon import apply_app_icon, ICON_PATH
        from app.audio.audio_player import AudioPlayer
        from app.audio.note_generator_adapter import generate_notes_from_analysis
        from app import config
        from app.settings import DEFAULT_SETTINGS
        assert DEFAULT_SETTINGS['note_speed'] == config.NOTE_SPEED
        report['default_note_speed'] = DEFAULT_SETTINGS['note_speed']
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
            report['model_path_ascii'] = str(tracker.model_root).isascii()
            report['cpp_runtime'] = cpp_runtime_origin()
            if getattr(sys, 'frozen', False) and sys.platform=='win32':
                assert report['cpp_runtime'] not in ('external-system-runtime','not-loaded')
            assert not tracker.track(np.zeros((240,320,3),dtype=np.uint8))['hand_visible']
        finally:
            tracker.close()
        report['checks'].append('MediaPipe Hands native model inference with Qt')
        with tempfile.TemporaryDirectory() as folder:
            mp=preload_mediapipe()
            unicode_root=Path(folder)/'\ud55c\uae00 \uacbd\ub85c'
            for name in MODEL_FOLDERS:
                shutil.copytree(Path(mp.__file__).parent/'modules'/name,unicode_root/'mediapipe'/'modules'/name)
            hands, model_root=create_hands(mp,resource_root=unicode_root)
            try:
                assert not hands.process(np.zeros((240,320,3),dtype=np.uint8)).multi_hand_landmarks
            finally:
                hands.close()
            report['unicode_model_inference']=True
        report['checks'].append('Unicode model path native inference')
        from app.input.live_video import LiveVideoWorker
        import time
        class TestCamera:
            capture = True
            status = 'SELF-TEST CAMERA'
            def __init__(self, settings): pass
            def read(self): return np.zeros((240,320,3), dtype=np.uint8)
            def release(self): self.capture = None
        video = LiveVideoWorker(dict(camera_enabled=True,camera_flip=True), camera_factory=TestCamera)
        try:
            deadline = time.monotonic()+15
            while video.read() is None:
                assert time.monotonic()<deadline, video.diagnostic_summary
                time.sleep(.01)
            assert video.backend_is_mediapipe, video.diagnostic_summary
            assert not video.track(video.read())['hand_visible']
        finally:
            video.close()
            video._thread.join(5)
        assert not video._thread.is_alive()
        report['background_hand_tracking'] = True
        report['checks'].append('Background native hand inference, latest-frame delivery and worker shutdown')
        from app.input.hand_gestures import FoldGestures
        from app.ui.hand_cursor import HandCursorController
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import QPointF
        gestures = FoldGestures()
        for moment,count in ((0.,5),(.12,5),(.16,0),(.26,0),(.30,5),(.42,5),(.46,0)):
            assert gestures.feed(count,count==0,moment,None) is None
        assert gestures.feed(0,True,.56,None)[0] == 'scroll'
        assert gestures.scrolling and gestures.advance(2.) is None
        cursor_host = QWidget()
        cursor_host.resize(320,240)
        cursor = HandCursorController(cursor_host)
        cursor.attach(cursor_host, lambda: None)
        cursor.timer.stop()
        cursor.overlay.move_ring(QPointF(160,120), True)
        assert not cursor.overlay.grab().isNull()
        cursor.detach()
        cursor_host.close()
        report['hand_navigation'] = True
        report['checks'].append('App-local cursor ring and fold/double-fold gesture state machine')
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
            assert notes and all(0<=n['lane']<config.LANE_COUNT for n in notes)
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
        from app.game.rhythm_game_engine import RhythmGameEngine
        from app.game.note import Note
        from app.input.input_fusion import GameInputState
        assert config.LANE_COUNT == 5
        assert [MediaPipeHandTracker.finger_count_to_lane(i) for i in range(6)] == [None,0,1,2,3,4]
        engine = RhythmGameEngine([Note(0,4,1000), Note(1,4,1050)])
        state = GameInputState(4,0,False,True,.5,.5,5,0)
        assert engine.update(state,990) is None
        state.emg_activated = True
        assert engine.update(state,1000) == 'PERFECT'
        assert engine.update(state,1050) is None
        from app.settings import DEFAULT_SETTINGS
        assert DEFAULT_SETTINGS['emg_signal'] == 'envelope'
        assert DEFAULT_SETTINGS['emg_threshold'] == config.EMG_THRESHOLD == 12
        report['default_emg_signal'] = DEFAULT_SETTINGS['emg_signal']
        report['default_emg_threshold'] = DEFAULT_SETTINGS['emg_threshold']
        report['lane_count'] = config.LANE_COUNT
        report['checks'].append('Five finger-count lanes, no hit without activation, one hit per contraction')
        report['ok'] = True
    except Exception:
        import traceback
        report['error'] = traceback.format_exc()
    Path(output_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['ok'] else 1
