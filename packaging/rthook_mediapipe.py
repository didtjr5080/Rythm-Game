"""Initialize numerical libraries before Qt's native DLLs in frozen Windows builds."""
import os
import tempfile
# Numba needs a writable cache even when the portable directory is read-only.
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(tempfile.gettempdir(), 'emg-motion-rhythm', 'numba'))
from app.input.mediapipe_tracker import preload_mediapipe
preload_mediapipe()
