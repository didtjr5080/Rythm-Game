Settings System

Purpose

Describe configurable gameplay and UI options stored in local settings.

Confirmed Facts

EXTRACTED: Settings are loaded from app/data/settings.json with defaults in app/settings.py.
EXTRACTED: Options include HUD visibility, music volume, judgement text, camera debug, camera flip, note speed, judgement line position, and EMG threshold.
EXTRACTED: Window mode and resolution are stored in settings.

Related Files

[app/settings.py](app/settings.py)
[README.md](README.md)

Flow

Load settings -> Apply to UI and gameplay -> Save updates to app/data/settings.json

Notes

Settings values are clamped to safe ranges when loaded and saved.

TODO

Confirm where settings UI writes updates in the SettingsScreen.
