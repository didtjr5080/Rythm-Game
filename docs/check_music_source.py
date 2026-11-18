"""Audio source identity and invalid analysis/cache regression checks."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.audio.beat_analyzer import analyze_audio_file
from app.audio import note_generator_adapter as adapter


class MusicSourceChecks(unittest.TestCase):
    def test_same_size_and_mtime_replacement_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(adapter, 'notes_dir', return_value=Path(folder)):
            song = Path(folder)/'song.wav'; song.write_bytes(b'original')
            chart = adapter.save_notes_json([{'lane': 0, 'hit_time_ms': 1000}], song_path=song,
                                            analysis={'duration': 5, 'beats': [1, 2, 3]})
            self.assertEqual(adapter.find_saved_notes_for_song(song), chart)
            stat = song.stat()
            song.write_bytes(b'replaced')
            os.utime(song, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            self.assertIsNone(adapter.find_saved_notes_for_song(song))

    def test_changed_after_analysis_preserves_previous_chart(self):
        with tempfile.TemporaryDirectory() as folder:
            song = Path(folder)/'song.wav'; song.write_bytes(b'original')
            notes = [{'lane': 0, 'hit_time_ms': 1000}]
            analysis = {'duration': 5, 'beats': [1, 2, 3], 'audio_signature': adapter.audio_signature(song)}
            chart = adapter.save_notes_json(notes, output_dir=folder, song_path=song, analysis=analysis)
            previous = chart.read_bytes()
            song.write_bytes(b'replacement')
            with self.assertRaisesRegex(ValueError, 'changed after analysis'):
                adapter.save_notes_json(notes, output_dir=folder, song_path=song, analysis=analysis)
            self.assertEqual(chart.read_bytes(), previous)

    def test_source_change_during_analysis_is_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            song = Path(folder)/'song.wav'; song.write_bytes(b'original')
            def analyze(path):
                song.write_bytes(b'replaced')
                return {'duration': 1, 'sample_rate': 8000}
            with patch('audio_analyzer.analyze_audio', side_effect=analyze):
                with self.assertRaisesRegex(RuntimeError, 'changed during analysis'):
                    analyze_audio_file(str(song))

    def test_analysis_provenance_uses_decoded_frames(self):
        with tempfile.TemporaryDirectory() as folder:
            song = Path(folder)/'song.wav'; song.write_bytes(b'audio')
            with patch('audio_analyzer.analyze_audio', return_value={'duration': 1.5, 'sample_rate': 8000}):
                analysis = analyze_audio_file(str(song))
            self.assertEqual(analysis['audio_source']['decoded_frames'], 12000)
            self.assertEqual(analysis['audio_source']['duration_basis'], 'decoded_pcm')
            self.assertEqual(analysis['audio_signature'], adapter.audio_signature(song))

    def test_invalid_real_song_analysis_never_returns_sample_notes(self):
        for analysis in ({'file_id': 'song'}, {'duration': 0}, {'duration': float('nan')}, {'duration': float('inf')}):
            with self.subTest(analysis=analysis), self.assertRaises(ValueError):
                adapter.generate_notes_from_analysis(analysis)

    def test_empty_and_malformed_mode_caches_are_regenerated(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(adapter, 'notes_dir', return_value=Path(folder)):
            song = Path(folder)/'song.wav'; song.write_bytes(b'audio')
            chart = adapter.save_notes_json([{'lane': 0, 'hit_time_ms': 1000}], song_path=song,
                                            analysis={'duration': 5, 'beats': [1, 2, 3]})
            valid = json.loads(chart.read_text())
            for key, bad in (('emg_notes', []), ('notes', [{'hit_time_ms': -1}]),
                             ('emg_notes', [{'hit_time_ms': 'bad'}])):
                payload = dict(valid); payload[key] = bad
                chart.write_text(json.dumps(payload))
                self.assertIsNone(adapter.find_saved_notes_for_song(song))
