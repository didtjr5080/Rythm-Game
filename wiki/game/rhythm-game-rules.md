Rhythm Game Rules

Purpose

Summarize core gameplay rules for lanes, notes, and hits.

Confirmed Facts

EXTRACTED: The game uses 3 lanes (LEFT, CENTER, RIGHT).
EXTRACTED: Notes are judged when they reach the judgement line timing window.
EXTRACTED: A hit requires EMG activation and the selected lane matching the note lane.
EXTRACTED: Score and combo are shown during gameplay.

Related Files

[app/config.py](app/config.py)
[app/game/judge.py](app/game/judge.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

Flow

Note spawns -> Moves toward judgement line -> EMG + lane match -> Result -> Score update

Notes

The judgement line position is configurable in settings.

TODO

Confirm whether any additional rule variants exist for difficulty modes.
