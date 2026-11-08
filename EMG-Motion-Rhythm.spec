# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from pathlib import Path
import os

runtime_dir = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32"
cpp_runtimes = [(str(runtime_dir/name), ".") for name in (
    "MSVCP140.dll", "MSVCP140_1.dll", "MSVCP140_2.dll", "CONCRT140.dll",
    "VCRUNTIME140.dll", "VCRUNTIME140_1.dll") if (runtime_dir/name).is_file()]

mediapipe_datas = collect_data_files(
    'mediapipe',
    includes=[
        'modules/hand_landmark/*',
        'modules/palm_detection/*',
    ],
)
mediapipe_binaries = collect_dynamic_libs('mediapipe')
mediapipe_hiddenimports = [
    'mediapipe',
    'mediapipe.python._framework_bindings',
    'mediapipe.python.solutions.hands',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
]

a = Analysis(
    ['app\\main.py'],
    pathex=['legacy_web/backend'],
    binaries=mediapipe_binaries + cpp_runtimes,
    datas=[('app/data/songs/.gitkeep', 'app/data/songs'), ('app/assets', 'app/assets')] + mediapipe_datas,
    hiddenimports=mediapipe_hiddenimports + ['audio_analyzer', 'note_generator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['packaging/rthook_mediapipe.py'],
    excludes=[
        'jax',
        'jaxlib',
        'sklearn',
        'torch',
        'tensorflow',
        'mediapipe.examples',
        'mediapipe.model_maker',
        'mediapipe.tasks.python.genai.converter',
        'mediapipe.tasks.python.genai.bundler',
        'mediapipe.tasks.python.test',
    ],
    module_collection_mode={'librosa': 'py'},
    noarchive=False,
    optimize=0,
)
# Keep all copies of the C++ runtime consistent; Qt wheels may ship older ones.
_runtime_names = {Path(source).name.lower(): source for source, _ in cpp_runtimes}
a.binaries = [(destination, _runtime_names.get(Path(destination).name.lower(), source), kind)
              for destination, source, kind in a.binaries]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EMG-Motion-Rhythm',
    icon='app/assets/app.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EMG-Motion-Rhythm',
)
