# -*- coding: utf-8 -*-
"""Orion 4.1 LeapC.h 기준 ctypes 브리지 (추가 카메라·Gemini CFFI 불필요).

중요: SDK 자체의 LeapC.h를 검사한 뒤 지원 구조에서만 포인터를 읽는다.
"""
from __future__ import annotations

import ctypes as C
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Dict

from app.input.pinch_classifier import HandSample

DEFAULT_SDK = (Path(sys._MEIPASS) / "LeapSDK" if getattr(sys, "frozen", False)
               else Path(r"C:\EMG-Motion-Rhythm\LeapSDK"))
SDK = Path(os.environ.get("LEAPSDK_INSTALL_LOCATION", str(DEFAULT_SDK)))


def _clean(source: str) -> str:
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", source, flags=re.S)


def _block(src: str, name: str) -> str:
    match = re.search(
        r"\btypedef\s+struct\s+_?" + re.escape(name)
        + r"\s*\{(.*?)\}\s*" + re.escape(name) + r"\s*;",
        src, flags=re.S,
    )
    if match is None:
        raise RuntimeError("LeapC.h에서 구조체를 확인할 수 없습니다: " + name)
    return match.group(1)


def event_values(src: str) -> Dict[str, int]:
    match = re.search(r"\benum\s+_?eLeapEventType\s*\{(.*?)\}", src, re.S)
    if not match:
        raise RuntimeError("LeapC.h에서 eLeapEventType 열거형을 찾지 못했습니다.")
    parsed = {}
    current = -1
    for piece in match.group(1).split(","):
        entry = piece.strip().split("=", 1)
        key = entry[0].strip()
        if not key.startswith("eLeapEventType_"):
            continue
        if len(entry) == 2:
            token = entry[1].strip().replace("UL", "").replace("U", "").replace("L", "")
            try:
                current = int(token, 0)
            except ValueError as exc:
                raise RuntimeError("지원하지 않는 이벤트 상수: " + entry[1]) from exc
        else:
            current += 1
        parsed[key] = current
    for key in ("eLeapEventType_Tracking", "eLeapEventType_Connection"):
        if key not in parsed:
            raise RuntimeError("LeapC.h 이벤트 상수 누락: " + key)
    return parsed


def make_abi(header: str):
    """SDK 헤더에 맞춰 데이터 구조 정의. 모르는 배치에서는 실행 중지."""
    src = _clean(header)
    hb = _block(src, "LEAP_HAND")
    pb = _block(src, "LEAP_PALM")
    db = _block(src, "LEAP_DIGIT")
    bb = _block(src, "LEAP_BONE")
    tb = _block(src, "LEAP_TRACKING_EVENT")
    mb = _block(src, "LEAP_CONNECTION_MESSAGE")
    fb = _block(src, "LEAP_FRAME_HEADER")
    if not all((
        re.search(r"\bLEAP_PALM\s+palm\s*;", hb),
        re.search(r"\bLEAP_BONE\s+arm\s*;", hb),
        re.search(r"\bLEAP_DIGIT\s+digits\s*\[\s*5\s*\]", hb),
        re.search(r"\bLEAP_QUATERNION\s+rotation\s*;", bb),
        re.search(r"\bLEAP_DIGIT\s+", hb),
        re.search(r"\bLEAP_HAND\s*\*\s*pHands\s*;", tb),
        re.search(r"\buint32_t\s+nHands\s*;", tb),
        re.search(r"\buint32_t\s+size\s*;", mb),
        re.search(r"\beLeapEventType\s+type\s*;", mb),
    )):
        raise RuntimeError(
            "현재 SDK의 구조체 배치가 이 Orion 어댑터와 다릅니다. "
            "SDK/include/LeapC.h의 LEAP_HAND/LEAP_BONE 정의를 확인해야 합니다. "
            "지원하지 않는 구조를 강제로 읽지 않습니다."
        )
    if "LEAP_MATRIX" in bb:
        raise RuntimeError("구형 basis 행렬 구조는 지원하지 않습니다(안전 중단).")

    # Orion 4.1의 추적 이벤트는 5개 필드만 존재한다.
    # 이전 코드에는 Gemini와도 무관한 interaction_box_* 필드 2개를
    # 추가해 nHands를 24바이트 뒤에서 읽는 결함이 있었다.
    tracking_layout = (
        r"\s*LEAP_FRAME_HEADER\s+info\s*;"
        r"\s*int64_t\s+tracking_frame_id\s*;"
        r"\s*uint32_t\s+nHands\s*;"
        r"\s*(?:const\s+)?LEAP_HAND\s*\*\s*pHands\s*;"
        r"\s*float\s+framerate\s*;\s*"
    )
    frame_header_layout = (
        r"\s*void\s*\*\s*reserved\s*;"
        r"\s*int64_t\s+frame_id\s*;"
        r"\s*int64_t\s+timestamp\s*;\s*"
    )
    if not re.fullmatch(tracking_layout, tb) or not re.fullmatch(frame_header_layout, fb):
        raise RuntimeError(
            "Orion LEAP_TRACKING_EVENT / LEAP_FRAME_HEADER의 필드 순서가 "
            "확인된 4.1 ABI와 다릅니다. 해당 헤더로 직접 배치를 확인해야 합니다."
        )

    # Orion SDK는 보통 pack(1)을 사용하지만 설치된 헤더를 우선으로 판정
    match = re.search(r"#\s*pragma\s+pack\s*\(\s*(?:push\s*,\s*)?(\d+)\s*\)", header)
    pack = int(match.group(1)) if match else None

    class Struct(C.Structure):
        if pack:
            _pack_ = pack
    class Vec3(Struct):
        _fields_ = [("x", C.c_float), ("y", C.c_float), ("z", C.c_float)]
    class Quaternion(Struct):
        _fields_ = [("x", C.c_float), ("y", C.c_float), ("z", C.c_float), ("w", C.c_float)]
    class Bone(Struct):
        _fields_ = [("prev_joint", Vec3), ("next_joint", Vec3),
                    ("width", C.c_float), ("rotation", Quaternion)]
    digit_fields = [("finger_id", C.c_int32), ("bones", Bone * 4)]
    if re.search(r"\bLEAP_VECTOR\s+tip_velocity\s*;", db):
        digit_fields.append(("tip_velocity", Vec3))
    if re.search(r"\bLEAP_VECTOR\s+stabilized_tip_position\s*;", db):
        digit_fields.append(("stabilized_tip_position", Vec3))
    digit_fields.append(("is_extended", C.c_uint32))
    class Digit(Struct):
        _fields_ = digit_fields
    palm_fields = [("position", Vec3), ("stabilized_position", Vec3),
                   ("velocity", Vec3), ("normal", Vec3), ("width", C.c_float),
                   ("direction", Vec3)]
    if re.search(r"\bLEAP_QUATERNION\s+orientation\s*;", pb):
        palm_fields.append(("orientation", Quaternion))
    class Palm(Struct):
        _fields_ = palm_fields
    class Hand(Struct):
        _fields_ = [("id", C.c_uint32), ("flags", C.c_uint32),
                    ("type", C.c_int32), ("confidence", C.c_float),
                    ("visible_time", C.c_uint64), ("pinch_distance", C.c_float),
                    ("grab_angle", C.c_float), ("pinch_strength", C.c_float),
                    ("grab_strength", C.c_float), ("palm", Palm), ("digits", Digit * 5),
                    ("arm", Bone)]
    class FrameHeader(Struct):
        _fields_ = [("reserved", C.c_void_p), ("frame_id", C.c_int64),
                    ("timestamp", C.c_int64)]
    class Tracking(Struct):
        _fields_ = [("info", FrameHeader), ("tracking_frame_id", C.c_int64),
                    ("nHands", C.c_uint32), ("pHands", C.POINTER(Hand)),
                    ("framerate", C.c_float)]
    class Message(Struct):
        _fields_ = [("size", C.c_uint32), ("type", C.c_int32),
                    ("pointer", C.c_void_p)]
        if re.search(r"\buint32_t\s+device_id\s*;", mb):
            _fields_.append(("device_id", C.c_uint32))

    # 포인터를 읽기 전에 내부 ABI의 대표적인 오프셋을 점검한다.
    # Python 환경에서 C 구조체가 잘못 정렬되면 숫자는 그럴듯해도 데이터는 틀릴 수 있다.
    if pack != 1 or not (
        C.sizeof(FrameHeader) == 24 and
        Tracking.nHands.offset == 32 and
        Tracking.pHands.offset == 36 and
        Tracking.framerate.offset == 44 and
        C.sizeof(Tracking) == 48 and
        Message.pointer.offset == 8 and
        C.sizeof(Message) in (16, 20)
    ):
        raise RuntimeError("ctypes ABI 정렬 검사 실패. pack(1) 및 포인터 크기를 확인하세요.")

    return {
        "pack": pack, "Vec3": Vec3, "Bone": Bone, "Digit": Digit,
        "Palm": Palm, "Hand": Hand, "Tracking": Tracking, "Message": Message,
        "events": event_values(src),
    }


def vec(v):
    return float(v.x), float(v.y), float(v.z)


def convert_hand(hand, tracking_frame_id: int, fps: float, t: float) -> HandSample:
    bones, chains, tips = [], [], []
    for d in hand.digits:
        segments = [(vec(b.prev_joint), vec(b.next_joint)) for b in d.bones]
        bones.append(segments)
        tips.append(segments[3][1])
        chains.append([segments[1][0], segments[1][1], segments[2][1]])
    return HandSample(
        frame_id=int(tracking_frame_id), t=t, hand_id=int(hand.id),
        side="LEFT" if hand.type == 0 else "RIGHT",
        palm=vec(hand.palm.position), palm_width=float(hand.palm.width),
        tips=tips, bones=bones, chains=chains,
        confidence=float(hand.confidence), sdk_pinch=float(hand.pinch_strength),
        fps=float(fps),
    )


class OrionReader:
    def __init__(self, sdk: Path = SDK):
        if platform.system() != "Windows" or C.sizeof(C.c_void_p) != 8:
            raise RuntimeError("Windows 64비트 Python 환경이 필요합니다.")
        self.sdk = Path(sdk)
        paths = [self.sdk / "include" / "LeapC.h", self.sdk / "Include" / "LeapC.h"]
        header_path = next((p for p in paths if p.is_file()), None)
        if header_path is None:
            matches = list(self.sdk.glob("**/LeapC.h"))
            header_path = matches[0] if matches else None
        if header_path is None:
            raise RuntimeError("설치된 LeapSDK에서 LeapC.h를 찾지 못했습니다. 파일 경로를 확인하세요.")
        self.header_path = header_path
        self.abi = make_abi(header_path.read_text(encoding="utf-8-sig", errors="replace"))
        dll_path = self.sdk / "lib" / "x64" / "LeapC.dll"
        if not dll_path.is_file():
            raise RuntimeError("LeapC.dll이 존재하지 않습니다: " + str(dll_path))
        self._dll_dir = os.add_dll_directory(str(dll_path.parent)) if hasattr(os, "add_dll_directory") else None
        self.dll = C.WinDLL(str(dll_path))
        self.dll.LeapCreateConnection.argtypes = [C.c_void_p, C.POINTER(C.c_void_p)]
        self.dll.LeapCreateConnection.restype = C.c_uint32
        self.dll.LeapOpenConnection.argtypes = [C.c_void_p]
        self.dll.LeapOpenConnection.restype = C.c_uint32
        self.dll.LeapPollConnection.argtypes = [C.c_void_p, C.c_uint32, C.POINTER(self.abi["Message"])]
        self.dll.LeapPollConnection.restype = C.c_uint32
        self.dll.LeapDestroyConnection.argtypes = [C.c_void_p]
        self.dll.LeapDestroyConnection.restype = None
        self.handle = C.c_void_p()
        self.connected = False
        self.frame_count = 0
        self.last_frame_at = 0.0
        self.last_rc = 0
        self.messages = []
        self.device_detected = False
        self.device_failures = 0
        self.device_lost_events = 0
        self.zero_hand_frames = 0
        self.other_hand_frames = 0
        self.seen_sides = {"LEFT": 0, "RIGHT": 0}
        self.event_counts = {}

    def open(self):
        rc = self.dll.LeapCreateConnection(None, C.byref(self.handle))
        if rc or not self.handle.value:
            raise RuntimeError("LeapCreateConnection 실패: 0x%08X" % rc)
        rc = self.dll.LeapOpenConnection(self.handle)
        if rc:
            self.close()
            raise RuntimeError("LeapOpenConnection 실패: 0x%08X" % rc)

    def poll(self, side: str, timeout_ms=35):
        """반환값: (새_추적_프레임인가, HandSample | None)."""
        if not self.handle.value:
            raise RuntimeError("연결이 열리지 않았습니다.")
        msg = self.abi["Message"]()
        msg.size = C.sizeof(msg)
        rc = self.dll.LeapPollConnection(self.handle, int(timeout_ms), C.byref(msg))
        self.last_rc = rc
        if rc:
            # 타임아웃은 정상적인 폴링 상태. 그 외 코드는 간헐적으로 안내
            if rc != 0xE2010004 and len(self.messages) < 20:
                self.messages.append("LeapPollConnection: 0x%08X" % rc)
            return False, None
        ev = self.abi["events"]
        names = {value: key.replace("eLeapEventType_", "") for key, value in ev.items()}
        event_name = names.get(msg.type, "UNKNOWN(%d)" % msg.type)
        self.event_counts = getattr(self, "event_counts", {})
        self.event_counts[event_name] = self.event_counts.get(event_name, 0) + 1
        if msg.type == ev.get("eLeapEventType_Device", -1):
            self.device_detected = True
            self.messages.append("Leap device event detected")
        elif msg.type == ev.get("eLeapEventType_DeviceLost", -1):
            self.device_detected = False
            self.device_lost_events += 1
            self.messages.append("Leap device lost")
        elif msg.type == ev.get("eLeapEventType_DeviceFailure", -1):
            self.device_failures += 1
            self.messages.append("Leap device failure")
        if msg.type == ev["eLeapEventType_Connection"]:
            self.connected = True
            self.messages.append("추적 서비스 연결 완료")
            return False, None
        if msg.type == ev.get("eLeapEventType_ConnectionLost", -1):
            self.connected = False
            self.messages.append("추적 서비스 연결 끊김")
            return False, None
        if msg.type != ev["eLeapEventType_Tracking"] or not msg.pointer:
            return False, None
        frame = C.cast(msg.pointer, C.POINTER(self.abi["Tracking"])).contents
        # 잘못된 구조체 배치 가능성이 있으면 손가락 영역을 읽기 전에 중지.
        # 프레임 포인터는 다음 LeapPollConnection 호출 전까지만 사용한다.
        if frame.nHands > 2 or not (0 <= frame.framerate <= 500):
            raise RuntimeError(
                "추적 프레임 배치 검사 실패: nHands=%d, fps=%.1f "
                "(추적 이벤트 ABI나 DLL 버전 확인 필요)" %
                (frame.nHands, frame.framerate)
            )
        self.frame_count += 1
        self.last_frame_at = time.monotonic()
        if frame.nHands == 0:
            self.zero_hand_frames = getattr(self, "zero_hand_frames", 0) + 1
            return True, None
        if not bool(frame.pHands):
            raise RuntimeError("nHands가 1 이상인데 pHands 포인터가 없습니다.")
        selected = None
        for i in range(frame.nHands):
            hand = frame.pHands[i]
            if hand.type not in (0, 1) or not (15.0 <= hand.palm.width <= 180.0):
                raise RuntimeError(
                    "손 데이터 배치 검사 실패: type=%d, palm.width=%.1f. "
                    "LeapC.h 배치를 확인하세요." % (hand.type, hand.palm.width)
                )
            self.seen_sides = getattr(self, "seen_sides", {"LEFT": 0, "RIGHT": 0})
            self.seen_sides["LEFT" if hand.type == 0 else "RIGHT"] += 1
            if (side == "right" and hand.type == 1) or (side == "left" and hand.type == 0):
                selected = convert_hand(hand, int(frame.tracking_frame_id), frame.framerate, self.last_frame_at)
        if selected is None:
            self.other_hand_frames = getattr(self, "other_hand_frames", 0) + 1
        return True, selected

    def close(self):
        if self.handle.value:
            self.dll.LeapDestroyConnection(self.handle)
            self.handle = C.c_void_p()
        if self._dll_dir is not None:
            self._dll_dir.close()
            self._dll_dir = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
