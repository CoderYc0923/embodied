"""手部状态 → 关节目标（阶段 1 简易线性映射）。"""

from __future__ import annotations

from pc.perception.hand_state import HandState
from pc.types import DEFAULT_LIMITS, JointFrame, JointLimits


def _clamp(value: float, bounds: tuple[float, float]) -> float:
    lo, hi = bounds
    return max(lo, min(hi, value))


class HandToJointMapper:
    """
    模式 A：
      手 x → j1（左右）
      手 y → j2（上下；画面 y 向下，故取反更符合「手抬高臂抬高」）
      j3 暂固定或弱跟随 scale
      pinch → grip（捏合越小夹爪越闭）
    """

    def __init__(
        self,
        limits: JointLimits = DEFAULT_LIMITS,
        j3_fixed: float = 90.0,
        use_scale_for_j3: bool = False,
        pinch_min: float = 0.05,
        pinch_max: float = 1.0,
        scale_min: float = 0.05,
        scale_span: float = 0.25,
    ) -> None:
        self.limits = limits
        self.j3_fixed = j3_fixed
        self.use_scale_for_j3 = use_scale_for_j3
        self.pinch_min = pinch_min
        self.pinch_max = max(pinch_min + 1e-6, pinch_max)
        self.scale_min = scale_min
        self.scale_span = max(1e-6, scale_span)

    @classmethod
    def from_config(cls, cfg: dict, limits: JointLimits | None = None) -> HandToJointMapper:
        mapping = cfg.get("mapping", {})
        return cls(
            limits=limits or DEFAULT_LIMITS,
            j3_fixed=float(mapping.get("j3_fixed", 90.0)),
            use_scale_for_j3=bool(mapping.get("use_scale_for_j3", False)),
            pinch_min=float(mapping.get("pinch_min", 0.05)),
            pinch_max=float(mapping.get("pinch_max", 1.0)),
            scale_min=float(mapping.get("scale_min", 0.05)),
            scale_span=float(mapping.get("scale_span", 0.25)),
        )

    def map(self, hand: HandState) -> JointFrame:
        j1 = _lerp(self.limits.j1[0], self.limits.j1[1], hand.x)
        j2 = _lerp(self.limits.j2[0], self.limits.j2[1], 1.0 - hand.y)

        if self.use_scale_for_j3:
            t = _clamp((hand.scale - self.scale_min) / self.scale_span, (0.0, 1.0))
            j3 = _lerp(self.limits.j3[0], self.limits.j3[1], t)
        else:
            j3 = self.j3_fixed

        # 这里的 hand.pinch 已在感知层按尺度归一化；再按配置裁剪映射到夹爪
        pinch_t = _clamp(hand.pinch, (self.pinch_min, self.pinch_max))
        open_amount = (pinch_t - self.pinch_min) / (self.pinch_max - self.pinch_min)
        grip = _lerp(self.limits.grip[1], self.limits.grip[0], open_amount)

        return JointFrame(j1, j2, j3, grip).clamp(self.limits)


def _lerp(a: float, b: float, t: float) -> float:
    t = _clamp(t, (0.0, 1.0))
    return a + (b - a) * t
