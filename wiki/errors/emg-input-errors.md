EMG Input Errors

Purpose

List EMG-related error conditions and fallbacks.

Confirmed Facts

EXTRACTED: Missing pyserial triggers a fallback to MockEMGReader.
EXTRACTED: Serial port open failures trigger a fallback to MockEMGReader.
EXTRACTED: Serial read errors log a message and return a mock value for the frame.
INFERRED: COM port mismatch or baudrate mismatch prevents real EMG readings.
INFERRED: Malformed serial data can be ignored if no numeric values are parsed.

Related Files

[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

Flow

Open port -> Read line -> Parse value -> Activation -> Fallback on error

Notes

Mock EMG ensures the game remains playable when hardware is absent.

TODO

Confirm if UI exposes any realtime EMG connection status.
