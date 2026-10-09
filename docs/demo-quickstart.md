# GuardianAI 跌倒检测 Demo：运行说明

此版本为**单摄像头研究原型**。它用 YOLO Pose 提取 17 个人体关键点，并用 ByteTrack 维持轨迹；当同一轨迹先出现站立、随后髋部向画面下方移动并保持横卧姿态时，生成一条待人工核查的疑似跌倒事件。阈值是演示默认值，未经养老场景数据校准。

## 安装与运行

建议使用 Python 3.10 或更新版本。在仓库根目录执行：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m guardianai.demo --source sample.mp4 --show
```

摄像头可用 `--source 0`；RTSP 视频流可用 `--source "rtsp://..."`。请勿把含密码的地址保存到仓库、截图或日志中。默认模型 `yolo26n-pose.pt` 在首次运行时可能需要联网下载。若已有本地模型，用 `--model 模型文件路径` 指定。

事件默认追加写入运行目录下的 `events.jsonl`，只含事件编号、UTC 时间、摄像头代号、临时轨迹号、模型名称、判定说明及待核查状态；程序不保存视频帧。`--events` 可指定其他位置。`--show` 才显示画面预览。文件结束或按 `q` / `Ctrl+C` 停止。

```bash
python -m guardianai.demo --source 0 --camera-id room-demo --events local/events.jsonl
python -m unittest discover -s tests -v
```

## 目前的边界

- 本版使用可解释的姿态与时间规则，**尚无经过训练的 GRU/TCN 模型**，也未实现双视角融合、步态风险评估、个性化模型或远程告警。
- 需要连续可见的站立到横卧轨迹；遮挡、轨迹重置、摄像头角度变化、坐下或躺床等都可能造成漏报或误报。未观察到站立起点时不会报警。
- 事件仅在本机写入 JSONL 并打印提示；需由人员复核。不能替代护理巡视、紧急呼叫或医疗设备。
- 接入真实场地前需确认安装区域、取得授权、设定数据保留与访问权限；不要把原始视频、事件文件、模型密钥或个人资料提交至公开仓库。

## 技术依据

- [Ultralytics Pose 文档](https://docs.ultralytics.com/tasks/pose/)：关键点和输出字段。
- [Ultralytics Tracking 文档](https://docs.ultralytics.com/modes/track/)：Pose 追踪、`persist=True` 与轨迹 ID。

