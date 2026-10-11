"""阶段 0 冒烟测试：不经手部，对 Backend 下发关节序列。

用法（在 gesture-arm 目录下）:
    python tools/backend_smoke_test.py
    python tools/backend_smoke_test.py --backend console
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pc.backend import create_backend
from pc.types import JointFrame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ArmBackend smoke test")
    parser.add_argument(
        "--backend",
        default="console",
        help="console | sim | serial（阶段 0 请用 console）",
    )
    parser.add_argument(
        "--hz",
        type=float,
        default=10.0,
        help="扫描序列发送频率",
    )
    return parser.parse_args()


def build_scan_sequence() -> list[JointFrame]:
    """一组可预期的关节目标，覆盖 home / 运动 / 夹爪 / 越限夹紧。"""
    return [
        JointFrame.home(),
        JointFrame(60.0, 100.0, 80.0, 0.0),
        JointFrame(120.0, 80.0, 100.0, 40.0),
        JointFrame(90.0, 120.0, 60.0, 80.0),
        JointFrame(90.0, 90.0, 90.0, 100.0),
        # 故意越限，验证硬限幅
        JointFrame(-20.0, 260.0, 90.0, 150.0),
        JointFrame.home(),
    ]


def main() -> int:
    args = parse_args()
    period = 1.0 / args.hz if args.hz > 0 else 0.0

    backend = create_backend(args.backend)
    print(f"=== backend smoke test: {type(backend).__name__} ===")

    backend.connect()
    assert backend.ping() is True

    backend.home()
    print(f"after home: {backend.get_joints()}")

    print("--- ENABLE scan ---")
    backend.set_enabled(True)
    for frame in build_scan_sequence():
        backend.set_joint_frame(frame)
        print(f"get_joints: {backend.get_joints()}")
        if period:
            time.sleep(period)

    print("--- DISABLE should ignore next target ---")
    backend.set_enabled(False)
    backend.set_joints(45.0, 45.0, 45.0, 10.0)
    disabled_joints = backend.get_joints()
    print(f"get_joints while disabled: {disabled_joints}")

    print("--- ENABLE + HOME ---")
    backend.set_enabled(True)
    backend.home()
    print(f"final: {backend.get_joints()}")

    backend.close()
    print("=== smoke test OK ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
