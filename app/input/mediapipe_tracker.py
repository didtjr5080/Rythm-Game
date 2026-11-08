from app import config

_mediapipe = None
_mediapipe_error = None


def preload_mediapipe():
    """Load MediaPipe before PyQt on Windows to avoid native DLL conflicts."""
    global _mediapipe, _mediapipe_error
    if not config.USE_MEDIAPIPE:
        return None
    if _mediapipe is None and _mediapipe_error is None:
        try:
            from app.input.mediapipe_runtime import prepare_native_runtime
            prepare_native_runtime()
            import mediapipe
            _mediapipe = mediapipe
        except Exception as exc:
            _mediapipe_error = f'{type(exc).__name__}: {exc}'
    return _mediapipe


class MediaPipeHandTracker:
    def __init__(self, flip: bool = config.CAMERA_FLIP):
        self.flip = flip
        self.available = False
        self.hands = None
        self.status = "starting"
        self.last_error = None
        self.initialization_error = None
        self.model_root = None
        self._selected_hand = None
        self._stable_fingers = None
        self._pending_fingers = None
        if not config.USE_MEDIAPIPE:
            self.status = "opencv only"
            return
        try:
            mp = preload_mediapipe()
            if mp is None:
                raise ImportError(_mediapipe_error or 'MediaPipe is disabled')

            self.mp_hands = mp.solutions.hands
            from app.input.mediapipe_runtime import create_hands
            self.hands, self.model_root = create_hands(mp,
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=config.HAND_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.HAND_TRACKING_CONFIDENCE,
            )
            self.available = True
            self.status = f"ready mp {getattr(mp, '__version__', '-')}"
        except ImportError as exc:
            self.status = "missing"
            self.last_error = f"{type(exc).__name__}: {exc}"
            self.initialization_error = self.last_error
            print(f"MediaPipe import failed: {self.last_error}")
        except Exception as exc:
            self.status = "error"
            self.last_error = str(exc)
            self.initialization_error = f"{type(exc).__name__}: {exc}"
            print(f"MediaPipe hand tracker could not start: {exc}")

    @property
    def backend_is_mediapipe(self):
        return self.available and not self.status.startswith('opencv') and self.status != 'error'

    @property
    def diagnostic_summary(self):
        if self.backend_is_mediapipe:
            return 'MEDIAPIPE READY / ' + self.status
        return 'MEDIAPIPE INACTIVE / ' + (self.initialization_error or self.last_error or 'disabled') + ' / APPROXIMATE OPENCV FALLBACK'

    def track(self, frame):
        if frame is None:
            self._reset_finger_history()
            if self.available: self.status = "no camera frame"
            return self._empty_result(frame)
        if not self.available or self.hands is None:
            return self._track_with_opencv(frame)
        try:
            import cv2

            display_frame = cv2.flip(frame, 1) if self.flip else frame
            result, detected_frame, x_mirror = self._process_candidates(cv2, frame, display_frame)
            if result is None or not result.multi_hand_landmarks:
                self.status = "no hand"
                self._reset_finger_history()
                return self._empty_result(display_frame)

            self.last_error = None
            self.status = "tracking"
            candidates = []
            handedness_list = result.multi_handedness or []
            for index, hand_landmarks in enumerate(result.multi_hand_landmarks):
                landmarks = hand_landmarks.landmark
                hand_x = sum(point.x for point in landmarks) / len(landmarks)
                if x_mirror:
                    hand_x = 1.0 - hand_x
                hand_y = sum(point.y for point in landmarks) / len(landmarks)
                hand_label = self._hand_label(handedness_list, index)
                if x_mirror:
                    hand_label = self._mirrored_label(hand_label)
                from types import SimpleNamespace
                aspect = detected_frame.shape[1] / detected_frame.shape[0]
                geometry = [SimpleNamespace(x=p.x*aspect, y=p.y, z=p.z*aspect) for p in landmarks]
                world_hands = getattr(result, 'multi_hand_world_landmarks', None)
                if world_hands and index < len(world_hands):
                    world = world_hands[index].landmark
                    import math
                    if len(world) == 21 and all(math.isfinite(float(v)) for p in world for v in (p.x,p.y,p.z)):
                        if math.dist((world[0].x,world[0].y,world[0].z),(world[9].x,world[9].y,world[9].z)) > 1e-6:
                            geometry = world
                finger_states = self.finger_states(geometry)
                finger_count = sum(finger_states.values())
                lane = self.finger_count_to_lane(finger_count)
                candidates.append(
                    {
                        "hand_visible": True,
                        "x": hand_x,
                        "y": hand_y,
                        "lane": lane,
                        "finger_count": finger_count,
                        "finger_states": finger_states,
                        "raw_finger_states": dict(finger_states),
                        "palm_size": (landmarks[5].x-landmarks[17].x)**2+(landmarks[5].y-landmarks[17].y)**2,
                        "hand_label": hand_label,
                        "frame": detected_frame,
                        "landmarks": [(1.0-point.x if x_mirror else point.x, point.y) for point in landmarks],
                    }
                )

            # Select the same spatial hand, never the first hand with a 1/2/3 gesture.
            # Gesture-based selection could jump to another hand and favor LEFT/CENTER.
            previous = getattr(self, '_selected_hand', None)
            chosen = max(candidates, key=lambda item: item['palm_size'])
            if previous is not None:
                nearest = min(candidates, key=lambda item: (item['x']-previous[0])**2+(item['y']-previous[1])**2)
                if (nearest['x']-previous[0])**2+(nearest['y']-previous[1])**2 < .25**2:
                    chosen = nearest
                else:
                    self._reset_finger_history()
            self._selected_hand = (chosen['x'], chosen['y'])
            chosen['finger_states'] = self._stabilize_fingers(chosen['raw_finger_states'])
            chosen['finger_count'] = sum(chosen['finger_states'].values())
            chosen['lane'] = self.finger_count_to_lane(chosen['finger_count'])
            return chosen
        except Exception as exc:
            self.status = "error"
            self.last_error = str(exc)
            print(f"Hand tracking failed for this frame: {exc}")
            return self._track_with_opencv(frame)

    def _track_with_opencv(self, frame):
        try:
            import cv2
            import numpy as np

            display_frame = cv2.flip(frame, 1) if self.flip else frame
            height, width = display_frame.shape[:2]
            blurred = cv2.GaussianBlur(display_frame, (7, 7), 0)

            ycrcb = cv2.cvtColor(blurred, cv2.COLOR_BGR2YCrCb)
            skin_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))

            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            skin_hsv = cv2.inRange(hsv, np.array([0, 25, 35]), np.array([25, 255, 255]))
            mask = cv2.bitwise_and(skin_ycrcb, skin_hsv)

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            candidates = []
            min_area = max(1200, int(width * height * 0.002))
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                if h < height * 0.08 or w < width * 0.025:
                    continue
                moments = cv2.moments(contour)
                if moments["m00"] == 0:
                    continue
                cx = moments["m10"] / moments["m00"]
                cy = moments["m01"] / moments["m00"]
                # Prefer hand-like blobs away from the face/body center.
                score = area * (1.0 + abs((cx / width) - 0.5))
                if y < height * 0.8:
                    score *= 1.2
                candidates.append((score, contour, cx, cy))

            if not candidates:
                self.status = "opencv no hand"
                return self._empty_result(display_frame)

            _, contour, cx, cy = max(candidates, key=lambda item: item[0])
            hand_x = max(0.0, min(1.0, cx / width))
            hand_y = max(0.0, min(1.0, cy / height))
            finger_count = self._estimate_fingers_from_contour(cv2, contour)
            lane = self.finger_count_to_lane(finger_count)

            self.status = "opencv fallback"
            return {
                "hand_visible": True,
                "x": hand_x,
                "y": hand_y,
                "lane": lane,
                "finger_count": finger_count,
                "hand_label": "opencv",
                "frame": display_frame,
            }
        except Exception as exc:
            self.status = "opencv error"
            self.last_error = str(exc)
            print(f"OpenCV hand fallback failed: {exc}")
            return self._empty_result(frame)

    def _process_candidates(self, cv2, frame, display_frame):
        candidates = [(display_frame, False)]
        if self.flip:
            candidates.append((frame, True))
        else:
            candidates.append((cv2.flip(frame, 1), True))

        for candidate_frame, x_mirror in candidates:
            result = self._process_frame(cv2, candidate_frame)
            if result.multi_hand_landmarks:
                return result, display_frame, x_mirror

            enhanced_frame = self._enhance_frame(cv2, candidate_frame)
            result = self._process_frame(cv2, enhanced_frame)
            if result.multi_hand_landmarks:
                return result, display_frame, x_mirror

        return None, display_frame, False

    def _process_frame(self, cv2, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        return self.hands.process(rgb)

    @staticmethod
    def _enhance_frame(cv2, frame):
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(l_channel)
        enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    @staticmethod
    def _estimate_fingers_from_contour(cv2, contour) -> int | None:
        silhouette_count = MediaPipeHandTracker._estimate_fingers_from_silhouette(cv2, contour)
        hull_indices = cv2.convexHull(contour, returnPoints=False)
        if hull_indices is None or len(hull_indices) < 4:
            return silhouette_count
        defects = cv2.convexityDefects(contour, hull_indices)
        if defects is None:
            x, y, w, h = cv2.boundingRect(contour)
            defect_count = 1 if h > w * 1.35 else None
            return MediaPipeHandTracker._max_count(defect_count, silhouette_count)

        x, y, w, h = cv2.boundingRect(contour)
        scale = max(w, h)
        gaps = 0
        for defect in defects[:, 0]:
            start_index, end_index, far_index, depth = defect
            start = contour[start_index][0]
            end = contour[end_index][0]
            far = contour[far_index][0]

            a = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
            b = ((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2) ** 0.5
            c = ((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2) ** 0.5
            if b == 0 or c == 0:
                continue

            cross = abs((start[0] - far[0]) * (end[1] - far[1]) - (end[0] - far[0]) * (start[1] - far[1]))
            dot = (start[0] - far[0]) * (end[0] - far[0]) + (start[1] - far[1]) * (end[1] - far[1])
            angle = cv2.fastAtan2(float(cross), float(dot))
            if angle < 90 and depth / 256.0 > scale * 0.035 and a > scale * 0.12:
                gaps += 1

        if gaps == 0:
            defect_count = 1 if h > w * 1.15 else None
        else:
            defect_count = min(5, gaps + 1)
        return MediaPipeHandTracker._max_count(defect_count, silhouette_count)

    @staticmethod
    def _estimate_fingers_from_silhouette(cv2, contour) -> int | None:
        try:
            import numpy as np

            x, y, w, h = cv2.boundingRect(contour)
            if w < 8 or h < 8:
                return None

            shifted = contour.copy()
            shifted[:, 0, 0] -= x
            shifted[:, 0, 1] -= y
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask, [shifted], -1, 255, thickness=-1)

            upper_limit = int(h * 0.62)
            top_rows = np.full(w, h, dtype=np.int32)
            for column in range(w):
                rows = np.flatnonzero(mask[:upper_limit, column])
                if rows.size:
                    top_rows[column] = int(rows[0])

            active = top_rows < int(h * 0.55)
            groups = []
            start = None
            for index, is_active in enumerate(active):
                if is_active and start is None:
                    start = index
                elif not is_active and start is not None:
                    groups.append((start, index - 1))
                    start = None
            if start is not None:
                groups.append((start, w - 1))

            min_width = max(5, int(w * 0.055))
            candidate_count = 0
            for start, end in groups:
                group_width = end - start + 1
                if group_width < min_width:
                    continue
                top = int(top_rows[start : end + 1].min())
                base = int(np.percentile(top_rows[start : end + 1], 85))
                if base - top < h * 0.06 and top > h * 0.2:
                    continue
                candidate_count += 1

            if candidate_count == 0:
                return None
            return min(5, candidate_count)
        except Exception:
            return None

    @staticmethod
    def _max_count(*counts: int | None) -> int | None:
        valid_counts = [count for count in counts if count is not None]
        if not valid_counts:
            return None
        return max(valid_counts)

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
    def _mirrored_label(hand_label: str | None) -> str | None:
        if hand_label == "Left":
            return "Right"
        if hand_label == "Right":
            return "Left"
        return hand_label

    def _reset_finger_history(self):
        self._selected_hand = None
        self._stable_fingers = None
        self._pending_fingers = None

    def _stabilize_fingers(self, states):
        # Two consecutive observations per finger suppress single-frame dropouts.
        # First detection is immediate and loss of tracking clears the history.
        if getattr(self, '_stable_fingers', None) is None:
            self._stable_fingers = dict(states)
        else:
            previous = self._pending_fingers or {}
            for name, extended in states.items():
                if previous.get(name) == extended:
                    self._stable_fingers[name] = extended
        self._pending_fingers = dict(states)
        return dict(self._stable_fingers)

    @staticmethod
    def finger_states(landmarks):
        """Classify all five fingers in hand-relative geometry, independent of mirroring.

        Joint angles and wrist distances use aspect-corrected coordinates
        supplied by track(); the public count helper also accepts square input.
        """
        import math

        def point(index):
            value = landmarks[index]
            return (float(value.x), float(value.y), float(getattr(value, 'z', 0.0)))

        points = [point(i) for i in range(21)]
        def distance(a, b):
            return math.dist(points[a], points[b])

        def angle(a, b, c):
            u = [points[a][i]-points[b][i] for i in range(3)]
            v = [points[c][i]-points[b][i] for i in range(3)]
            lengths = math.sqrt(sum(x*x for x in u)*sum(x*x for x in v))
            if lengths < 1e-10:
                return 0.0
            cosine = max(-1.0, min(1.0, sum(x*y for x,y in zip(u,v))/lengths))
            return math.degrees(math.acos(cosine))

        scale = max(distance(0, 9), distance(5, 17), 1e-6)
        states = {}
        # Thumb MCP naturally bends when abducted. Requiring it to be almost
        # straight excluded normal open palms. Check distal reach and which side
        # of the index knuckle the tip lies on, using the palm's own lateral axis.
        palm_width = max(distance(5, 17), 1e-6)
        outward = sum((points[4][i]-points[5][i])*(points[5][i]-points[17][i]) for i in range(3))/palm_width
        thumb_length = distance(2, 3)+distance(3, 4)
        states['thumb'] = (
            angle(2, 3, 4) >= 135
            and distance(2, 4)/max(thumb_length, 1e-6) >= .8
            and outward > palm_width*.12
            and distance(4, 5) > distance(3, 5)+scale*.03
        )
        for name, mcp, pip, dip, tip in (
            ('index', 5, 6, 7, 8), ('middle', 9, 10, 11, 12),
            ('ring', 13, 14, 15, 16), ('pinky', 17, 18, 19, 20),
        ):
            length = distance(mcp, pip)+distance(pip, dip)+distance(dip, tip)
            # A slightly curved fingertip is still extended. Count whole-finger
            # reach instead of vetoing it solely because DIP is below 145 deg.
            states[name] = (
                angle(mcp, pip, dip) >= 135
                and distance(mcp, tip)/max(length, 1e-6) >= .72
                and distance(0, tip) > distance(0, pip)+scale*.08
            )
        return states

    @staticmethod
    def count_lane_fingers(landmarks, hand_label: str | None = None) -> int:
        # Keep the existing public entrypoint; handedness is unnecessary here.
        return sum(MediaPipeHandTracker.finger_states(landmarks).values())

    @staticmethod
    def finger_count_to_lane(count: int | None):
        return count - 1 if count is not None and 1 <= count <= 5 else None

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
