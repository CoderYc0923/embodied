"""跨模块共享的数据结构（阶段 0 冻结）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JointLimits:
    """各关节角度限位（度）。"""

    j1: tuple[float, float] = (0.0, 180.0)
    j2: tuple[float, float] = (0.0, 180.0)
    j3: tuple[float, float] = (0.0, 180.0)
    grip: tuple[float, float] = (0.0, 100.0)


DEFAULT_LIMITS = JointLimits()

# 上电 / HOME 默认姿态（度）
HOME_JOINTS = (90.0, 90.0, 90.0, 0.0)


def _clamp(value: float, bounds: tuple[float, float]) -> float:
    lo, hi = bounds
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class JointFrame:
    """连续控制关节帧，对应协议 `J,j1,j2,j3,grip`。"""

    j1: float
    j2: float
    j3: float
    grip: float

    @classmethod
    def home(cls) -> JointFrame:
        return cls(*HOME_JOINTS)

    def clamp(self, limits: JointLimits = DEFAULT_LIMITS) -> JointFrame:
        return JointFrame(
            j1=_clamp(self.j1, limits.j1),
            j2=_clamp(self.j2, limits.j2),
            j3=_clamp(self.j3, limits.j3),
            grip=_clamp(self.grip, limits.grip),
        )

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.j1, self.j2, self.j3, self.grip)

    def to_command(self) -> str:
        """序列化为真机串口文本协议（仿真后端可不经此路径）。"""
        return f"J,{self.j1:.2f},{self.j2:.2f},{self.j3:.2f},{self.grip:.2f}"
