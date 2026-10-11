"""按名称创建后端。"""

from __future__ import annotations

from pc.backend.base import ArmBackend
from pc.backend.console import ConsoleBackend
from pc.backend.serial_arm import SerialArmBackend
from pc.backend.sim_pybullet import SimArmBackend


def create_backend(name: str = "console", **kwargs) -> ArmBackend:
    key = name.strip().lower()
    if key == "console":
        return ConsoleBackend(**kwargs)
    if key in {"sim", "pybullet", "sim_pybullet"}:
        return SimArmBackend(**kwargs)
    if key in {"serial", "serial_arm"}:
        return SerialArmBackend(**kwargs)
    raise ValueError(
        f"Unknown backend '{name}'. Expected: console | sim | serial"
    )
