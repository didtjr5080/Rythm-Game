Mock Input

Purpose

Document how to test gameplay without a real EMG sensor or camera.

Confirmed Facts

EXTRACTED: SPACE key toggles mock EMG activation.
EXTRACTED: Mock EMG uses a high value when SPACE is pressed and a low value otherwise.
EXTRACTED: A/S/D or Left/Down/Right provide lane fallback when hand tracking is not visible.
EXTRACTED: Manual lane input is used when the hand is not visible.

Related Files

[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[README.md](README.md)

Flow

Press SPACE -> Mock EMG value -> Activation check
Press A/S/D or Left/Down/Right -> Manual lane -> Lane selection

Notes

Camera-free testing is supported through manual lane input and mock EMG.

TODO

Confirm any additional hotkeys exposed in calibration or settings screens.
