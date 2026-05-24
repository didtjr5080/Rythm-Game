Camera Fallback

Purpose

Explain how the game behaves when the camera or tracking is unavailable.

Confirmed Facts

EXTRACTED: If the camera cannot be opened, the game continues and keyboard lane fallback remains enabled.
EXTRACTED: MediaPipe import failures are handled with a console message and tracking is disabled.
EXTRACTED: Manual lane input is applied when the hand is not visible.

Related Files

[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[README.md](README.md)

Flow

Camera failure -> No hand data -> Manual lane fallback -> Continue gameplay

Notes

The fallback path ensures the UI remains responsive even when computer vision fails.

TODO

Confirm any additional user-facing messaging in UI screens beyond console logs.
