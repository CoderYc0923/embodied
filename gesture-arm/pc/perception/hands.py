"""MediaPipe Hands 封装（Tasks API，兼容 mediapipe 1.x）。"""

from __future__ import annotations

import math
import time
import urllib.request
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Sequence

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

from pc.perception.hand_state import HandState, TrackStatus
from pc.perception.track_fsm import TrackStateMachine

# gesture-arm/models/hand_landmarker.task
_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_MODEL = _ROOT / "models" / "hand_landmarker.task"
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


class FollowPoint(str, Enum):
    INDEX_TIP = "index_tip"
    WRIST = "wrist"


_WRIST = 0
_THUMB_TIP = 4
_INDEX_TIP = 8
_MIDDLE_MCP = 9
_PINKY_MCP = 17


def ensure_hand_model(model_path: Path = _DEFAULT_MODEL) -> Path:
    """若本地无模型则自动下载。"""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    if model_path.exists() and model_path.stat().st_size > 0:
        return model_path
    print(f"Downloading hand_landmarker model -> {model_path}")
    urllib.request.urlretrieve(_MODEL_URL, model_path)
    return model_path


class HandTracker:
    def __init__(
        self,
        follow_point: FollowPoint = FollowPoint.INDEX_TIP,
        max_num_hands: int = 1,
        detection_confidence: float = 0.5,
        presence_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
        hit_frames: int = 3,
        miss_frames: int = 10,
        pinch_norm_scale: float = 1.8,
        model_path: Path | str | None = None,
    ) -> None:
        self.follow_point = follow_point
        self.pinch_norm_scale = max(1e-6, pinch_norm_scale)
        self._fsm = TrackStateMachine(hit_frames=hit_frames, miss_frames=miss_frames)
        path = ensure_hand_model(Path(model_path) if model_path else _DEFAULT_MODEL)
        # Windows 下原生层对中文路径不友好，改用 buffer 加载
        model_buffer = path.read_bytes()

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=model_buffer),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=presence_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._timestamp_ms = 0
        self._last_landmarks: Optional[Sequence[Any]] = None
        self._last_good: Optional[HandState] = None
        self._connections = [
            (c.start, c.end) for c in vision.HandLandmarksConnections.HAND_CONNECTIONS
        ]

    def close(self) -> None:
        self._landmarker.close()

    def set_follow_point(self, follow_point: FollowPoint) -> None:
        self.follow_point = follow_point

    def process(self, frame_bgr: np.ndarray) -> HandState:
        """处理一帧 BGR 图像（建议传入已镜像画面）。"""
        now = time.time()
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO 模式要求时间戳单调递增
        self._timestamp_ms += max(1, int((now * 1000) - self._timestamp_ms))
        if self._timestamp_ms <= 0:
            self._timestamp_ms = 1

        result = self._landmarker.detect_for_video(mp_image, self._timestamp_ms)
        detected = bool(result.hand_landmarks)
        status = self._fsm.update(detected)

        if detected:
            landmarks = result.hand_landmarks[0]
            self._last_landmarks = landmarks
            measured = self._landmarks_to_state(landmarks, status, now)
            if status == TrackStatus.TRACKING:
                self._last_good = measured
            return measured

        self._last_landmarks = None
        if status == TrackStatus.TRACKING and self._last_good is not None:
            return HandState(
                x=self._last_good.x,
                y=self._last_good.y,
                scale=self._last_good.scale,
                pinch=self._last_good.pinch,
                status=TrackStatus.TRACKING,
                timestamp=now,
            )
        self._last_good = None
        return HandState.lost(now)

    def draw(self, frame_bgr: np.ndarray) -> None:
        if self._last_landmarks is None:
            return
        h, w = frame_bgr.shape[:2]
        pts = []
        for lm in self._last_landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            pts.append((x, y))
            cv2.circle(frame_bgr, (x, y), 3, (0, 255, 0), -1, cv2.LINE_AA)

        for start, end in self._connections:
            if start < len(pts) and end < len(pts):
                cv2.line(frame_bgr, pts[start], pts[end], (0, 200, 255), 2, cv2.LINE_AA)

    def _landmarks_to_state(
        self,
        landmarks: Sequence[Any],
        status: TrackStatus,
        timestamp: float,
    ) -> HandState:
        follow_idx = (
            _INDEX_TIP if self.follow_point == FollowPoint.INDEX_TIP else _WRIST
        )
        follow = landmarks[follow_idx]
        thumb = landmarks[_THUMB_TIP]
        index = landmarks[_INDEX_TIP]
        wrist = landmarks[_WRIST]
        middle_mcp = landmarks[_MIDDLE_MCP]
        pinky_mcp = landmarks[_PINKY_MCP]

        scale_a = _dist(wrist, middle_mcp)
        scale_b = _dist(middle_mcp, pinky_mcp)
        scale = max(scale_a, scale_b, 1e-6)

        pinch_raw = _dist(thumb, index)
        pinch = float(np.clip(pinch_raw / (scale * self.pinch_norm_scale), 0.0, 1.5))

        return HandState(
            x=float(np.clip(follow.x, 0.0, 1.0)),
            y=float(np.clip(follow.y, 0.0, 1.0)),
            scale=float(scale),
            pinch=pinch,
            status=status,
            timestamp=timestamp,
        )


def _dist(a: Any, b: Any) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
