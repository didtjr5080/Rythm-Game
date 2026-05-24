EMG Threshold

Purpose

Describe how EMG threshold impacts activation and gameplay.

Confirmed Facts

EXTRACTED: EMG threshold is configurable via settings and defaults to 400.
EXTRACTED: EMG activation is true when the current value is greater than or equal to the threshold.

Related Files

[app/config.py](app/config.py)
[app/settings.py](app/settings.py)
[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

Flow

EMG value -> Compare to threshold -> Activation flag -> Judgement

Notes

INFERRED: Too low a threshold can cause accidental hits; too high a threshold can cause missed hits.
INFERRED: Future rehabilitation workflows may require baseline calibration per user session.

TODO

Confirm if calibration UI exposes a threshold test mode.
