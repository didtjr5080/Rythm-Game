Architecture Decisions

Purpose

Record notable design choices visible in the current implementation.

Confirmed Facts

EXTRACTED: The game is implemented as a PyQt6 desktop application.
EXTRACTED: legacy_web/ is preserved and referenced by adapter modules for audio and note generation.
EXTRACTED: Mock EMG input is supported for testing without hardware.
EXTRACTED: Keyboard lane fallback is supported when hand tracking is unavailable.
EXTRACTED: Songs and notes are stored locally under app/data/.
EXTRACTED: This effort adds documentation and visualization only, without gameplay changes.

Related Files

[README.md](README.md)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

Flow

Document design decisions -> Align with code -> Avoid feature changes

Notes

These decisions are based on the current implementation and should be updated if architecture changes.

TODO

Confirm if any pending refactor plans exist in project discussions.
