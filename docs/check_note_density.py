"""Density migration must keep beat times and never change the saved chart."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from app.game.rhythm_game_engine import RhythmGameEngine
from app.game.emg_chart import generate_emg_notes
from app.audio.note_generator_adapter import simplify_for_emg


class DensityChecks(unittest.TestCase):
    def test_existing_dense_chart_is_reduced_in_all_modes_without_rewriting(self):
        taps = [dict(note_id=i, lane=i%4, hit_time_ms=2000+i*900) for i in range(30)]
        holds = [dict(note_id=i, lane=0, hit_time_ms=2000+i*3000, duration_ms=2000) for i in range(10)]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'chart.json'
            path.write_text(json.dumps(dict(notes=taps, emg_notes=holds)))
            before = hashlib.sha256(path.read_bytes()).digest()
            for mode in ('pinch', 'pinch_extension', 'emg'):
                source = holds if mode == 'emg' else taps
                notes = RhythmGameEngine.from_json_file(path, mode).notes
                self.assertLess(len(notes), len(source))
                self.assertTrue(all(n.hit_time_ms in {s['hit_time_ms'] for s in source} for n in notes))
                self.assertTrue(all(b.hit_time_ms-a.end_time_ms >= 1800 for a,b in zip(notes, notes[1:])))
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).digest())

    def test_new_charts_have_more_rest_without_moving_beats(self):
        raw = [dict(lane=i%4, hit_time_ms=2000+i*900) for i in range(30)]
        notes = simplify_for_emg(raw)
        self.assertEqual(len(notes), 15)
        self.assertEqual([n['hit_time_ms'] for n in notes], [n['hit_time_ms'] for n in raw[::2]])
        holds = generate_emg_notes([], dict(bpm=120, duration=30))
        self.assertTrue(holds)
        self.assertTrue(all(b['hit_time_ms']-a['hit_time_ms']-a['duration_ms'] >= 1800
                            for a,b in zip(holds, holds[1:])))
