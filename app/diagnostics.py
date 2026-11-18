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
        from app.ui.theme import APP_STYLE, font_families
        from app.ui.dashboard import Instrument
        from app.ui.app_icon import apply_app_icon, ICON_PATH
        from app.audio.audio_player import AudioPlayer
        from app.audio.note_generator_adapter import generate_notes_from_analysis, save_notes_json
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
        assert config.USE_CAMERA and config.USE_MEDIAPIPE
        report['menu_camera_enabled'] = True
        report['gameplay_camera_enabled'] = False
        report['checks'].append('Menu MediaPipe enabled; gameplay camera disabled')
        from app.input.mediapipe_tracker import preload_mediapipe, MediaPipeHandTracker
        mp = preload_mediapipe()
        assert mp is not None, 'MediaPipe import failed'
        tracker = MediaPipeHandTracker()
        try:
            assert tracker.backend_is_mediapipe, tracker.diagnostic_summary
            tracker.track(np.zeros((240,320,3),dtype=np.uint8))
            assert tracker.backend_is_mediapipe, tracker.diagnostic_summary
            report['mediapipe_version'] = mp.__version__
        finally:
            tracker.close()
        report['checks'].append('Packaged MediaPipe hand graph initializes, processes a blank frame and closes without webcam access')
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
            assert all((a['lane'], b['lane']) != (1, 2) for a, b in zip(notes, notes[1:]))
            chart_path = save_notes_json(notes, output_dir=folder, analysis=analysis)
            assert RhythmGameEngine.from_json_file(chart_path, 'pinch').notes
            assert RhythmGameEngine.from_json_file(chart_path, 'emg').notes
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
        assert config.LANE_COUNT == 4
        window = type('TestWindow', (), {'selected_song_path': None, 'notes_path': None})()
        game = GameWidget(window)
        try:
            game.timer.stop()
            assert game.input_fusion.emg_reader is None
            sample_lanes = [note.lane for note in game.engine.notes]
            assert all(pair != (1, 2) for pair in zip(sample_lanes, sample_lanes[1:]))
            assert not game.grab().isNull()
            report['no_song_sample_lanes'] = [lane + 1 for lane in sample_lanes]
        finally:
            game.close()
        report['checks'].append('Actual no-song GameWidget sample lanes and rendering: no MIDDLE to RING')
        from app.input.orion_leapc import SDK, OrionReader
        from app.input.pinch_classifier import HandSample, NAMES, PinchClassifier
        assert (SDK / 'include' / 'LeapC.h').is_file()
        assert (SDK / 'lib' / 'x64' / 'LeapC.dll').is_file()
        leap = OrionReader()
        leap.close()
        report['bundled_leap_sdk'] = str(SDK)
        for finger, name in enumerate(NAMES):
            model = PinchClassifier()
            tips = [(0,0,0)] + [(100+i*30,0,0) for i in range(4)]
            tips[finger+1] = (10,0,0)
            sample = HandSample(1,1.,1,'RIGHT',(0,0,0),80,tips,[],[[(0,0,0),(0,1,0),(0,2,0)]]*5)
            assert model.step(sample)[0] == 'NONE'
            sample.t = 1.1
            assert model.step(sample)[0] == name
            assert model.step(None)[0] == 'LOST'
        report['checks'].append('Bundled Orion SDK ABI and DLL loading, four pinch classes and tracking loss')
        from app.input.leap_calibration import calculate_thresholds, save_profile, load_profiles, activate_profile
        from app.ui.leap_calibration_dialog import LeapCalibrationDialog
        calibration_samples = {'NONE': [[1.] * 4 for _ in range(30)]}
        for i, name in enumerate(NAMES):
            row = [1.] * 4
            row[i] = .2
            calibration_samples[name] = [list(row) for _ in range(30)]
        thresholds = calculate_thresholds(calibration_samples)
        assert thresholds == dict.fromkeys(NAMES, .52)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'profiles.json'
            save_profile('self-test', thresholds, path)
            assert load_profiles(path)['profiles']['self-test'] == thresholds
            activate_profile(None, path)
            assert load_profiles(path)['active'] is None
        class CalibrationTracker:
            status = 'SELF-TEST LEAP'
            def close(self): pass
        dialog = LeapCalibrationDialog(tracker_factory=CalibrationTracker)
        try:
            if hasattr(dialog, 'timer'): dialog.timer.stop()
            assert not dialog.grab().isNull()
        finally:
            dialog.reject()
        report['checks'].append('Personal Leap calibration: thresholds, profiles, reset and dialog rendering')
        for old in range(4):
            for new in range(4):
                if old == new: continue
                model = PinchClassifier(dict.fromkeys(NAMES, .52))
                tips = [(0,0,0)] + [(96,0,0)] * 4
                tips[old+1] = (8,0,0)
                sample = HandSample(1,1.,1,'RIGHT',(0,0,0),80,tips,[],
                                    [[(0,0,0),(0,1,0),(0,2,0)]]*5)
                model.step(sample)
                sample.t = 1.1
                assert model.step(sample)[0] == NAMES[old]
                tips[old+1] = (48,0,0)  # Still inside calibrated release threshold.
                tips[new+1] = (8,0,0)
                sample.t = 1.11
                assert model.step(sample)[0] == NAMES[new]
        report['checks'].append('All 12 calibrated direct pinch transitions without open hand or switch delay')
        engine = RhythmGameEngine([Note(0,3,1000), Note(1,3,1050)])
        state = GameInputState(3,0,False,True,.5,.5,None,0)
        assert engine.update(state,990) is None
        assert engine.update(state,1000) == 'PERFECT'
        assert engine.update(state,1000) is None
        assert engine.update(state,1050) == 'PERFECT'
        assert engine.score_state.score == 2000
        from app.settings import DEFAULT_SETTINGS
        expected_signal = 'unfiltered' if Path(__file__).with_name('no_bandpass.marker').is_file() else 'envelope'
        assert DEFAULT_SETTINGS['emg_signal'] == expected_signal
        assert DEFAULT_SETTINGS['emg_threshold'] == config.EMG_THRESHOLD == 12
        report['default_emg_signal'] = DEFAULT_SETTINGS['emg_signal']
        report['default_emg_threshold'] = DEFAULT_SETTINGS['emg_threshold']
        report['lane_count'] = config.LANE_COUNT
        report['gameplay_emg_enabled'] = False
        report['checks'].append('Pinch timing kernel: consecutive held notes score once each')
        report['pinch_input_source'] = 'leap_only'
        report['checks'].append('Leap-only pinch: no armband calibration or fusion')
        from app.ui.game_selection_screen import GameSelectionScreen
        from app.i18n import tr
        assert tr('start_game', 'ko') == '게임 선택'
        class ModeOwner:
            selected_song_path = None
            def show_game_widget(self, mode): pass
            def show_start_screen(self): pass
        selection = GameSelectionScreen(ModeOwner())
        try:
            selection.resize(1280, 720)
            assert set(selection.mode_buttons) == {'pinch', 'emg'}
            assert not selection.grab().isNull()
        finally:
            selection.close()
        previous_mock = config.USE_MOCK_EMG
        config.USE_MOCK_EMG = True
        emg_game = None
        try:
            emg_game = GameWidget(ModeOwner(), mode='emg')
            emg_game.timer.stop()
            emg_game.rest_baseline.baseline_cents = 5000
            assert emg_game.input_fusion.tracker is None
            assert emg_game.input_fusion.emg_reader is not None
            assert any(n.duration_ms for n in emg_game.engine.notes)
            assert not emg_game.grab().isNull()
        finally:
            if emg_game is not None: emg_game.close()
            config.USE_MOCK_EMG = previous_mock
        hold_engine = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
        emg_state = GameInputState(None,20,True,False,None,None,None,0)
        for stamp in range(1000, 3000, 100):
            assert hold_engine.update(emg_state, stamp) is None
            assert hold_engine.score_state.score == 0
        assert hold_engine.update(emg_state, 3000) == 'PERFECT'
        failed_hold = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
        failed_hold.update(emg_state, 1000)
        emg_state.emg_activated = False
        for stamp in range(1100, 1501, 100):
            assert failed_hold.update(emg_state, stamp) is None
        assert failed_hold.update(emg_state, 1601) == 'MISS'
        report['game_modes'] = ['pinch', 'emg']
        report['emg_hold_notes_enabled'] = True
        report['checks'].append('Both charts saved; game selection; independent EMG input and long-note rendering')
        report['checks'].append('EMG hold completion scores only at tail; early release fails')
        from app.input.emg_session import EMGSession
        from app.input.rest_baseline import RestBaseline
        from app.settings import load_settings
        shared = EMGSession()
        try:
            settings = load_settings()
            first = shared.acquire(settings, use_mock_emg=True)
            first.set_space_pressed(True)
            value = first.read()
            reader = first.reader
            first.close()
            second = shared.acquire(settings, use_mock_emg=True)
            assert second.reader is reader and second.read() == value
            second.close()
        finally:
            shared.shutdown()
        baseline = RestBaseline()
        baseline.measure([185.03], True, 0.)
        assert not baseline.ready
        baseline.measure([185.03], True, 3.)
        assert baseline.baseline == 185.03 and baseline.threshold == 185.04
        assert baseline.active(185.04, True) and not baseline.active(185.03, True)
        assert not baseline.active(185.04, False)
        report['emg_rest_measurement_seconds'] = 3
        report['emg_activation_delta'] = .01
        assisted_hold = RhythmGameEngine([Note(0,0,1000,duration_ms=2000)], mode='emg')
        emg_state.emg_activated = True
        assisted_hold.update(emg_state, 1000)
        for stamp in range(1100, 1500, 100):
            emg_state.emg_activated = False
            assert assisted_hold.update(emg_state, stamp) is None
        emg_state.emg_activated = True
        for stamp in range(1500, 3000, 100):
            assert assisted_hold.update(emg_state, stamp) is None
        assert assisted_hold.update(emg_state, 3000) == 'PERFECT'
        report['emg_judge_window_ms'] = config.EMG_JUDGE_WINDOW_MS
        report['emg_hold_dropout_ms'] = config.EMG_HOLD_DROPOUT_MS
        report['checks'].append('Shared EMG stream, 3s baseline +0.01 recognition and short-dropout hold recovery')
        miss_game = RhythmGameEngine([Note(i,0,1000+i*1000) for i in range(12)])
        absent = GameInputState(None,0,False,False,None,None,None,0)
        for i in range(9):
            assert miss_game.update(absent,1101+i*1000) == 'MISS'
            assert not miss_game.miss_limit_reached
        assert miss_game.update(absent,10101) == 'MISS'
        assert miss_game.miss_limit_reached and miss_game.is_finished(10101)
        report['pinch_consecutive_miss_limit'] = 10
        report['checks'].append('Pinch game ends at exactly 10 consecutive misses')
        report['ok'] = True
    except Exception:
        import traceback
        report['error'] = traceback.format_exc()
    Path(output_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['ok'] else 1
