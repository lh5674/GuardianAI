# GuardianAI

GuardianAI 是面向养老场景的计算机视觉跌倒检测研究项目。仓库目前为**公开仓库**，包含单摄像头跌倒候选事件 Demo、技术架构、人民币硬件预算与研发任务清单。

## 跌倒检测 Demo

运行说明：[单摄像头 Demo](docs/demo-quickstart.md)

```bash
python -m pip install -r requirements.txt
python -m guardianai.demo --source sample.mp4 --show
```

Demo 从视频提取 YOLO Pose 关键点并跟踪人物，以连续帧姿态规则生成本地 `events.jsonl` 疑似跌倒事件。它尚未接入训练后的 GRU/TCN、双视角融合或远程告警；不应作为已通过现场验证的照护产品使用。

## 项目资料

- [技术架构书](docs/architecture.md)
- [Demo 硬件采购预算（人民币）](planning/hardware-procurement.csv)
- [研发任务看板](planning/rd-board.csv)

采购预算以 2026 年 10 月 9 日人民币兑美元中间价 1 USD = 6.7330 CNY 换算。除 NVIDIA 开发套件官方参考价外，其他单价是内部规划估算，非供应商报价。在线表格导入后应以其中的可调汇率和预算公式为准。

飞书协作链接将在完成导入和权限核对后补入。不要向本公开仓库提交真实视频、住户个人资料、事件文件或密钥。

## 研发方向

后续按架构书引入标注数据、GRU/TCN 时序模型、多视角遮挡处理、边缘部署与告警闭环。步态风险评估与个性化行为模型作为研究原型单独验证。

