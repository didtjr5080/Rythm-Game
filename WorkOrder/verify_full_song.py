"""Run both modes' full-song checks, optionally inspect an actual MP3.

python WorkOrder/verify_full_song.py --real-song --report release/music-check.json
Physical camera, Leap, armband and audio output are never opened.
"""
import argparse
import json
import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from docs.check_full_song import FullSongChecks, inspect_real_song

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--real-song', action='store_true')
    parser.add_argument('--song', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FullSongChecks))
    report = {'ok': result.wasSuccessful(), 'tests': result.testsRun}
    if report['ok'] and (args.real_song or args.song):
        song = args.song or next((ROOT/'app/data/songs').glob('BIGBANG*.mp3'))
        try:
            report['real_song'] = inspect_real_song(song)
            print(json.dumps(report['real_song'], ensure_ascii=True, indent=2))
        except Exception:
            import traceback
            report.update(ok=False, error=traceback.format_exc())
            print(report['error'], file=sys.stderr)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(0 if report['ok'] else 1)
