Judgement System

Purpose

Document the timing windows and results used for scoring.

Confirmed Facts

EXTRACTED: Judgement results are PERFECT, GOOD, or MISS.
EXTRACTED: PERFECT occurs within the perfect window; GOOD occurs within the judge window.
EXTRACTED: MISS is recorded if the note passes beyond the judge window without a hit.
EXTRACTED: PERFECT awards 1000 points; GOOD awards 500 points; MISS resets combo.

Related Files

[app/game/judge.py](app/game/judge.py)
[app/game/score.py](app/game/score.py)
[app/config.py](app/config.py)

Flow

Input check -> Timing window -> PERFECT/GOOD/MISS -> ScoreState update

Notes

Judgement relies on both timing accuracy and EMG activation with lane match.

TODO

Confirm if any alternate scoring logic exists outside ScoreState.
