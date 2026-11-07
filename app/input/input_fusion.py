import time
from dataclasses import dataclass

from app import config
from app.input.emg_reader import SerialEMGReader
from app.input.mediapipe_tracker import MediaPipeHandTracker
from app.input.mock_emg_reader import MockEMGReader


@dataclass
class GameInputState:
    lane: int | None
    emg_value: float
    emg_activated: bool
    hand_visible: bool
    hand_x: float | None
    hand_y: float | None
    finger_count: int | None
    timestamp: float
    tracker_status: str | None = None
    hand_label: str | None = None
    tracker_error: str | None = None


class InputFusion:
    def __init__(
        self,
        use_camera: bool = config.USE_CAMERA,
        use_mock_emg: bool = config.USE_MOCK_EMG,
        emg_threshold: int = config.EMG_THRESHOLD,
        camera_flip: bool = config.CAMERA_FLIP,
    ):
        self.tracker = MediaPipeHandTracker(flip=camera_flip) if use_camera else None
        self.emg_reader = MockEMGReader(emg_threshold) if use_mock_emg else SerialEMGReader(threshold=emg_threshold)
        self.last_camera_frame = None
        self.latest_frame_rgb = None
        self.finger_states = None
        self.hand_landmarks_norm = None
        self.raw_emg_value = 0.0
        self.filtered_emg_value = 0.0
        self.emg_mvc_ratio = 0.0
        self.last_timing_error_ms = None
        self.current_lane = None

    def set_space_pressed(self, pressed: bool):
        if hasattr(self.emg_reader, "set_space_pressed"):
            self.emg_reader.set_space_pressed(pressed)

    def toggle_camera_flip(self) -> bool | None:
        if self.tracker is None or not hasattr(self.tracker, "toggle_flip"):
            return None
        return self.tracker.toggle_flip()

    def set_camera_flip(self, enabled: bool):
        if self.tracker is not None and hasattr(self.tracker, "set_flip"):
            self.tracker.set_flip(enabled)

    def read(self, frame=None) -> tuple[GameInputState, object | None]:
        hand = {"hand_visible": False, "x": None, "y": None, "lane": None, "frame": frame}
        if self.tracker is not None:
            try:
                hand = self.tracker.track(frame)
            except Exception as exc:
                print(f"Input hand tracking failed: {exc}")
        try:
            emg_value, emg_activated = self.emg_reader.read()
        except Exception as exc:
            print(f"EMG input failed: {exc}")
            emg_value, emg_activated = 0.0, False

        state = GameInputState(
            lane=hand.get("lane"),
            emg_value=float(emg_value),
            emg_activated=bool(emg_activated),
            hand_visible=bool(hand.get("hand_visible")),
            hand_x=hand.get("x"),
            hand_y=hand.get("y"),
            finger_count=hand.get("finger_count"),
            timestamp=time.time(),
            tracker_status=getattr(self.tracker, "status", None),
            hand_label=hand.get("hand_label"),
            tracker_error=getattr(self.tracker, "last_error", None),
        )
        self.last_camera_frame = hand.get("frame")
        self.current_lane = state.lane
        self.hand_landmarks_norm = hand.get("landmarks")
        self.finger_states = hand.get("finger_states")
        self.raw_emg_value = float(emg_value)
        self.filtered_emg_value += .18 * (self.raw_emg_value - self.filtered_emg_value)
        self.emg_mvc_ratio = self.filtered_emg_value / max(1, self.emg_reader.threshold)
        self.latest_frame_rgb = None
        if self.last_camera_frame is not None:
            try:
                self.latest_frame_rgb = self.last_camera_frame[:, :, ::-1].copy()
            except (TypeError, IndexError, AttributeError):
                pass
        return state, self.last_camera_frame

    def close(self):
        for target in (self.tracker, self.emg_reader):
            if hasattr(target, "close"):
                target.close()
