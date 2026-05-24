Audio Note Generation

Purpose

Explain how audio analysis and note generation are handled.

Confirmed Facts

EXTRACTED: Audio analysis calls legacy backend functions when available.
EXTRACTED: Note generation attempts to use legacy backend note_generator first.
EXTRACTED: If legacy generation fails, sample notes are used as a fallback.
EXTRACTED: Notes are simplified to reduce dense hit intervals.
EXTRACTED: legacy_web frontend calls backend endpoints for upload, analyze, and generate-notes.
EXTRACTED: legacy_web backend builds chart data and exports JSON/CSV for generated notes.

Related Files

[app/audio/beat_analyzer.py](app/audio/beat_analyzer.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[README.md](README.md)
[legacy_web/frontend/src/api.js](legacy_web/frontend/src/api.js)
[legacy_web/backend/main.py](legacy_web/backend/main.py)

Flow

Analyze audio -> Generate chart -> Convert to lanes -> Simplify -> Save JSON

Notes

The adapter imports legacy_web/backend modules via sys.path adjustments.

TODO

Confirm which legacy backend functions are required for full note generation.
