Local Data Layout

Purpose

Explain the local data directories used at runtime.

Confirmed Facts

EXTRACTED: app/data/songs/ stores user-added audio files.
EXTRACTED: app/data/notes/ stores generated note JSON files.
EXTRACTED: app/data/settings.json stores configuration settings.
EXTRACTED: app/data/sessions/ stores session logs as JSON and CSV files.
EXTRACTED: app/data/results/ stores per-play result summaries as JSON files.
EXTRACTED: Result summaries may include references to the session JSON/CSV paths.
EXTRACTED: These runtime data paths are ignored by git in .gitignore.

Related Files

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/analytics/session_logger.py](app/analytics/session_logger.py)
[app/ui/result_screen.py](app/ui/result_screen.py)
[app/settings.py](app/settings.py)
[.gitignore](.gitignore)

Flow

Runtime content -> app/data/* -> Excluded from version control

Notes

Keep runtime data separate from source to avoid accidental commits.

TODO

Confirm if any additional data subfolders are created by analytics modules.
