"""Five-lane selection, legacy charts, and one hit per contraction."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import config
from app.game.note import Note
from app.game.rhythm_game_engine import RhythmGameEngine
from app.input.input_fusion import GameInputState
from app.input.mediapipe_tracker import MediaPipeHandTracker
from app.audio.note_generator_adapter import save_notes_json

assert config.LANE_COUNT == 5
assert [MediaPipeHandTracker.finger_count_to_lane(i) for i in range(6)] == [None, 0, 1, 2, 3, 4]
for lane in range(5):
    engine = RhythmGameEngine([Note(0, lane, 1000), Note(1, lane, 1050)])
    state = GameInputState(lane, 0, False, True, .5, .5, lane+1, 0)
    assert engine.update(state, 990) is None
    state.emg_activated = True
    assert engine.update(state, 1000) == 'PERFECT'
    assert engine.update(state, 1050) is None  # Held contraction cannot hit again.
    state.emg_activated = False
    assert engine.update(state, 1051) is None
    state.emg_activated = True
    assert engine.update(state, 1052) == 'PERFECT'
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder)/'old.json'
    path.write_text(json.dumps([dict(lane=i, hit_time_ms=i*1000) for i in range(3)]))
    assert [n.lane for n in RhythmGameEngine.from_json_file(path).notes] == [0, 2, 4]
    path = save_notes_json([dict(lane=i, hit_time_ms=i*1000) for i in range(5)], folder)
    assert [n.lane for n in RhythmGameEngine.from_json_file(path).notes] == list(range(5))
print('PASS: 5 lanes; fist selects none; no EMG means no hit; held input cannot repeat; release/retrigger; legacy chart migration; new chart roundtrip')
