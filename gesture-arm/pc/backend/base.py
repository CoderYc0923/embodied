"""ArmBackend 统一接口（阶段 0 冻结）。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from pc.types import JointFrame


class ArmBackend(ABC):
    """执行器后端抽象：仿真 / 串口真机 / 控制台日志实现同一接口。"""

    @abstractmethod
    def connect(self) -> None:
        """建立连接或初始化资源。"""

    @abstractmethod
    def close(self) -> None:
        """释放资源。"""

    @abstractmethod
    def home(self) -> None:
        """回到初始姿态。"""

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """ENABLE/DISABLE：关闭后忽略新的关节目标，保持当前角。"""

    @abstractmethod
    def set_joints(self, j1: float, j2: float, j3: float, grip: float) -> None:
        """下发关节目标角（度）。后端内部应做硬限幅。"""

    @abstractmethod
    def get_joints(self) -> Tuple[float, float, float, float]:
        """读取当前关节角（度），顺序为 j1, j2, j3, grip。"""

    # ---- 便捷方法（非抽象，所有后端共用） ----

    def set_joint_frame(self, frame: JointFrame) -> None:
        self.set_joints(frame.j1, frame.j2, frame.j3, frame.grip)

    def ping(self) -> bool:
        """连通性探测；默认认为已连接即可。真机后端可覆写。"""
        return True
