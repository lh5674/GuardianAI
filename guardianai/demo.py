"""Run the GuardianAI single-camera fall candidate demo."""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .detector import FallDetector, PoseObservation


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="GuardianAI 单摄像头跌倒候选事件 Demo")
    parser.add_argument("--source", default="0", help="摄像头编号、视频文件或 RTSP 地址")
    parser.add_argument("--model", default="yolo26n-pose.pt", help="YOLO 姿态模型路径或名称")
    parser.add_argument("--camera-id", default="demo-camera", help="事件中的摄像头代号")
    parser.add_argument("--events", type=Path, default=Path("events.jsonl"), help="本地 JSONL 事件文件")
    parser.add_argument("--show", action="store_true", help="显示实时预览窗口；按 q 退出")
    parser.add_argument("--hold-seconds", type=float, default=1.0, help="横卧姿态持续时间")
    parser.add_argument("--cooldown-seconds", type=float, default=30.0, help="同一轨迹告警冷却时间")
    return parser.parse_args(argv)


def _open_source(source: str):
    import cv2

    return cv2.VideoCapture(int(source) if source.isdecimal() else source)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError as exc:
        print(f"缺少运行依赖：{exc}。请先安装 requirements.txt。", file=sys.stderr)
        return 2

    capture = _open_source(args.source)
    if not capture.isOpened():
        print("无法打开视频源，请检查摄像头编号、文件路径或 RTSP 连接。", file=sys.stderr)
        return 2
    try:
        model = YOLO(args.model)
    except Exception as exc:
        capture.release()
        print(f"无法加载姿态模型：{exc}", file=sys.stderr)
        return 2
    detector = FallDetector(hold_seconds=args.hold_seconds, cooldown_seconds=args.cooldown_seconds)
    is_file = not args.source.isdecimal() and not args.source.lower().startswith(("rtsp://", "http://", "https://"))
    fps = capture.get(cv2.CAP_PROP_FPS) or 0
    frame_index = 0
    args.events.parent.mkdir(parents=True, exist_ok=True)
    print(f"开始分析 {args.camera_id}；事件写入 {args.events}。按 Ctrl+C 停止。")
    try:
        with args.events.open("a", encoding="utf-8") as event_file:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                frame_index += 1
                # Recorded video uses video time, so a fast CPU does not alter hold durations.
                timestamp = frame_index / fps if is_file and fps > 0 else time.monotonic()
                try:
                    result = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
                except Exception as exc:
                    print(f"姿态推理失败：{exc}", file=sys.stderr)
                    return 1
                if result.boxes is not None and result.boxes.id is not None and result.keypoints is not None:
                    ids = result.boxes.id.int().cpu().tolist()
                    boxes = result.boxes.xyxy.cpu().tolist()
                    points = result.keypoints.data.cpu().tolist()
                    for track_id, box, keypoints in zip(ids, boxes, points):
                        observation = PoseObservation.from_keypoints(keypoints, box, frame.shape[0])
                        if detector.update(track_id, timestamp, observation):
                            event = {
                                "event_id": str(uuid.uuid4()),
                                "event_type": "suspected_fall",
                                "occurred_at": datetime.now(timezone.utc).isoformat(),
                                "camera_id": args.camera_id,
                                "track_id": track_id,
                                "model": args.model,
                                "decision": "upright_to_horizontal_with_hip_drop_and_hold",
                                "review_status": "pending",
                            }
                            event_file.write(json.dumps(event, ensure_ascii=False) + "\n")
                            event_file.flush()
                            print(f"疑似跌倒，请人工核查：{event['occurred_at']} track={track_id} event={event['event_id']}")
                detector.prune(timestamp)
                if args.show:
                    cv2.imshow("GuardianAI Demo", result.plot())
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
    except KeyboardInterrupt:
        pass
    finally:
        capture.release()
        if args.show:
            cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

