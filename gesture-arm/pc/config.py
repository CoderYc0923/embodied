"""加载 config.yaml。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pc.types import JointLimits

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "config.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.is_file():
        raise FileNotFoundError(f"配置文件不存在: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"配置文件格式错误，根节点应为 mapping: {cfg_path}")
    return data


def joint_limits_from_config(cfg: dict[str, Any]) -> JointLimits:
    limits = cfg.get("limits", {})
    return JointLimits(
        j1=_pair(limits.get("j1"), (0.0, 180.0)),
        j2=_pair(limits.get("j2"), (0.0, 180.0)),
        j3=_pair(limits.get("j3"), (0.0, 180.0)),
        grip=_pair(limits.get("grip"), (0.0, 100.0)),
    )


def home_joints_from_config(cfg: dict[str, Any]) -> tuple[float, float, float, float]:
    home = cfg.get("home", {})
    joints = home.get("joints", [90.0, 90.0, 90.0, 0.0])
    if len(joints) != 4:
        raise ValueError("home.joints 必须是长度为 4 的数组: [j1, j2, j3, grip]")
    return (float(joints[0]), float(joints[1]), float(joints[2]), float(joints[3]))


def _pair(value: Any, default: tuple[float, float]) -> tuple[float, float]:
    if value is None:
        return default
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"限位应为 [min, max]，收到: {value!r}")
    return (float(value[0]), float(value[1]))
