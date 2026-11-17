EMG Motion Rhythm - Current Windows build (2026.11.17.11)

Extract the entire ZIP and run EMG-Motion-Rhythm-No-Bandpass.exe.
Keep _internal next to the EXE. Run one EMG app at a time (COM3 is exclusive).

Hand navigation: open hand to move the pointer, fist to click.
Face the palm toward the camera and keep the forearm still. Extend TWO fingers.
Hold the wrist straight briefly (HOLD WRIST -> WRIST READY), then bend the wrist
back to scroll UP or inward to scroll DOWN. Hold the tilt to keep scrolling.
Return the wrist to neutral or release the two-finger pose to stop; ESC resets.
This uses the palm's 3D tilt relative to its initial pose, not a forearm joint angle.
Double fist no longer toggles scroll mode. Gameplay hand lane input is unchanged.

This build defaults to NO BANDPASS / DC removed RMS (comparison).
Only the 60-100 Hz bandpass is bypassed. The 500 Hz ADC sampling, initial
DC centering, 40 ms RMS, PC median/EMA and ON/OFF detection remain shared.
It is not an entirely unprocessed ADC input mode.

The comparison firmware sends both BP RMS and NO BP RMS from the same input.
In Settings, Connect / Test EMG and check both values.
Choose a signal type and measure rest (about 4 seconds).
Then follow the screen for 3 repetitions: relax 2 seconds, contract 2 seconds
(about 12 seconds total). Do not hold one contraction for the full sequence.
Calibration directly maps measured rest/contraction medians to ON/OFF, without
rejecting noise, a small gap, overlap, equality or a decrease during contraction.
DIR UP/DOWN indicates the measured activation direction. Empty or invalid data
still cannot be calibrated. Equal signals do not contain a way to distinguish actions.
Decimal ON/OFF values are preserved in settings and gameplay. Press Save.
The game HUD shows the actual EMG activity number, ACTIVE/REST, ON/OFF and
UP/DOWN. The old activity/ON percentage labelled MVC ACTIVE has been removed;
ON is an activation threshold, not a measured maximum contraction.
Switching the signal type clears the previous calibration: recalibrate each mode.
Use the P95/P10/gap and rest/contraction response to compare; a larger value
alone does not mean a cleaner signal. Keep electrodes and movement consistent.

The original filtered build remains separate. Existing EMG1 packets are unchanged.
The new EMG1_BYPASS extension requires the comparison firmware on the ESP8266.
No Python installation is needed to run this EXE.
