Runtime Errors

Purpose

Catalog likely runtime issues and their sources.

Confirmed Facts

EXTRACTED: Audio playback reports errors when files are missing or decoding fails.
EXTRACTED: Corrupted settings.json falls back to default settings silently.
INFERRED: Corrupted notes JSON may raise a load error at game start.
INFERRED: Missing song files are reported in the StartScreen logs.
INFERRED: PyQt6 startup errors are possible if dependencies are missing.

Related Files

[app/audio/audio_player.py](app/audio/audio_player.py)
[app/settings.py](app/settings.py)
[app/game/rhythm_game_engine.py](app/game/rhythm_game_engine.py)
[app/ui/start_screen.py](app/ui/start_screen.py)

Flow

Launch app -> Load settings -> Load notes -> Load audio -> Report or fallback

Notes

The code prefers fallback behavior over crashing for missing peripherals.

TODO

Confirm any user-facing error dialogs in UI components.
