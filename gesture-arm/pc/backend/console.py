"""控制台后端：打印协议帧，用于阶段 0 接口验证。"""

from __future__ import annotations

from typing import TextIO, Tuple

from pc.backend.base import ArmBackend
from pc.types import DEFAULT_LIMITS, HOME_JOINTS, JointFrame, JointLimits


class ConsoleBackend(ArmBackend):
    def __init__(
        self,
        limits: JointLimits = DEFAULT_LIMITS,
        stream: TextIO | None = None,
    ) -> None:
        self._limits = limits
        self._stream = stream  # None → print
        self._connected = False
        self._enabled = True
        self._joints = JointFrame.home()

    def _log(self, message: str) -> None:
        if self._stream is None:
            print(message)
        else:
            self._stream.write(message + "\n")
            self._stream.flush()

    def connect(self) -> None:
        self._connected = True
        self._enabled = True
        self._joints = JointFrame.home()
        self._log("[ConsoleBackend] CONNECT")
        self._log(f"[ConsoleBackend] {self._joints.to_command()}  # home on connect")

    def close(self) -> None:
        self._connected = False
        self._log("[ConsoleBackend] CLOSE")

    def home(self) -> None:
        self._ensure_connected()
        self._joints = JointFrame(*HOME_JOINTS).clamp(self._limits)
        self._log(f"[ConsoleBackend] HOME -> {self._joints.to_command()}")

    def set_enabled(self, enabled: bool) -> None:
        self._ensure_connected()
        self._enabled = enabled
        state = "ENABLE" if enabled else "DISABLE"
        self._log(f"[ConsoleBackend] {state}")

    def set_joints(self, j1: float, j2: float, j3: float, grip: float) -> None:
        self._ensure_connected()
        if not self._enabled:
            self._log("[ConsoleBackend] IGNORE set_joints (disabled)")
            return

        target = JointFrame(j1, j2, j3, grip).clamp(self._limits)
        if target != JointFrame(j1, j2, j3, grip):
            self._log(
                f"[ConsoleBackend] ERR:RANGE clamped -> {target.to_command()}"
            )
        self._joints = target
        self._log(f"[ConsoleBackend] {self._joints.to_command()}")

    def get_joints(self) -> Tuple[float, float, float, float]:
        self._ensure_connected()
        return self._joints.as_tuple()

    def ping(self) -> bool:
        self._ensure_connected()
        self._log("[ConsoleBackend] PING -> PONG")
        return True

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("ConsoleBackend is not connected; call connect() first")
