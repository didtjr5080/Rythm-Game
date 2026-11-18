"""Pinch classifier from Orion_4_1_Pinch_Lab_Fix_v3 (90ms stability)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

Vec3 = Tuple[float, float, float]
NAMES = ("INDEX", "MIDDLE", "RING", "PINKY")
DEFAULT_RATIO = 0.36   # 실험 시작용 휴리스틱: 손바닥 너비의 36%, 임상 기준 아님
STABLE_SEC = 0.09      # 동작 확정까지 약 90ms
RELEASE_FACTOR = 1.28  # 히스테리시스 해제 임계값 배율
MIN_GAP_RATIO = 0.065  # 2번째 후보와의 최소 거리 차이(손바닥 너비 기준)


def distance(a: Vec3, b: Vec3) -> float:
    return math.dist(a, b)


def clamp(v: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, v))


def bend_angle(chain: List[Vec3]) -> float:
    """MCP-PIP-DIP 관절을 사용해 굽힘각 계산. 직선은 약 0도."""
    if len(chain) < 3:
        return 0.0
    a, b, c = chain[:3]
    u = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    v = (c[0]-b[0], c[1]-b[1], c[2]-b[2])
    nu, nv = math.sqrt(sum(x*x for x in u)), math.sqrt(sum(x*x for x in v))
    if nu < 1e-6 or nv < 1e-6:
        return 0.0
    cos_value = clamp(sum(x*y for x,y in zip(u, v)) / (nu*nv), -1.0, 1.0)
    return 180.0 - math.degrees(math.acos(cos_value))


@dataclass
class HandSample:
    frame_id: int
    t: float
    hand_id: int
    side: str
    palm: Vec3
    palm_width: float
    tips: List[Vec3]              # 엄지, 검지, 중지, 약지, 소지 순서
    bones: List[List[Tuple[Vec3, Vec3]]]  # 5손가락 x 4뼈
    chains: List[List[Vec3]]
    confidence: float = 1.0
    sdk_pinch: float = 0.0
    fps: float = 0.0


def features(sample: HandSample):
    """엄지-4손가락 끝 3D 거리(mm), 손 크기 정규화 거리, 굽힘각."""
    if sample.palm_width <= 20.0 or not all(math.isfinite(v) for p in sample.tips for v in p):
        raise ValueError("유효하지 않은 손 크기 또는 관절 좌표")
    mm = [distance(sample.tips[0], sample.tips[i]) for i in range(1, 5)]
    ratio = [d / sample.palm_width for d in mm]
    bends = [bend_angle(sample.chains[i]) for i in range(1, 5)]
    return mm, ratio, bends


class PinchClassifier:
    """정규화 3D 거리 + 후보 분리 + 유지시간 + 해제 히스테리시스."""
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = {name: DEFAULT_RATIO for name in NAMES}
        if thresholds:
            self.thresholds.update({k: float(v) for k,v in thresholds.items() if k in NAMES})
        self.active = "NONE"
        self.pending = "NONE"
        self.pending_t = 0.0
        self.last_hand_id = None
        self.last_t = None

    def reset(self):
        self.active, self.pending = "NONE", "NONE"
        self.last_hand_id, self.last_t = None, None

    def step(self, sample: Optional[HandSample]) -> Tuple[str, str, str]:
        """결과, 아직 미확정된 1프레임 후보, 사유."""
        if sample is None:
            self.reset()
            return "LOST", "NONE", "추적 손실"
        if self.last_hand_id != sample.hand_id or (self.last_t is not None and sample.t-self.last_t > 0.25):
            self.reset()
        self.last_hand_id, self.last_t = sample.hand_id, sample.t
        try:
            _, r, bends = features(sample)
        except ValueError:
            self.reset()
            return "LOST", "NONE", "잘못된 관절 좌표"

        # 손가락 굽힘각은 모니터링·동점 보조 점수로 사용하며,
        # 재활 환자에게 불리할 수 있는 강제 굽힘 하한은 두지 않음.
        scores = [(r[i] / max(self.thresholds[n], 0.01), i) for i,n in enumerate(NAMES)]
        best_ratio, best_i = min(scores)
        best_name = NAMES[best_i]
        second_ratio = sorted(r)[1]
        # 실제 거리의 차이: 경쟁 손가락과 충분히 구별 가능한지 검사
        distinguishable = (second_ratio - r[best_i] >= MIN_GAP_RATIO)
        candidate = best_name if best_ratio <= 1.0 and distinguishable else "NONE"

        direct_switch = self.active != "NONE" and candidate not in ("NONE", self.active)
        if self.active != "NONE" and candidate == "NONE":
            i = NAMES.index(self.active)
            if r[i] <= self.thresholds[self.active] * RELEASE_FACTOR:
                # Only retain an ambiguous pinch; a clear new finger takes priority.
                candidate = self.active

        if candidate != self.pending:
            self.pending = candidate
            self.pending_t = sample.t
        if direct_switch or (candidate != self.active and sample.t-self.pending_t >= STABLE_SEC):
            self.active = candidate
        reason = "접촉 후보가 불분명" if candidate == "NONE" else f"굽힘각 {bends[NAMES.index(candidate)]:.1f}도"
        return self.active, candidate, reason
