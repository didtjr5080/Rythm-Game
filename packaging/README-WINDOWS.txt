EMG Motion Rhythm - Windows x64 portable build

Current build: 2026.11.18.10
Reduced note frequency: pinch/advanced minimum gap 1.8s; EMG rest after hold 1.8s.
Existing charts also use lower density without rewriting files or shifting beats.
Game selection: open hand moves the webcam cursor; close fist once to select a card.
Note speed is 50-200; older settings above 200 are clamped when loaded.
The advanced PINCH + EXTENSION selection card uses the supplied pinch-and-armband image.
Use the player selector / profile manager to create, select or delete a person.
Saved pinch and EMG calibration is reused; new values are measured only when missing.
Advanced mode unlocks only after BOTH basic modes finish normally for that profile.
Manual exit, playback errors and 10 consecutive misses do not grant completion.
Practice without a selected profile does not save calibration or unlock advanced mode.
New advanced mode: PINCH + EXTENSION (4 lanes).
Score only when the matching Leap pinch AND fresh armband extension are present together.
Complete Leap calibration, then 3.0s EMG recording before music begins.
The original Leap-only pinch and armband-only sustained-note modes remain available.
EMG: record 3.0 seconds before play; current value >= minimum means EXTENSION.
Use the actual recorded minimum, with no mean, +0.01 offset or comparison rounding.
Both modes stop immediately at 10 CONSECUTIVE misses; PERFECT or GOOD resets the streak.
EMG rhythm/hold uses sustained notes only (at least 1 second), including old charts.
Leap Motion pinch rhythm (4 lanes) and OYMotion armband EMG rhythm/hold (1 lane).
Webcam hand navigation is used in menus; gameplay uses the selected sensor only.
Generate Notes again after upgrading: source SHA256 is required for cached charts.
Audio analysis/playback errors stop preparation or gameplay without sample substitution.
The remaining instructions below include historical controls from older builds;
use the current game selection and calibration screens for sensor setup.

Extract the entire ZIP to a writable folder and run EMG-Motion-Rhythm.exe.
Keep _internal next to the EXE; copying only the EXE will not work.
No Python installation is required. Music and personal runtime data are not bundled.

Hand navigation (Main, Settings, post-game Results and saved Results):
- Open hand: move green ring. Fold once: click after a short confirmation delay.
- Face the palm toward the camera, keep the forearm still, and extend TWO fingers.
- Hold the wrist straight briefly (HOLD WRIST -> WRIST READY).
- Bend the wrist back for SCROLL UP; bend inward for SCROLL DOWN.
- Return the wrist to neutral or release the two-finger pose to stop. ESC resets.
- No OS mouse movement; other applications, gameplay and calibration screens are excluded.

Settings:
- New-install EMG defaults: Filtered activity (envelope), threshold 12.
- Existing saved settings take priority; check the signal type and threshold when updating.
- Screen resolution: 1920x1080, 1440x900, and other listed sizes.
- Enable real webcam; choose Camera 0-9; Connect / Test Camera; Save.
- Camera frames may negotiate a lower capture size than requested.
- Any combination of 1-5 extended fingers selects lane 1-5; a fist selects none.
- T/I/M/R/P labels identify thumb/index/middle/ring/pinky.
- Green means extended; orange means folded.
- Number keys 1-5 select lanes without tracking; SPACE works only in explicit mock mode.
- Real EMG mode never falls back to keyboard input when disconnected.
- Relax before each contraction; holding one contraction scores at most one note.
- F flips the camera; V toggles the AR camera background.

Add a local MP3/WAV/OGG, load it, and generate notes before playing.
The selected audio plays through to the end before results are shown.
Local settings, songs, generated notes, results and logs are stored under
_internal/app/data in this portable build. Keep the extracted folder writable.

If Windows blocks the camera, enable camera access for desktop apps in Windows
Settings and close other applications that are using the same camera.
This build is unsigned; no code-signing certificate was provided.

Self-test without camera, serial or speakers:
EMG-Motion-Rhythm.exe --self-test self-test.json

Troubleshooting: runtime fault traces are saved to _internal/app/data/logs/
when the extracted folder is writable. Main/Settings share their camera session.
