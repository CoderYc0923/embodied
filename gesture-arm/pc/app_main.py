"""阶段 1 主入口：真摄像头手部跟踪 → 映射 → ConsoleBackend。

用法（在 gesture-arm 目录下）:
    python -m pc.app_main
    python -m pc.app_main --config config.yaml
    python -m pc.app_main --camera 1   # CLI 可覆盖 config
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

from pc.backend import create_backend
from pc.capture import Camera
from pc.config import (
    DEFAULT_CONFIG_PATH,
    home_joints_from_config,
    joint_limits_from_config,
    load_config,
)
from pc.filter import JointSendGate
from pc.mapping import HandToJointMapper
from pc.perception import FollowPoint, HandTracker, TrackStatus
from pc.types import JointFrame
from pc.viz import draw_hud


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gesture Arm Phase 1 - hand tracking")
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="配置文件路径（默认 config.yaml）",
    )
    # 下列参数默认 None：未传则使用 config.yaml
    parser.add_argument("--camera", type=int, default=None, help="覆盖 camera.device_id")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--no-mirror", action="store_true", help="覆盖为关闭镜像")
    parser.add_argument(
        "--follow",
        choices=["index_tip", "wrist"],
        default=None,
        help="覆盖 perception.follow_point",
    )
    parser.add_argument("--hz", type=float, default=None, help="覆盖 control.send_hz")
    parser.add_argument(
        "--verbose-backend",
        action="store_true",
        help="覆盖 backend.verbose=true",
    )
    parser.add_argument(
        "--backend",
        default=None,
        choices=["console"],
        help="覆盖 backend.name（阶段 1 仅 console）",
    )
    return parser.parse_args()


def _follow_point(name: str) -> FollowPoint:
    return FollowPoint.INDEX_TIP if name == "index_tip" else FollowPoint.WRIST


def main() -> int:
    args = parse_args()
    cfg = load_config(args.config)

    cam_cfg = cfg.get("camera", {})
    per_cfg = cfg.get("perception", {})
    ctl_cfg = cfg.get("control", {})
    backend_cfg = cfg.get("backend", {})

    device_id = args.camera if args.camera is not None else int(cam_cfg.get("device_id", 0))
    width = args.width if args.width is not None else int(cam_cfg.get("width", 640))
    height = args.height if args.height is not None else int(cam_cfg.get("height", 480))
    mirror = False if args.no_mirror else bool(cam_cfg.get("mirror", True))

    follow_name = args.follow or str(per_cfg.get("follow_point", "index_tip"))
    follow = _follow_point(follow_name)

    send_hz = float(args.hz if args.hz is not None else ctl_cfg.get("send_hz", 20.0))
    deadband = float(ctl_cfg.get("deadband_deg", 1.5))
    enabled = bool(ctl_cfg.get("start_enabled", True))

    backend_name = args.backend or str(backend_cfg.get("name", "console"))
    verbose = True if args.verbose_backend else bool(backend_cfg.get("verbose", False))

    limits = joint_limits_from_config(cfg)
    home = home_joints_from_config(cfg)

    backend = create_backend(
        backend_name,
        verbose=verbose,
        limits=limits,
        home_joints=home,
    )
    tracker = HandTracker(
        follow_point=follow,
        max_num_hands=int(per_cfg.get("max_num_hands", 1)),
        detection_confidence=float(per_cfg.get("min_hand_detection_confidence", 0.5)),
        presence_confidence=float(per_cfg.get("min_hand_presence_confidence", 0.5)),
        tracking_confidence=float(per_cfg.get("min_tracking_confidence", 0.5)),
        hit_frames=int(per_cfg.get("hit_frames", 3)),
        miss_frames=int(per_cfg.get("miss_frames", 10)),
        pinch_norm_scale=float(per_cfg.get("pinch_norm_scale", 1.8)),
    )
    mapper = HandToJointMapper.from_config(cfg, limits=limits)
    gate = JointSendGate(hz=send_hz, deadband_deg=deadband)

    last_joints = JointFrame(*home).clamp(limits)
    last_status = TrackStatus.LOST
    fps = 0.0
    frame_count = 0
    fps_t0 = time.perf_counter()

    camera = Camera(
        device_id=device_id,
        width=width,
        height=height,
        mirror=mirror,
    )

    print(f"Loaded config: {Path(args.config).resolve()}")
    print(
        f"camera={device_id} follow={follow.value} hz={send_hz} "
        f"deadband={deadband} backend={backend_name}"
    )
    print("Keys: Q=quit  Space=ENABLE/DISABLE  F=switch follow point")

    try:
        camera.open()
        backend.connect()
        backend.set_enabled(enabled)

        while True:
            ok, frame = camera.read()
            if not ok or frame is None:
                print("读取摄像头失败，退出。")
                break

            hand = tracker.process(frame)
            tracker.draw(frame)

            if hand.status == TrackStatus.TRACKING:
                target = mapper.map(hand)
                if enabled and gate.should_send(target):
                    backend.set_joint_frame(target)
                    last_joints = target

            if hand.status != last_status:
                print(f"[track] {last_status.value} -> {hand.status.value}")
                last_status = hand.status

            frame_count += 1
            elapsed = time.perf_counter() - fps_t0
            if elapsed >= 0.5:
                fps = frame_count / elapsed
                frame_count = 0
                fps_t0 = time.perf_counter()

            draw_hud(
                frame,
                hand=hand,
                joints=last_joints,
                fps=fps,
                enabled=enabled,
                follow_point=tracker.follow_point.value,
            )
            cv2.imshow("gesture-arm / phase1 hand tracking", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key == ord(" "):
                enabled = not enabled
                backend.set_enabled(enabled)
                gate.reset()
                print(f"[ctrl] {'ENABLE' if enabled else 'DISABLE'}")
            if key in (ord("f"), ord("F")):
                follow = (
                    FollowPoint.WRIST
                    if tracker.follow_point == FollowPoint.INDEX_TIP
                    else FollowPoint.INDEX_TIP
                )
                tracker.set_follow_point(follow)
                print(f"[follow] {follow.value}")

    finally:
        tracker.close()
        backend.close()
        camera.close()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
