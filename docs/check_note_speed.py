import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from app.settings import load_settings,save_settings
class SpeedChecks(unittest.TestCase):
    def test_old_and_out_of_range_settings_are_clamped_on_read_and_save(self):
        with tempfile.TemporaryDirectory() as directory, patch('app.settings.settings_path',return_value=Path(directory)/'settings.json'):
            for value,expected in ((900,200),(360,200),(125,125),(0,50)):
                path=Path(directory)/'settings.json'
                path.write_text(json.dumps({'note_speed':value}))
                self.assertEqual(load_settings()['note_speed'],expected)
                self.assertEqual(save_settings({'note_speed':value})['note_speed'],expected)
                self.assertEqual(json.loads(path.read_text())['note_speed'],expected)
