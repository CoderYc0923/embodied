"""跟踪状态机：LOST <-> TRACKING，带 hit/miss 计数防抖。"""

from __future__ import annotations

from pc.perception.hand_state import TrackStatus


class TrackStateMachine:
    def __init__(self, hit_frames: int = 3, miss_frames: int = 10) -> None:
        self.hit_frames = max(1, hit_frames)
        self.miss_frames = max(1, miss_frames)
        self.status = TrackStatus.LOST
        self._hit = 0
        self._miss = 0

    def update(self, detected: bool) -> TrackStatus:
        if detected:
            self._hit += 1
            self._miss = 0
            if self.status == TrackStatus.LOST and self._hit >= self.hit_frames:
                self.status = TrackStatus.TRACKING
        else:
            self._miss += 1
            self._hit = 0
            if self.status == TrackStatus.TRACKING and self._miss >= self.miss_frames:
                self.status = TrackStatus.LOST
        return self.status

    def reset(self) -> None:
        self.status = TrackStatus.LOST
        self._hit = 0
        self._miss = 0
