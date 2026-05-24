Contradictions and Ambiguities

Purpose

Highlight mismatches or uncertain claims so documentation stays aligned with the implemented code.

Confirmed Facts

EXTRACTED: The README instructs setting Serial EMG baudrate to 115200.
EXTRACTED: The SerialEMGReader default baudrate in code is 9600.
AMBIGUOUS: It is unclear whether 9600 or 115200 is the intended default for real sensors in current deployments.
INFERRED: Future clinical analysis features are discussed in ideas but are not implemented in the current codebase.

Related Files

[README.md](README.md)
[app/input/emg_reader.py](app/input/emg_reader.py)

Flow

Requirement (README) -> Implementation (code) -> Document ambiguity -> Avoid changing runtime defaults

Notes

If deployments use a different baudrate, document it as configuration guidance, not a code change.

TODO

Confirm the intended default baudrate for production EMG sensors.
