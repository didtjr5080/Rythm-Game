from app import config


class MediaPipeHandTracker:
    def __init__(self, flip: bool = config.CAMERA_FLIP):
        self.flip = flip
        self.available = False
        self.hands = None
        try:
            import mediapipe as mp

            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.available = True
        except ImportError:
            print("MediaPipe is not installed. Hand tracking is disabled.")
        except Exception as exc:
            print(f"MediaPipe hand tracker could not start: {exc}")

    def track(self, frame):
        if frame is None or not self.available or self.hands is None:
            return self._empty_result(frame)
        try:
            import cv2

            display_frame = cv2.flip(frame, 1) if self.flip else frame
            rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb)
            if not result.multi_hand_landmarks:
                return self._empty_result(display_frame)

            candidates = []
            handedness_list = result.multi_handedness or []
            for index, hand_landmarks in enumerate(result.multi_hand_landmarks):
                landmarks = hand_landmarks.landmark
                hand_x = sum(point.x for point in landmarks) / len(landmarks)
                hand_y = sum(point.y for point in landmarks) / len(landmarks)
                hand_label = self._hand_label(handedness_list, index)
                finger_count = self.count_lane_fingers(landmarks, hand_label)
                lane = self.finger_count_to_lane(finger_count)
                candidates.append(
                    {
                        "hand_visible": True,
                        "x": hand_x,
                        "y": hand_y,
                        "lane": lane,
                        "finger_count": finger_count,
                        "hand_label": hand_label,
                        "frame": display_frame,
                    }
                )

            for candidate in candidates:
                if candidate["lane"] is not None:
                    return candidate

            fallback = candidates[0]
            fallback["lane"] = self.x_to_lane(fallback["x"])
            return fallback
        except Exception as exc:
            print(f"Hand tracking failed for this frame: {exc}")
            return self._empty_result(frame)

    @staticmethod
    def _empty_result(frame):
        return {
            "hand_visible": False,
            "x": None,
            "y": None,
            "lane": None,
            "finger_count": None,
            "hand_label": None,
            "frame": frame,
        }

    @staticmethod
    def _hand_label(handedness_list, index: int) -> str | None:
        try:
            return handedness_list[index].classification[0].label
        except Exception:
            return None

    @staticmethod
    def count_lane_fingers(landmarks, hand_label: str | None = None) -> int:
        tips = (8, 12, 16)
        pips = (6, 10, 14)
        count = 0
        for tip_index, pip_index in zip(tips, pips):
            if landmarks[tip_index].y < landmarks[pip_index].y - 0.025:
                count += 1
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        if hand_label == "Left":
            thumb_open = thumb_tip.x > thumb_ip.x + 0.025 and thumb_tip.x > thumb_mcp.x + 0.025
        elif hand_label == "Right":
            thumb_open = thumb_tip.x < thumb_ip.x - 0.025 and thumb_tip.x < thumb_mcp.x - 0.025
        else:
            thumb_open = abs(thumb_tip.x - thumb_mcp.x) > 0.065
        if thumb_open:
            count += 1
        return count

    @staticmethod
    def finger_count_to_lane(count: int | None):
        if count == 1:
            return 0
        if count == 2:
            return 1
        if count == 3:
            return 2
        return None

    def set_flip(self, enabled: bool):
        self.flip = enabled

    def toggle_flip(self) -> bool:
        self.flip = not self.flip
        return self.flip

    @staticmethod
    def x_to_lane(x: float | None):
        if x is None:
            return None
        if x < 0.33:
            return 0
        if x < 0.66:
            return 1
        return 2

    def close(self):
        try:
            if self.hands is not None:
                self.hands.close()
        except Exception:
            pass
