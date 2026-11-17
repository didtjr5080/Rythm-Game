# Hand cursor flow

```mermaid
flowchart TD
    MP[Existing MediaPipe video worker] --> VALID{Fresh native hand result?}
    VALID -- No --> RESET[Hide pointer and cancel pending actions]
    VALID -- Yes --> SCOPE{Main, Settings, Result or History active; no modal?}
    SCOPE -- No --> RESET
    SCOPE -- Yes --> OPEN[Open hand arms gesture and moves app-local ring]
    OPEN --> FOLD[Stable fold locks target and starts 450ms wait]
    FOLD --> CLICK[One app-local click after confirmation delay]
    CLICK --> NEXT[Queue navigation after mouse event delivery]
    NEXT --> SHARE[Next page reuses camera session]
    SCOPE --> TWO[Exactly two fingers / native 3D hand landmarks]
    TWO --> NEUTRAL[Hold wrist straight / stable 0.4s reference]
    NEUTRAL --> TILT{Relative palm tilt}
    TILT -->|Back / positive depth tilt| UP[Scroll up]
    TILT -->|Inward / negative depth tilt| DOWN[Scroll down]
    UP --> MODE[Cancel pending click / hold pose to keep scrolling]
    DOWN --> MODE
    MODE --> RELEASE[Neutral wrist or release two-finger pose / stop without clicking]
    RELEASE --> OPEN
    ESC[ESC, focus loss, resize or screen change] --> RESET
```

EXTRACTED: No OS cursor movement or global input injection. Gameplay and calibration are excluded.

EXTRACTED: Uses a camera-relative 3D palm tilt proxy, not an anatomical wrist angle with a tracked forearm. Palm faces camera and forearm stays still. Source: `app/input/hand_gestures.py`, `app/input/mediapipe_tracker.py`, `app/ui/hand_cursor.py`.
