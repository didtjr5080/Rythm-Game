Saved Music Flow

Purpose

Document how user-added music and notes are stored and loaded.

Confirmed Facts

EXTRACTED: Added songs are copied into app/data/songs/ with a timestamped name.
EXTRACTED: Notes are saved under app/data/notes/ using a _notes.json suffix.
EXTRACTED: When a selected song has saved notes, they are loaded automatically.

Related Files

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[README.md](README.md)

Flow

Add song -> app/data/songs/ -> Generate notes -> app/data/notes/ -> Load Selected -> Start game

Notes

Saved songs and notes are runtime data and should remain excluded from git.

TODO

Confirm how missing note files are surfaced to the user.
