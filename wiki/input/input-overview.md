Input Overview

Purpose

Summarize how lane selection and EMG activation combine into gameplay input.

Confirmed Facts

EXTRACTED: Hand tracking provides lane selection when the camera is available.
EXTRACTED: EMG activation is read each frame and combined with the lane state.
EXTRACTED: SPACE activates mock EMG input for testing.
EXTRACTED: Keyboard lane fallback supports A/S/D and Left/Down/Right keys.
EXTRACTED: If hand tracking fails but a manual lane is set, manual lane selection is used.

Related Files

[app/input/input_fusion.py](app/input/input_fusion.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[README.md](README.md)

Flow

Camera frame -> MediaPipe tracking -> Lane selection
Keyboard lane input -> Manual lane override
EMG reader -> Activation
Lane + Activation -> GameInputState

Notes

Manual lane input allows gameplay testing even when camera tracking is unavailable.

TODO

Confirm behavior when both manual input and hand tracking are present simultaneously.
