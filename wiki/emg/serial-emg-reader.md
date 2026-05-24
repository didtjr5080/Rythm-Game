Serial EMG Reader

Purpose

Explain the serial EMG reader behavior and fallback logic.

Confirmed Facts

EXTRACTED: SerialEMGReader defaults to COM3 with baudrate 9600.
EXTRACTED: The reader attempts to open a pyserial Serial connection with a short timeout.
EXTRACTED: If pyserial is missing or the port fails, it falls back to MockEMGReader.
EXTRACTED: Incoming lines are parsed for a numeric value, including formats like filtered: 123.
EXTRACTED: The reader returns a numeric value and an activation flag based on threshold.

Related Files

[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

Flow

Open serial -> Read line -> Extract numeric value -> Compare to threshold -> Activation
If serial fails -> Use mock reader

Notes

The README suggests a different baudrate for real sensors; see contradictions.

TODO

Confirm the intended default baudrate for the production EMG device.
