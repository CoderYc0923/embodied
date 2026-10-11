"""摄像头画面 HUD。"""

from __future__ import annotations

import cv2
import numpy as np

from pc.perception.hand_state import HandState, TrackStatus
from pc.types import JointFrame


def draw_hud(
    frame: np.ndarray,
    hand: HandState,
    joints: JointFrame,
    fps: float,
    enabled: bool,
    follow_point: str,
) -> None:
    h, w = frame.shape[:2]
    color = (0, 220, 0) if hand.status == TrackStatus.TRACKING else (0, 0, 220)

    lines = [
        f"FPS: {fps:.1f}",
        f"STATUS: {hand.status.value}",
        f"FOLLOW: {follow_point}",
        f"CTRL: {'ENABLE' if enabled else 'DISABLE'}",
        f"hand x={hand.x:.2f} y={hand.y:.2f} pinch={hand.pinch:.2f} scale={hand.scale:.3f}",
        f"J: {joints.to_command()}",
        "keys: [Q]quit  [Space]enable  [F]follow tip/wrist",
    ]
    y = 24
    for text in lines:
        cv2.putText(
            frame,
            text,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color if "STATUS" in text else (240, 240, 240),
            1,
            cv2.LINE_AA,
        )
        y += 22

    # 跟随点准星
    if hand.status == TrackStatus.TRACKING:
        cx, cy = int(hand.x * w), int(hand.y * h)
        cv2.drawMarker(
            frame,
            (cx, cy),
            (0, 255, 255),
            markerType=cv2.MARKER_CROSS,
            markerSize=18,
            thickness=2,
        )
