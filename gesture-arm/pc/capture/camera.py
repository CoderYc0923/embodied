"""摄像头采集。"""

from __future__ import annotations

import sys
from typing import Optional, Tuple

import cv2
import numpy as np


class Camera:
    def __init__(
        self,
        device_id: int = 0,
        width: int = 640,
        height: int = 480,
        mirror: bool = True,
    ) -> None:
        self.device_id = device_id
        self.width = width
        self.height = height
        self.mirror = mirror
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(self.device_id)

        if not cap.isOpened():
            # 回退默认后端
            cap.release()
            cap = cv2.VideoCapture(self.device_id)

        if not cap.isOpened():
            raise RuntimeError(
                f"无法打开摄像头 device_id={self.device_id}。"
                "请检查设备占用，或改用 --camera 1/2。"
            )

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cap = cap

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self._cap is None:
            raise RuntimeError("Camera is not open")
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return False, None
        if self.mirror:
            frame = cv2.flip(frame, 1)
        return True, frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> Camera:
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
