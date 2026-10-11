# 手部跟随桌面机械臂（Gesture Arm）

低成本入门具身智能项目：真摄像头跟踪手部 → 统一控制接口 → **仿真臂跟随**（真机后置）。

## 路径策略

**仿真臂练控制与进阶 + 真摄像头练跟随感知 → 接口统一 → 真机后置 →（可选）端侧**

完整设计见：[docs/DESIGN.md](./docs/DESIGN.md)

## 快速开始（阶段 0）

```bash
cd gesture-arm
python tools/backend_smoke_test.py
```

应看到 `ConsoleBackend` 打印 `J,...` 序列，并以 `smoke test OK` 结束。

## 当前状态

- [x] 设计方案（v0.3：仿真主线 + 真摄像头 + 统一接口）
- [x] 阶段 0：环境与仓库骨架 / ArmBackend 接口 / ConsoleBackend
- [ ] 阶段 1：真摄像头手部跟踪
- [ ] 阶段 2：PyBullet 仿真臂接入同一接口
- [ ] 阶段 3：手部跟随仿真闭环
- [ ] 阶段 4：控制进阶（限速、插值、工作空间等）
- [ ] 阶段 5：真机后置接入
- [ ] 阶段 6：端侧迁移（可选）

## 目录结构

```text
gesture-arm/
├── docs/DESIGN.md
├── protocols/commands.md
├── pc/
│   ├── types.py              # JointFrame（已冻结）
│   ├── backend/              # ArmBackend + Console / Sim占位 / Serial占位
│   └── app_main.py
├── sim/                      # URDF / 场景（阶段 2）
├── firmware/                 # 真机固件（阶段 5）
├── tools/backend_smoke_test.py
└── requirements.txt
```
