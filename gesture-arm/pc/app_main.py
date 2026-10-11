"""主入口占位：阶段 3 再接入感知 + 仿真跟随闭环。"""

from __future__ import annotations

import argparse

from pc.backend import create_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gesture Arm main entry (phase stubs)")
    parser.add_argument(
        "--backend",
        default="console",
        choices=["console", "sim", "serial"],
        help="执行后端（阶段 0 仅 console 可用）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    backend = create_backend(args.backend)
    print(f"backend={args.backend} created: {type(backend).__name__}")
    print("阶段 0 请运行: python tools/backend_smoke_test.py")
    print("阶段 1+ 将在此接入摄像头跟踪与跟随闭环。")


if __name__ == "__main__":
    main()
