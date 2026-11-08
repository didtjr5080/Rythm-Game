EMG Motion Rhythm - Windows x64 portable build

Extract the entire ZIP to a writable folder and run EMG-Motion-Rhythm.exe.
Keep _internal next to the EXE; copying only the EXE will not work.
No Python installation is required. Music and personal runtime data are not bundled.

Settings:
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
