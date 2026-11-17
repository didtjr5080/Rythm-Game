# EXTRACTED: EMG activity filtering and automatic calibration

EXTRACTED: HUD source `app/ui/game_widget.py` displays the actual activity number, ACTIVE/REST and unchanged ON/OFF; it no longer presents activity divided by ON as MVC percent.

```mermaid
flowchart TD
    RAW[SZH-GJD001 A0 / 500Hz] --> DC[Initial DC centering / same input samples]
    DC --> BP[ESP8266 v2: 60-100Hz bandpass]
    BP --> RMS[20-sample RMS / 40ms]
    RMS -->|filtered field / 50Hz| A
    DC --> NORMS[Bypass bandpass / 20-sample RMS]
    NORMS -->|EMG1_BYPASS / 50Hz| A
    A[USB serial packet] --> B{Signal selection}
    B -->|envelope| C[Firmware filtered activity]
    B -->|unfiltered| UACT[Firmware no-bandpass RMS]
    UACT --> E
    B -->|raw / other sensor ENV| D[Direct A0 activity]
    B -->|ESP8266 v2 raw| DIAG[Diagnostic only / activation disabled]
    C --> E[Validate 0..1023]
    D --> E
    E --> F[Median 3 samples + EMA 0.4]
    F --> G[Rest to arm / threshold activation]
    G --> H[Existing game input]
    F --> I[InputFusion filtered display]
    F --> J[Settings ACTIVITY display]
    F --> K[Fresh samples only]
    K --> L[Rest measurement: settle 0.75s + collect 3s]
    L --> M[User starts guided 3 repetitions]
    K --> N[3 x rest 2s + contraction 2s / discard first 0.5s each]
    M --> N
    N --> O{All intervals contain valid measurement numbers?}
    O -->|yes| P[Apply measured medians to ON and OFF / rising or falling / reset activation]
    O -->|no| Q[Show missing or invalid data / preserve prior values]
    P --> R[User presses Save]
    R --> S[settings.json: ON and OFF]
    S --> GAME[InputFusion reader / game uses both thresholds]
    GAME --> HUD[HUD: activity value + ACTIVE or REST + ON/OFF + UP/DOWN]
    MANUAL[Manual ON or input source change] --> FALLBACK[Clear calibrated OFF / use ON x 0.6]
    T[Signal lost during measurement] --> U[Cancel / restart from rest]
```

EXTRACTED: Sources: `firmware/esp8266_emg/szh_gjd001_filter.h`, `firmware/esp8266_emg/esp8266_emg.ino`, `app/input/emg_processing.py`, `app/input/emg_reader.py`, `app/input/input_fusion.py`, `app/ui/settings_screen.py`. See [usage and limits](../docs/emg-auto-calibration.md) and [SZH-GJD001 firmware](../docs/szh-gjd001-filter.md). The diagram describes the new firmware source; flashing the hardware is a separate step.
