# 手部跟随桌面机械臂（Gesture Arm）

低成本入门具身智能项目：真摄像头跟踪手部 → 统一控制接口 → **仿真臂跟随**（真机后置）。

## 路径策略

**仿真臂练控制与进阶 + 真摄像头练跟随感知 → 接口统一 → 真机后置 →（可选）端侧**

完整设计见：[docs/DESIGN.md](./docs/DESIGN.md)

## 环境

```bash
cd gesture-arm
python -m pip install -r requirements.txt
```

## 阶段 0：Backend 冒烟

```bash
python tools/backend_smoke_test.py
```

## 阶段 1：真摄像头手部跟踪

首次运行若缺少模型，会自动下载到 `models/hand_landmarker.task`（也可预先放好）。

可调参数集中在 [`config.yaml`](./config.yaml)，改完直接重跑即可。

```bash
python -m pc.app_main
python -m pc.app_main --config config.yaml
```

CLI 可临时覆盖配置：

```bash
python -m pc.app_main --camera 0
python -m pc.app_main --follow wrist
python -m pc.app_main --verbose-backend
```

快捷键：

| 键 | 作用 |
|----|------|
| `Q` / `Esc` | 退出 |
| `Space` | ENABLE / DISABLE |
| `F` | 切换跟随点（指尖 / 手腕） |

验收：画面显示骨架与 HUD；手进出画面时 `STATUS` 在 `TRACKING` / `LOST` 间切换；跟踪时 HUD 中 `J,...` 随手变化。

## 当前状态

- [x] 设计方案（v0.3）
- [x] 阶段 0：ArmBackend + ConsoleBackend
- [x] 阶段 1：真摄像头手部跟踪 → ConsoleBackend
- [ ] 阶段 2：PyBullet 仿真臂接入同一接口
- [ ] 阶段 3：手部跟随仿真闭环
- [ ] 阶段 4：控制进阶
- [ ] 阶段 5：真机后置接入
- [ ] 阶段 6：端侧迁移（可选）
