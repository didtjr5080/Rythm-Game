# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

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
    binaries=mediapipe_binaries,
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
