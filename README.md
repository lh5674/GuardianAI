# GuardianAI

GuardianAI 是面向养老场景的计算机视觉跌倒检测 Demo 项目。本仓库保存技术方案、Demo 采购清单和研发任务的可版本管理副本；在线协作文件保存在受限 Google Drive 文件夹。

## 协作入口

- [Google Drive 团队协作空间](https://drive.google.com/drive/folders/1rgE1cHe3vlAryPAzbp5tH50iRO_qxkWD)
- 技术架构：`docs/architecture.md`
- Demo 硬件采购：`planning/hardware-procurement.csv`
- 研发任务：`planning/rd-board.csv`

Drive 文件夹及本仓库均保持现有受限权限。需由项目所有者指定团队成员邮箱后再授予访问权。

## Demo 目标

边缘设备从摄像头读取视频，使用 YOLO-Pose 提取人体关键点，经时序 GRU 或 TCN 判断跌倒事件。通过多帧确认、人工复核和事件通知完成闭环。步态风险评估、多视角遮挡检测、个性化行为模型作为后续迭代方向。

## 状态

目前为方案与任务规划阶段。硬件报价、供应商、负责人和测试阈值均为待确认项；本仓库不含已完成的产品代码。
