# Glassmorphism Sonic Lab implementation

Implemented the desktop PyQt6 work order using QPainter and QSS only.

- Shared aurora background (cached), frosted cards, font fallbacks, gauges, 3D crystal notes, spline waveforms and 21-point hand overlays.
- Perspective 3-lane gameplay, lane illumination, crystal trails, hit ripples, DSP history, threshold-relative activation gauge, webcam PIP with lane frames, timing error and score.
- V toggles the 18% AR camera background; F retains camera mirroring; keyboard lane / mock EMG controls remain intact.
- Three-column lobby/song browser, calibration and results. Song selection remains integrated in StartScreen because this repository has no separate song-select screen.
- Calibration reads the existing input fusion, supports SPACE fallback, and persists its threshold through the existing settings store.
- Additive frame / normalized landmark / raw and filtered EMG telemetry. Existing engine, judge, note and score interfaces are unchanged.
- Live lobby bio tracking releases hardware before screen changes. Results display actual metrics and explicitly label the hand preview. Illustrative waveform and unavailable BPM/density are labeled rather than presented as measured data. Actual audio analysis is displayed after Generate Notes during the current application session.

## Verification

Run from the repository root:

```powershell
.venv311/Scripts/python.exe WorkOrder/verify_ui.py
.venv311/Scripts/python.exe -m compileall -q app WorkOrder/verify_ui.py
```

The offscreen check renders all four screens at 1280x720 and checks mock input, threshold persistence (with file writes mocked), PERFECT scoring, timing, ripple creation, V toggle, RGB/PIP/AR drawing and bounded history. Result persistence is mocked to avoid creating a fictitious session. It generates lobby_preview.png, calibration_preview.png, game_preview.png and result_preview.png beside this report.

Measured paint time with synthetic PIP and AR was approximately 10 ms/frame on this machine. This measures painting only; it does not establish end-to-end 60 FPS with real camera capture / MediaPipe inference. Physical webcam and EMG hardware were not exercised. The existing synchronous camera / tracker path may affect frame timing on hardware.

Existing user changes to sensor readers, configuration, packaging and launch scripts were preserved. No executable distribution was rebuilt.


## Real webcam and higher resolutions update

Settings now provides Enable real webcam, Camera 0-9, capture size (640x480 / 1280x720 / 1920x1080), and Connect / Test Camera. Save applies the selected device to the lobby, calibration and gameplay. Windows camera startup tries DirectShow, Media Foundation and the default backend, verifies an actual frame, and reports the negotiated frame dimensions. A webcam can choose a lower capture size than requested. Settings reports connection errors and the live screens show actual frames. Simulated hand geometry is not drawn over live frames when no landmarks were detected.

Window resolution and camera capture size are independent. Choose 1920x1080 or 1440x900 under Settings > Resolution and Save. Gameplay and dashboard instruments preserve their geometry instead of stretching circular gauges or the highway in 16:10 windows. Settings scrolls when its contents exceed the available height. Camera frames retain their aspect ratio, and skeleton coordinates follow the fitted image bounds.

Additional verification:

```powershell
.venv311/Scripts/python.exe WorkOrder/verify_camera_resolution.py
```

Passes: selected camera index, Windows backend fallback, requested vs actual capture dimensions, disabling the camera, resource release, setting persistence, real-frame preview pipeline using synthetic camera input, and five screens at both 1920x1080 and 1440x900. Screenshots are saved alongside this report.

Physical camera 0 was probed in this execution environment but could not be opened by any available backend; three read attempts returned no frame. Therefore physical camera / hand-tracking success is not claimed. OpenCV 4.11.0 and MediaPipe 0.10.21 with the Hands API are installed. To connect on the user's desktop, select the correct device in Settings, close other applications using that camera if necessary, enable Windows camera access for desktop applications, and click Connect / Test Camera.


## Finger recognition fix

Two defects were reproduced in the existing code: the finger count omitted the pinky and used image-axis comparisons that broke under hand rotation; additionally, on this Windows Python 3.11 environment, importing PyQt before MediaPipe caused native `_framework_bindings` initialization to fail. This silently moved the application to its approximate skin-contour fallback.

The application entrypoint now preloads MediaPipe before importing Qt. A real Hands model was successfully initialized and processed a blank frame after the complete app import; it correctly reported no hand. All five fingers now use joint angles and wrist-relative distances, with input aspect correction, independent of handedness / image mirroring. Existing 1/2/3 finger lane assignments remain unchanged; 4/5 fingers use horizontal hand position as before.

Camera test preview now runs the same tracker, displays actual landmarks and the detected finger count / tracker status. Lobby, calibration and gameplay also show finger counts. This separates no camera frame, no detected hand, exact landmark tracking and approximate OpenCV fallback.

Regression commands:

```powershell
.venv311/Scripts/python.exe WorkOrder/verify_tracker_startup.py
.venv311/Scripts/python.exe WorkOrder/verify_fingers.py
.venv311/Scripts/python.exe WorkOrder/verify_camera_resolution.py
```

Passed: real model initialization/inference with Qt; 32 synthetic finger configurations at five rotations, with mirroring and both handedness labels; non-square frame geometry; mirrored landmark alignment; lane mapping and no-hand results; camera preview pipeline and both higher screen resolutions. Synthetic geometry tests validate the counting logic, not real-world detection accuracy. Physical hand/camera recognition remains unverified in this environment because the camera could not be opened. Fully exit and restart through run.bat to apply the new native library import order. Existing packaged EXEs were not rebuilt.


## Follow-up: undercounting palm-facing 3-finger gestures

User reported that palm-facing gestures mostly selected LEFT/CENTER. This is consistent with undercounting, but the user's physical pose was not available for direct diagnosis. The previous code required nearly straight distal joints on every finger, which rejected mildly curved ring fingertips in a constructed regression case. Removed the strict DIP-angle veto, and classify by PIP angle, whole-finger reach and wrist-relative extension. Thumb classification permits a naturally flexed MCP and rejects a straight thumb crossing the palm using the palm's lateral axis.

MediaPipe world hand landmarks are now preferred when present, finite and nondegenerate; aspect-corrected image geometry remains a fallback. Per-finger changes require two consecutive observations, while first acquisition is immediate and tracking loss clears the history. Multiple detected hands are selected by spatial continuity / palm size instead of favoring the first hand whose gesture maps to 1/2/3.

Diagnostics color extended fingers green and folded fingers orange, with T/I/M/R/P for thumb/index/middle/ring/pinky. A binary summary is shown in calibration, lobby, game HUD and camera test; gameplay also shows the selected lane. Existing lane mappings remain 1=LEFT, 2=CENTER, 3=RIGHT, 4/5=horizontal hand position.

The expanded verify_fingers.py passes mildly curved ring => 3 fingers / RIGHT, natural thumb MCP flexion, folded-across-palm thumb, world-coordinate selection, one-frame dropout rejection, deliberate gesture updates, and multi-hand selection, plus the original 32-combination/mirror/rotation tests. Real-model startup, UI smoke tests and both higher resolutions also passed. These are geometry/pipeline regressions; accuracy on the user's physical hand remains to be checked after restarting run.bat.


## Full-song playback fix

Confirmed that game_loop used engine.is_finished(), which returns true when all notes are judged, and immediately called AudioPlayer.stop(). Local song metadata showed an approximately 213.77-second track whose final note was at 202.861 seconds. Audio loading itself did not crop the file; the note-based session end truncated the remaining music.

Selected-song sessions now finish on natural audio completion. The player exposes loading, completion, duration and a clock anchored to actual playback startup; note judgment and painting wait for loading and follow that clock. Sample sessions retain their note-based finish. Playback errors are displayed and retain a bounded chart-based fallback. Stopping while decoding prevents a stale background track from starting afterward. Explicit hit_time_ms timestamps below 1000 now remain milliseconds rather than being multiplied into seconds.

`WorkOrder/verify_full_song.py` passed: full PCM buffer submitted, natural playback completion, judged chart does not truncate a still-playing track, playback-clock use, sample completion, cancellation during decode and sub-second millisecond timestamps. Audio output is mocked; physical speaker playback was not exercised. UI smoke verification and compilation also passed. Existing saved charts need no regeneration for the playback-end fix.


## Windows EXE release build

Built the current implementation with Python 3.11 and PyInstaller 6.21.0 using EMG-Motion-Rhythm.spec. The onedir bundle includes MediaPipe Hands models and the legacy audio analysis / note generation modules, and excludes local songs, settings and session data. A custom runtime hook preloads MediaPipe before the built-in Qt hook. Librosa is collected as source modules and uses a temporary Numba cache so frozen audio analysis works.

The final EXE --self-test passed all checks: actual native MediaPipe Hands model inference with Qt, 1920x1080 and 1440x900 instrument rendering, complete WAV decode, librosa audio analysis, legacy note generation, audio output library import and all desktop screen imports. Camera, serial and speaker hardware were not exercised. Earlier packaging omissions were corrected before the final archive.

build_windows.ps1 reproduces the build, runs the EXE self-test, archives the complete folder and writes a SHA256 checksum. packaging/README-WINDOWS.txt explains extraction, operation and local data paths. The ZIP is intended for GitHub Releases; sources, build configuration, tests and documentation are committed to Git. Historical dist_* directories and generated previews stay local.
