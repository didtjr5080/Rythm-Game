System Overview

Purpose

Explain the top-level structure of the PyQt6 rhythm game and how major subsystems connect.

Confirmed Facts

EXTRACTED: The application is launched via a PyQt6 entry point in app/main.py.
EXTRACTED: MainWindow switches between Start, Settings, Calibration, Game, and Result screens.
EXTRACTED: MediaPipe-based hand tracking is used for lane selection when the camera is enabled.
EXTRACTED: EMG input uses SerialEMGReader with a mock fallback when serial input is unavailable.
EXTRACTED: Keyboard lane fallback uses A/S/D or Left/Down/Right and SPACE for mock EMG.
EXTRACTED: Songs and notes are stored under app/data/songs/ and app/data/notes/.
EXTRACTED: Settings are stored in app/data/settings.json.
EXTRACTED: Gameplay sessions are logged to JSON and CSV in app/data/sessions/.
EXTRACTED: Result summaries are saved as JSON files in app/data/results/.
EXTRACTED: legacy_web/ is preserved and audio/note adapters reference the legacy backend modules.

Related Files

[app/main.py](app/main.py)
[app/ui/main_window.py](app/ui/main_window.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/analytics/session_logger.py](app/analytics/session_logger.py)
[app/analytics/game_metrics.py](app/analytics/game_metrics.py)
[app/ui/result_screen.py](app/ui/result_screen.py)
[app/settings.py](app/settings.py)
[README.md](README.md)

Flow

Launch app -> StartScreen -> Select or add song -> Generate or load notes -> GameWidget
GameWidget -> InputFusion (camera + EMG) -> RhythmGameEngine -> Judge -> Score -> ResultScreen

Notes

The game continues even when camera or serial input is unavailable, using fallback inputs.

TODO

Validate any optional calibration flow details in CalibrationScreen.
