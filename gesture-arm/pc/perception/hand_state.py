"""手部状态数据结构。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TrackStatus(str, Enum):
    TRACKING = "TRACKING"
    LOST = "LOST"


@dataclass(frozen=True)
class HandState:
    """归一化手部特征，供映射层使用。"""

    x: float  # 主跟随点，图像坐标归一化到 [0, 1]，原点左上
    y: float
    scale: float  # 手部尺度（相对画面），粗深度代理
    pinch: float  # 拇指-食指距离，已按手部尺度归一化，约 [0, 1+]
    status: TrackStatus
    timestamp: float

    @classmethod
    def lost(cls, timestamp: float) -> HandState:
        return cls(
            x=0.5,
            y=0.5,
            scale=0.0,
            pinch=1.0,
            status=TrackStatus.LOST,
            timestamp=timestamp,
        )
