"""Real native model inference from Unicode paths, cache repair and error visibility."""
import sys, shutil
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.input.mediapipe_tracker import preload_mediapipe, MediaPipeHandTracker
from app.input.mediapipe_runtime import create_hands, resolve_model_root, MODEL_FOLDERS
mp=preload_mediapipe()
assert mp is not None
import numpy as np
from mediapipe.python import solution_base
root=ROOT/'build'/'portability'/('\ud55c\uae00 \uacbd\ub85c')
modules=Path(mp.__file__).parent/'modules'
for folder in MODEL_FOLDERS:
    shutil.copytree(modules/folder,root/'mediapipe'/'modules'/folder,dirs_exist_ok=True)
old_file=solution_base.__file__
# Force the cache path, covering PCs with 8.3 names disabled and Unicode TEMP.
base=ROOT/'build'/'portability'/'ascii-model-cache'
with patch('app.input.mediapipe_runtime._short_ascii_path',return_value=None),patch('app.input.mediapipe_runtime._cache_bases',return_value=iter([base])):
    hands, model_root=create_hands(mp,resource_root=root)
    try: assert not hands.process(np.zeros((240,320,3),dtype=np.uint8)).multi_hand_landmarks
    finally: hands.close()
assert str(model_root).isascii() and solution_base.__file__==old_file
asset=model_root/'mediapipe/modules/hand_landmark/hand_landmark_full.tflite'
asset.write_bytes(b'corrupt')
with patch('app.input.mediapipe_runtime._short_ascii_path',return_value=None),patch('app.input.mediapipe_runtime._cache_bases',return_value=iter([base])):
    repaired=resolve_model_root(root)
assert (repaired/'mediapipe/modules/hand_landmark/hand_landmark_full.tflite').read_bytes()==(modules/'hand_landmark/hand_landmark_full.tflite').read_bytes()
with patch('app.input.mediapipe_runtime.create_hands',side_effect=FileNotFoundError('model missing / TEST')):
    tracker=MediaPipeHandTracker()
assert not tracker.available
tracker.track(np.zeros((240,320,3),dtype=np.uint8))
assert 'model missing / TEST' in tracker.diagnostic_summary and 'INACTIVE' in tracker.diagnostic_summary
tracker.close()
print('PASS: real Unicode-path inference through ASCII cache; Python metadata restored; cache corruption repaired; initialization error persists through fallback')

# A failed native construction must not leak its temporary module metadata.
with patch('mediapipe.python.solutions.hands.Hands',side_effect=RuntimeError('TEST CONSTRUCTION FAILURE')):
    try: create_hands(mp,resource_root=root)
    except RuntimeError: pass
assert solution_base.__file__==old_file
import os
with patch('app.input.mediapipe_runtime.tempfile.gettempdir',return_value=str(root)),patch.dict(os.environ,{'PUBLIC':str(ROOT/'build'/'portability'/'public-ascii')}):
    from app.input.mediapipe_runtime import _cache_bases
    candidates=list(_cache_bases())
    assert candidates and all(str(p).isascii() for p in candidates)
print('PASS: constructor failure cleanup and Unicode TEMP fallback')
