"""简单限频与死区，避免刷爆后端。"""

from __future__ import annotations

import time

from pc.types import JointFrame


class JointSendGate:
    def __init__(self, hz: float = 20.0, deadband_deg: float = 1.5) -> None:
        self.min_interval = 1.0 / hz if hz > 0 else 0.0
        self.deadband_deg = deadband_deg
        self._last_t = 0.0
        self._last_sent: JointFrame | None = None

    def should_send(self, frame: JointFrame) -> bool:
        now = time.perf_counter()
        if self.min_interval > 0 and (now - self._last_t) < self.min_interval:
            return False
        if self._last_sent is not None and _max_delta(self._last_sent, frame) < self.deadband_deg:
            return False
        self._last_t = now
        self._last_sent = frame
        return True

    def reset(self) -> None:
        self._last_t = 0.0
        self._last_sent = None


def _max_delta(a: JointFrame, b: JointFrame) -> float:
    return max(
        abs(a.j1 - b.j1),
        abs(a.j2 - b.j2),
        abs(a.j3 - b.j3),
        abs(a.grip - b.grip),
    )
