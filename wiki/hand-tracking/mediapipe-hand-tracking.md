MediaPipe Hand Tracking

Purpose

Describe how MediaPipe tracking maps hand data to gameplay lanes.

Confirmed Facts

EXTRACTED: MediaPipe is used to detect hands and landmarks when available.
EXTRACTED: The tracker counts fingers to select lanes (1, 2, 3 fingers -> lanes 0, 1, 2).
EXTRACTED: If finger count does not map to a lane, x position is used as a fallback.
EXTRACTED: Camera flip is supported to mirror the input view.
EXTRACTED: Tracking failures return an empty result without crashing the app.

Related Files

[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

Flow

Camera frame -> MediaPipe Hands -> Landmarks -> Finger count -> Lane
If lane missing -> x position -> Lane fallback

Notes

When MediaPipe is not installed, tracking is disabled and the app continues running.

TODO

Confirm whether hand label data is used anywhere outside tracking.
