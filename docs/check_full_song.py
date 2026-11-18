"""Full-track lifecycle and source/PCM checks without physical hardware."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
import numpy as np
import soundfile as sf
from PyQt6.QtWidgets import QApplication
from app import config
from app.audio.audio_player import AudioPlayer
from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.input_fusion import GameInputState
from app.ui.game_widget import GameWidget


class FullSongChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_entire_pcm_submission_latency_clock_and_natural_end(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'track.wav'
            sf.write(path, np.zeros(24000, dtype=np.float32), 8000)
            started, done = threading.Event(), threading.Event()
            def play(data, rate, blocking):
                self.assertEqual((data.shape, rate), ((24000, 2), 8000))
                started.set()
            device = NS(play=play, wait=lambda: done.wait(3), get_stream=lambda: NS(latency=.125))
            with patch.dict(sys.modules, {'sounddevice': device}):
                player = AudioPlayer(str(path))
                player.play()
                try:
                    self.assertTrue(started.wait(3))
                    with player._play_lock:
                        self.assertIsNotNone(player.started_at)
                    for seconds in (-.05, 0., 1.5, 2.99):
                        with patch('app.audio.audio_player.time.monotonic', return_value=player.started_at+seconds):
                            self.assertAlmostEqual(player.position_ms, max(0, int(seconds*1000)), delta=1)
                    self.assertEqual(player.output_latency_seconds, .125)
                finally:
                    done.set()
                    player._thread.join(3)
                self.assertTrue(player.finished)
                self.assertIsNone(player.error)
                self.assertEqual(player.position_ms, 3000)

    def test_stop_during_decode_never_starts_stale_track(self):
        entered, release = threading.Event(), threading.Event()
        def decode():
            entered.set()
            if not release.wait(3): raise TimeoutError('test decoder not released')
            return np.zeros(8000, dtype=np.float32), 8000
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'track.wav'; path.touch()
            device = Mock()
            with patch.dict(sys.modules, {'sounddevice': device}):
                player = AudioPlayer(str(path))
                with patch.object(player, '_load_audio', side_effect=decode):
                    player.play()
                    try:
                        self.assertTrue(entered.wait(3))
                        player.stop()
                    finally:
                        release.set(); player._thread.join(3)
                device.play.assert_not_called()
                self.assertTrue(player.finished)
                self.assertIsNone(player.error)
                self.assertEqual(player.position_ms, 0)

    def test_stop_freezes_clock_and_replay_resets_duration(self):
        player = AudioPlayer(None); player.started_at = 10.; player.duration_seconds = 20.
        with patch('app.audio.audio_player.time.monotonic', return_value=12.): player.stop()
        with patch('app.audio.audio_player.time.monotonic', return_value=99.): self.assertEqual(player.position_ms, 2000)
        player.play()
        self.assertEqual(player.position_ms, 0)
        self.assertEqual(player.duration_seconds, 0)

    def test_device_error_and_invalid_pcm(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'track.wav'; path.touch()
            for data, error in ((np.zeros(80), OSError('device lost')), (np.array([np.nan]), None), (np.zeros(0), None)):
                device = NS(play=Mock(side_effect=error))
                with self.subTest(frames=len(data)), patch.dict(sys.modules, {'sounddevice': device}):
                    player = AudioPlayer(str(path))
                    with patch.object(player, '_load_audio', return_value=(data, 8000)):
                        player.play(); player._thread.join(3)
                    self.assertTrue(player.finished)
                    self.assertTrue(player.error)

    def test_both_modes_wait_for_audio_after_last_note(self):
        for mode in ('pinch', 'emg'):
            engine = RhythmGameEngine([Note(0, 0, 1000)], mode=mode)
            engine.notes[0].judged = True
            audio = NS(error=None, finished=False, position_ms=203000)
            game = NS(mode=mode, song_path='track.mp3', audio_player=audio, engine=engine, rest_baseline=None, start_time=0)
            self.assertFalse(GameWidget._should_finish(game, 203000))
            self.assertEqual(GameWidget._playback_time_ms(game), 203000)
            audio.finished = True
            self.assertTrue(GameWidget._should_finish(game, 213770))
            game.song_path = None
            self.assertTrue(GameWidget._should_finish(game, 203000))

    def test_214_second_chart_with_final_hold_both_modes(self):
        for mode in ('pinch', 'emg'):
            notes = [Note(i, i % 4 if mode == 'pinch' else 0, 1000+i*1000) for i in range(210)]
            if mode == 'emg':
                from app.game.emg_chart import generate_emg_notes
                notes = [RhythmGameEngine.normalize_note_dict(n, i) for i, n in enumerate(
                    generate_emg_notes([], {'duration': 214., 'bpm': 120.}))]
                self.assertTrue(all(n.duration_ms >= 1000 for n in notes))
            engine = RhythmGameEngine(notes, mode=mode)
            for stamp in range(0, 214001, 20):
                note = next((n for n in engine.notes if not n.judged), None)
                active = note is not None and note.hit_time_ms <= stamp <= note.end_time_ms
                state = GameInputState(note.lane if note else None, 20. if active else 0., active, True, .5, .5, 1, stamp/1000)
                engine.update(state, stamp)
            self.assertEqual(engine.score_state.hit_count, len(notes), mode)
            self.assertEqual(engine.score_state.miss_count, 0, mode)
            self.assertTrue(all(n.judged for n in engine.notes))

    def test_natural_eof_accounts_for_final_notes(self):
        for mode in ('pinch', 'emg'):
            engine = RhythmGameEngine([Note(0, 0, 2990), Note(1, 0, 2995)], mode=mode)
            game = NS(finished=False, song_path='track.wav', mode=mode,
                      audio_player=NS(error=None, loading=False, finished=True), engine=engine,
                      _playback_time_ms=lambda: 3000,
                      input_fusion=NS(read=lambda frame: (GameInputState(None, 0., False, False, None, None, None, 0.), None)),
                      rest_baseline=NS(ready=True, active=lambda *a: False) if mode == 'emg' else None,
                      ripples=[], session_logger=Mock(), finish_game=Mock(), input_delays_ms=[], result_flash=None,
                      _should_finish=lambda stamp: True)
            GameWidget.game_loop(game)
            self.assertEqual(engine.score_state.miss_count, 2)
            self.assertEqual(engine.consecutive_misses, 2)
            self.assertTrue(all(n.judged for n in engine.notes))
            engine.finalize_unjudged_notes()
            self.assertEqual(engine.score_state.miss_count, 2)
            game.finish_game.assert_called_once()

    def test_errors_and_cancel_both_modes_never_score(self):
        for mode in ('pinch', 'emg'):
            owner = NS(show_start_screen=Mock())
            with patch('app.ui.game_widget.AudioPlayer', return_value=Mock(error='output failed', loading=False)), \
                 patch('app.ui.game_widget.InputFusion'), patch('app.ui.game_widget.QMessageBox.warning') as warning:
                game = GameWidget(owner, song_path='track.mp3', mode=mode); game.timer.stop()
                game.game_loop()
                self.assertTrue(game.finished)
                self.assertEqual(game.engine.score_state.judged_count, 0)
                owner.show_start_screen.assert_called_once(); warning.assert_called_once()
                game.game_loop(); warning.assert_called_once()
                game.close()
            owner = NS(show_start_screen=Mock())
            with patch('app.ui.game_widget.AudioPlayer'), patch('app.ui.game_widget.InputFusion'):
                game = GameWidget(owner, song_path='track.mp3', mode=mode); game.timer.stop()
                game.abort_game()
                self.assertEqual(game.engine.score_state.judged_count, 0)
                owner.show_start_screen.assert_called_once()
                game.close()


def inspect_real_song(path):
    from app.audio.beat_analyzer import analyze_audio_file
    from app.audio.note_generator_adapter import generate_notes_from_analysis
    from app.game.emg_chart import generate_emg_notes
    import audio_analyzer
    analysis = analyze_audio_file(str(path))
    decoder = AudioPlayer(str(path))
    decoded, rate = decoder._load_audio()
    assert decoded is not None
    analyzed, analysis_rate = audio_analyzer.librosa.load(str(path), sr=None, mono=True)
    mono = decoded.mean(axis=1) if decoded.ndim == 2 else decoded
    np.testing.assert_array_equal(mono, analyzed)
    assert analysis_rate == rate and analysis['duration'] == len(decoded)/rate
    notes = generate_notes_from_analysis(analysis)
    submitted = threading.Event()
    def play(data, sample_rate, blocking):
        expected = decoded if decoded.ndim == 2 else np.column_stack([decoded, decoded])
        np.testing.assert_array_equal(data, np.clip(expected*.85, -1, 1))
        assert sample_rate == rate
        submitted.set()
    device = NS(play=play, wait=lambda: None, get_stream=lambda: NS(latency=.05))
    with patch.dict(sys.modules, {'sounddevice': device}):
        player = AudioPlayer(str(path)); player.play(); player._thread.join(30)
        assert player.finished and player.error is None and submitted.is_set()
        assert player.position_ms == int(analysis['duration']*1000)
    checkpoints = {}
    for mode, raw in (('pinch', notes), ('emg', generate_emg_notes(notes, analysis))):
        engine = RhythmGameEngine([RhythmGameEngine.normalize_note_dict(n, i) for i, n in enumerate(raw)], mode=mode)
        stamps = []
        for index in (0, len(engine.notes)//2, len(engine.notes)-1):
            note = engine.notes[index]
            y = next(y for n, y in engine.visible_notes(note.hit_time_ms, 900) if n.note_id == note.note_id)
            assert y == 900*config.JUDGEMENT_LINE_Y_RATIO
            stamps.append(note.hit_time_ms)
        checkpoints[mode] = stamps
    info = sf.info(str(path))
    return {'source': analysis['audio_source'], 'sha256': analysis['audio_signature']['sha256'],
            'playback_decoder': decoder.decoder_backend,
            'soundfile_version': sf.__version__, 'libsndfile_version': sf.__libsndfile_version__,
            'analysis_loader': str(Path(audio_analyzer.librosa.__file__).resolve()),
            'librosa_version': audio_analyzer.librosa.__version__,
            'metadata_frames': info.frames, 'metadata_duration': info.duration,
            'decoded_frames': len(decoded), 'decoded_duration': len(decoded)/rate,
            'sample_rate': rate, 'waveform_max_error': float(np.max(np.abs(mono-analyzed))),
            'checkpoint_ms': checkpoints, 'physical_output_tested': False}
