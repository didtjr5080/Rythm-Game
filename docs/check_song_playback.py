"""python -m unittest docs.check_song_playback -q (no camera or serial access)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch,PropertyMock
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication
from app.settings import DEFAULT_SETTINGS
from app.ui.main_window import MainWindow
from app.ui.start_screen import StartScreen
from app.ui.game_selection_screen import GameSelectionScreen
from app.audio.note_generator_adapter import save_notes_json,find_saved_notes_for_song,generate_notes_from_analysis
from app.audio.beat_analyzer import analyze_audio_file
from app.input.emg_session import EMGSession
from docs.check_emg_assistance import FakeSerialReader


class SongPlaybackChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])

    def test_music_generation_failure_never_returns_sample_notes(self):
        with patch('note_generator.generate_notes',side_effect=ValueError('failed')):
            with self.assertRaises(RuntimeError):generate_notes_from_analysis({'duration':10,'beats':[1,2]})
        with patch('audio_analyzer.analyze_audio',side_effect=ValueError('bad audio')):
            with self.assertRaises(RuntimeError):analyze_audio_file('broken.mp3')

    def test_chart_cache_is_bound_to_audio_file_and_old_cache_is_regenerated(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); song=root/'song.wav';song.write_bytes(b'original')
            with patch('app.audio.note_generator_adapter.notes_dir',return_value=root):
                chart=save_notes_json([{'lane':0,'hit_time_ms':1000}],output_dir=root,song_path=song,analysis={'duration':5,'beats':[1,2,3]})
                self.assertEqual(find_saved_notes_for_song(song),chart)
                song.write_bytes(b'changed and longer')
                self.assertIsNone(find_saved_notes_for_song(song))
                chart.write_text(json.dumps({'schema_version':2,'notes':[{'lane':0,'hit_time_ms':1000}]}))
                self.assertIsNone(find_saved_notes_for_song(song))

    def test_single_click_selects_actual_song_and_play_auto_generates_chart(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); songs=root/'songs';songs.mkdir();notes=root/'notes'
            a=songs/'a_1.wav';b=songs/'b_2.wav';a.write_bytes(b'a');b.write_bytes(b'b')
            tracker=Mock(status='FAKE',last_error=None);tracker.track.return_value={'hand_visible':False,'lane':None}
            analysis={'duration':10.,'bpm':120.,'beats':[i*.5 for i in range(20)],'onsets':[1.,2.,3.], 'onset_strengths':[1.,1.,1.]}
            with patch('app.ui.start_screen.StartScreen.songs_dir',new_callable=PropertyMock,return_value=songs), \
                 patch('app.audio.note_generator_adapter.notes_dir',return_value=notes), \
                 patch('app.ui.main_window.load_settings',return_value=dict(DEFAULT_SETTINGS,camera_enabled=False)), \
                 patch('app.config.USE_CAMERA',False),patch('app.config.USE_MOCK_EMG',True), \
                 patch('app.input.input_fusion.LeapPinchTracker',return_value=tracker), \
                 patch('app.ui.start_screen.analyze_audio_file',return_value=analysis):
                window=MainWindow()
                try:
                    screen=window.centralWidget()
                    item=next(screen.song_list.item(i) for i in range(screen.song_list.count()) if screen.song_list.item(i).data(Qt.ItemDataRole.UserRole)==str(b))
                    screen.song_list.setCurrentItem(item)
                    self.assertEqual(window.selected_song_path,str(b))
                    window.show_game_selection()
                    deadline=time.monotonic()+3
                    while not isinstance(window.centralWidget(),GameSelectionScreen) and time.monotonic()<deadline:QTest.qWait(20)
                    self.assertIsInstance(window.centralWidget(),GameSelectionScreen)
                    self.assertEqual(window.notes_path,str(find_saved_notes_for_song(b)))
                    payload=json.loads(Path(window.notes_path).read_text())
                    self.assertEqual(payload['audio_signature']['filename'],b.name)
                    self.assertTrue(payload['notes'])
                    self.assertTrue(payload['emg_notes'])
                finally:window.close()

    def test_native_connection_survives_auto_to_actual_port_and_irrelevant_signal_settings(self):
        session=EMGSession()
        settings=dict(DEFAULT_SETTINGS,emg_port='auto',emg_backend='oymotion')
        reader=FakeSerialReader(port='auto',baudrate=115200,threshold=12,device_id='',signal='envelope',release_threshold=None)
        reader.connected=True;reader.error=None;reader.port='COM4';reader.connected_identity='oymotion:test'
        with patch('app.input.emg_session.create_emg_reader',return_value=reader) as create:
            try:
                first=session.acquire(settings,use_mock_emg=False)
                first.close()
                second=session.acquire(dict(settings,emg_port='COM4',emg_device_id='oymotion:test',emg_signal='unfiltered'),use_mock_emg=False)
                self.assertIs(second.reader,reader)
                self.assertEqual(create.call_count,1)
                self.assertIsNotNone(reader.serial)
            finally:session.shutdown()

    def test_playback_error_aborts_before_note_judgement(self):
        from app.ui.game_widget import GameWidget
        owner=SimpleNamespace(show_start_screen=Mock())
        player=Mock(error='output unavailable',loading=False)
        with patch('app.ui.game_widget.AudioPlayer',return_value=player),patch('app.ui.game_widget.QMessageBox.warning') as warning, \
             patch('app.input.input_fusion.LeapPinchTracker',return_value=Mock(status='FAKE',last_error=None)):
            game=GameWidget(owner,song_path='song.wav')
            try:
                game.timer.stop()
                game.game_loop()
                self.assertTrue(game.finished)
                self.assertEqual(game.engine.score_state.score,0)
                owner.show_start_screen.assert_called_once()
                warning.assert_called_once()
            finally:game.close()
