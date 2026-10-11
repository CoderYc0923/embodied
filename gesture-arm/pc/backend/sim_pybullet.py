"""PyBullet 仿真后端占位（阶段 2 实现）。"""

from __future__ import annotations

from typing import Tuple

from pc.backend.base import ArmBackend


class SimArmBackend(ArmBackend):
    def connect(self) -> None:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")

    def close(self) -> None:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")

    def home(self) -> None:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")

    def set_enabled(self, enabled: bool) -> None:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")

    def set_joints(self, j1: float, j2: float, j3: float, grip: float) -> None:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")

    def get_joints(self) -> Tuple[float, float, float, float]:
        raise NotImplementedError("SimArmBackend 将在阶段 2 实现")
