Input Flow Diagram

```mermaid
graph TD
    A[Camera Frame] --> B[MediaPipe Hand Tracking]
    B --> C[Finger Count Lane]
    C --> D[Lane Selection]
    E[Keyboard Lane Fallback] --> D
    P[Settings: auto or chosen USB identity] --> Q[Discover and reconnect serial device]
    Q --> R[Verify firmware and parse framed samples]
    R --> F[EMG Reader: raw or filtered]
    F --> G[EMG Value]
    Q --> S[Disconnected: clear activation]
    S --> Q
    G --> H{Threshold}
    H --> I[Activation]
    D --> J[InputFusion State]
    I --> J
```
