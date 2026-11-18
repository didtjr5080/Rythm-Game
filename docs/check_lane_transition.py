"""python -m unittest docs.check_lane_transition -v"""
import itertools
import json
import tempfile
import unittest
from unittest.mock import patch

from app.audio.note_generator_adapter import (
    chart_to_motion_notes, generate_notes_from_analysis, save_notes_json, simplify_for_emg,
)
from app.game.rhythm_game_engine import RhythmGameEngine
from app.game.note import Note


class LaneTransitionChecks(unittest.TestCase):
    def test_engine_enforces_rule_after_sorting(self):
        engine = RhythmGameEngine([Note(2, 2, 3000), Note(0, 1, 1000), Note(1, 2, 2000)])
        self.assertEqual([note.lane for note in engine.notes], [1, 0, 2])
        self.assertEqual([note.hit_time_ms for note in engine.notes], [1000, 2000, 3000])
        with tempfile.TemporaryDirectory() as directory:
            from pathlib import Path
            path = Path(directory) / 'old-chart.json'
            path.write_text(json.dumps({'notes': [{'lane': 1, 'hit_time_ms': 1000},
                                                  {'lane': 2, 'hit_time_ms': 2000}]}))
            self.assertEqual([n.lane for n in RhythmGameEngine.from_json_file(path).notes], [1, 0])

    def assert_allowed(self, notes):
        self.assertTrue(all((a['lane'], b['lane']) != (1, 2)
                            for a, b in zip(notes, notes[1:])))

    def test_all_five_note_sequences(self):
        for lanes in itertools.product(range(4), repeat=5):
            raw = [{'lane': lane, 'hit_time_ms': i*1000} for i, lane in enumerate(lanes)]
            notes = simplify_for_emg(raw)
            self.assert_allowed(notes)
            self.assertEqual(len(notes), len(raw))
            self.assertEqual([n['hit_time_ms'] for n in notes], [n['hit_time_ms'] for n in raw])
            self.assertEqual(simplify_for_emg(notes), notes)
            for i, original in enumerate(raw):
                if notes[i]['lane'] != original['lane']:
                    self.assertEqual((notes[i-1]['lane'], original['lane'], notes[i]['lane']), (1, 2, 0))

    def test_timing_pruning_and_sorting(self):
        raw = [{'lane': 2, 'hit_time_ms': 1000}, {'lane': 0, 'hit_time_ms': 100},
               {'lane': 1, 'hit_time_ms': 0}]
        self.assertEqual([n['lane'] for n in simplify_for_emg(raw)], [1, 0])

    def test_generate_save_and_fallback(self):
        chart = {'notes': [{'lane': 1, 'time': 1}, {'lane': 2, 'time': 2}]}
        self.assert_allowed(chart_to_motion_notes(chart))
        with patch('note_generator.generate_notes', return_value=chart):
            self.assert_allowed(generate_notes_from_analysis({}))
        with patch('note_generator.generate_notes', side_effect=ValueError('test fallback')):
            self.assert_allowed(generate_notes_from_analysis({}))
        with tempfile.TemporaryDirectory() as directory:
            path = save_notes_json([{'lane': 1, 'hit_time_ms': 1000},
                                    {'lane': 2, 'hit_time_ms': 2000}], output_dir=directory)
            notes = json.loads(path.read_text())['notes']
            self.assertEqual([n['lane'] for n in notes], [1, 0])
            self.assert_allowed(notes)
        self.assertTrue(all((a.lane, b.lane) != (1, 2) for a, b in zip(
            RhythmGameEngine.generate_sample_notes(), RhythmGameEngine.generate_sample_notes()[1:])))
