Camera and MediaPipe Errors

Purpose

Summarize camera and tracking failure scenarios.

Confirmed Facts

EXTRACTED: Camera open failures are handled and keyboard fallback remains enabled.
EXTRACTED: MediaPipe import failures disable hand tracking with a console message.
EXTRACTED: Tracking failures for a frame return an empty result.
INFERRED: Camera permission issues can prevent VideoCapture from opening.
INFERRED: Frame delays may reduce tracking stability.

Related Files

[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)

Flow

Open camera -> Capture frame -> Track hand -> Fallback if unavailable

Notes

Tracking failures do not stop the game loop.

TODO

Confirm if any additional error indicators are shown in the UI.
