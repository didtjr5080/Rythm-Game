"""Native DLL discovery and ASCII model paths for MediaPipe 0.10.21 on Windows."""
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading

_dll_handles = []
_native_handles = []
_prepared = False
_model_lock = threading.RLock()
MODEL_FOLDERS = ('hand_landmark', 'palm_detection')
REQUIRED_MODELS = (
    'hand_landmark/hand_landmark_tracking_cpu.binarypb',
    'hand_landmark/hand_landmark_full.tflite',
    'hand_landmark/hand_landmark_lite.tflite',
    'palm_detection/palm_detection_full.tflite',
    'palm_detection/palm_detection_lite.tflite',
)


def prepare_native_runtime():
    """Expose C++ runtimes before MediaPipe, without importing any Qt modules."""
    global _prepared
    if _prepared or sys.platform != 'win32':
        return
    import ctypes
    roots = []
    if getattr(sys, 'frozen', False):
        roots.append(Path(sys._MEIPASS))
    else:
        roots.append(Path(os.environ.get('SystemRoot', 'C:/Windows'))/'System32')
    for root in roots:
        for directory in (root, root/'mediapipe'/'python'):
            if directory.is_dir():
                _dll_handles.append(os.add_dll_directory(str(directory)))
        runtime = root/'MSVCP140.dll'
        if runtime.is_file():
            _native_handles.append(ctypes.WinDLL(str(runtime)))
            break
    _prepared = True


def _short_ascii_path(path):
    if str(path).isascii() and len(str(path)) < 150:
        return path
    if sys.platform != 'win32':
        return None
    import ctypes
    function = ctypes.windll.kernel32.GetShortPathNameW
    function.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
    function.restype = ctypes.c_uint
    buffer = ctypes.create_unicode_buffer(32768)
    length = function(str(path), buffer, len(buffer))
    if 0 < length < len(buffer) and buffer.value.isascii() and len(buffer.value) < 150:
        return Path(buffer.value)
    return None


def _cache_bases():
    candidates = [Path(tempfile.gettempdir())/'EMGMotionRhythm'/'models']
    if os.environ.get('PUBLIC'):
        candidates.append(Path(os.environ['PUBLIC'])/'Documents'/'EMGMotionRhythm'/'models')
    if sys.platform == 'win32':
        candidates.append(Path(os.environ.get('SystemDrive', 'C:')+'/Users/Public/Documents/EMGMotionRhythm/models'))
    for path in candidates:
        if str(path).isascii() and len(str(path)) < 115:
            yield path


def resolve_model_root(original):
    original = Path(original).resolve()
    modules = original/'mediapipe'/'modules'
    for name in REQUIRED_MODELS:
        if not (modules/name).is_file():
            raise FileNotFoundError(f'MediaPipe model missing: {name}. Extract the entire ZIP including _internal.')
    if sys.platform != 'win32':
        return original
    short = _short_ascii_path(original)
    if short is not None:
        return short
    files = sorted(p for folder in MODEL_FOLDERS for p in (modules/folder).rglob('*')
                   if p.is_file() and p.suffix in ('.tflite', '.binarypb', '.txt'))
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.relative_to(original).as_posix().encode())
        digest.update(file.read_bytes())
    key = 'hands-' + digest.hexdigest()[:16]
    errors = []
    for base in _cache_bases():
        target_root = base/key
        try:
            for file in files:
                target = target_root/file.relative_to(original)
                if target.is_file() and hashlib.sha256(target.read_bytes()).digest() == hashlib.sha256(file.read_bytes()).digest():
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.emg-', delete=False) as output:
                        temporary = Path(output.name)
                        with file.open('rb') as source:
                            shutil.copyfileobj(source, output)
                    os.replace(temporary, target)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
            return target_root
        except OSError as exc:
            errors.append(str(exc))
    raise RuntimeError('MediaPipe needs a writable ASCII model path. Extract to C:/EMG-Motion-Rhythm. ' + '; '.join(errors))


def create_hands(mp, resource_root=None, **options):
    """Keep native model reads off Unicode paths while restoring Python metadata.

    Pinned SolutionBase has no resource-root argument and derives it from its
    module __file__. Redirect that derivation only during serialized construction;
    the resulting graph retains the ASCII resource directory. No global chdir or
    permanent package modification is used.
    """
    from mediapipe.python import solution_base
    with _model_lock:
        original_file = solution_base.__file__
        original_root = Path(original_file).resolve().parents[2]
        root = resolve_model_root(resource_root or original_root)
        try:
            if root != original_root:
                solution_base.__file__ = str(root/'mediapipe'/'python'/'solution_base.py')
            return mp.solutions.hands.Hands(**options), root
        finally:
            solution_base.__file__ = original_file


def cpp_runtime_origin():
    if sys.platform != 'win32':
        return 'not-windows'
    import ctypes
    kernel = ctypes.windll.kernel32
    kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel.GetModuleHandleW.restype = ctypes.c_void_p
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
    handle = kernel.GetModuleHandleW('MSVCP140.dll')
    if not handle:
        return 'not-loaded'
    buffer = ctypes.create_unicode_buffer(32768)
    kernel.GetModuleFileNameW(handle, buffer, len(buffer))
    if getattr(sys, 'frozen', False):
        try:
            return str(Path(buffer.value).resolve().relative_to(Path(sys._MEIPASS).resolve()))
        except ValueError:
            return 'external-system-runtime'
    return Path(buffer.value).name
