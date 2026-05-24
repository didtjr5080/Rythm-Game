Data Flow

Purpose

Describe the path from music files to notes and gameplay results.

Confirmed Facts

EXTRACTED: Added songs are stored under app/data/songs/.
EXTRACTED: Generated notes are saved under app/data/notes/ with a _notes.json suffix.
EXTRACTED: Saved notes are loaded automatically when a selected song already has notes.
EXTRACTED: Game updates evaluate lane selection and EMG activation for judgement.

Related Files

[app/ui/start_screen.py](app/ui/start_screen.py)
[app/audio/note_generator_adapter.py](app/audio/note_generator_adapter.py)
[app/game/rhythm_game_engine.py](app/game/rhythm_game_engine.py)
[app/game/judge.py](app/game/judge.py)

Flow

Music File
-> app/data/songs/
-> Generate Notes
-> app/data/notes/
-> Load Selected Song
-> Note Spawn
-> Hand Lane Selection
-> EMG Activation
-> Judgement
-> Score / Combo / Result
-> Session Log (app/data/sessions/)
-> Result Summary (app/data/results/)

Notes

Notes are normalized and simplified before gameplay to reduce dense hit windows.

TODO

Confirm any additional data flow for session logs and results output.
