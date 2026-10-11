"""无摄像头的阶段 1 状态机快速自检。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pc.perception import TrackStatus, TrackStateMachine


def main() -> int:
    fsm = TrackStateMachine(hit_frames=3, miss_frames=4)
    assert fsm.status == TrackStatus.LOST
    assert fsm.update(True) == TrackStatus.LOST
    assert fsm.update(True) == TrackStatus.LOST
    assert fsm.update(True) == TrackStatus.TRACKING
    assert fsm.update(False) == TrackStatus.TRACKING
    assert fsm.update(False) == TrackStatus.TRACKING
    assert fsm.update(False) == TrackStatus.TRACKING
    assert fsm.update(False) == TrackStatus.LOST
    print("track fsm OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
