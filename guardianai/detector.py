"""Conservative, explainable fall candidate detection from tracked poses.

This is a demonstration baseline, not a trained temporal classifier. It requires
an observed upright-to-horizontal transition and a sustained horizontal pose.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees


@dataclass(frozen=True)
class PoseObservation:
    torso_angle_deg: float
    box_aspect: float
    hip_y_fraction: float
    keypoint_quality: float

    @classmethod
    def from_keypoints(cls, keypoints, box, frame_height: int, minimum_confidence: float = 0.35):
        """Read one COCO-17 pose. Return None when core joints are uncertain."""
        if len(keypoints) < 13 or frame_height <= 0:
            return None
        core = [5, 6, 11, 12]  # shoulders and hips
        for index in core:
            point = keypoints[index]
            if len(point) < 3 or float(point[2]) < minimum_confidence:
                return None
        shoulder_x = (float(keypoints[5][0]) + float(keypoints[6][0])) / 2
        shoulder_y = (float(keypoints[5][1]) + float(keypoints[6][1])) / 2
        hip_x = (float(keypoints[11][0]) + float(keypoints[12][0])) / 2
        hip_y = (float(keypoints[11][1]) + float(keypoints[12][1])) / 2
        width = max(float(box[2]) - float(box[0]), 1.0)
        height = max(float(box[3]) - float(box[1]), 1.0)
        return cls(
            torso_angle_deg=degrees(atan2(abs(shoulder_x - hip_x), abs(shoulder_y - hip_y))),
            box_aspect=width / height,
            hip_y_fraction=hip_y / frame_height,
            keypoint_quality=min(float(keypoints[i][2]) for i in core),
        )


@dataclass
class _TrackState:
    last_seen: float
    upright_at: float | None = None
    upright_hip_y: float | None = None
    horizontal_since: float | None = None
    last_alert_at: float = float("-inf")


class FallDetector:
    def __init__(self, hold_seconds: float = 1.0, transition_seconds: float = 4.0,
                 cooldown_seconds: float = 30.0, minimum_hip_drop: float = 0.08):
        if hold_seconds <= 0 or transition_seconds <= 0 or cooldown_seconds < 0:
            raise ValueError("Time settings must be positive (cooldown may be zero)")
        self.hold_seconds = hold_seconds
        self.transition_seconds = transition_seconds
        self.cooldown_seconds = cooldown_seconds
        self.minimum_hip_drop = minimum_hip_drop
        self.tracks: dict[int, _TrackState] = {}

    def update(self, track_id: int, timestamp: float, pose: PoseObservation | None) -> bool:
        """Return True once for a newly confirmed fall candidate."""
        state = self.tracks.setdefault(track_id, _TrackState(last_seen=timestamp))
        state.last_seen = timestamp
        if pose is None:
            state.horizontal_since = None
            return False
        upright = pose.torso_angle_deg <= 30 and pose.box_aspect <= 0.9
        horizontal = pose.torso_angle_deg >= 55 and pose.box_aspect >= 1.05
        if upright:
            state.upright_at = timestamp
            state.upright_hip_y = pose.hip_y_fraction
            state.horizontal_since = None
            return False
        if not horizontal:
            state.horizontal_since = None
            return False
        if state.horizontal_since is None:
            state.horizontal_since = timestamp
        if state.upright_at is None or state.upright_hip_y is None:
            return False
        transitioned_recently = timestamp - state.upright_at <= self.transition_seconds
        held = timestamp - state.horizontal_since >= self.hold_seconds
        moved_down = pose.hip_y_fraction - state.upright_hip_y >= self.minimum_hip_drop
        cooled = timestamp - state.last_alert_at >= self.cooldown_seconds
        if transitioned_recently and held and moved_down and cooled:
            state.last_alert_at = timestamp
            state.upright_at = None  # prevent repeated alerts without another upright pose
            return True
        return False

    def prune(self, timestamp: float, max_missing_seconds: float = 10.0) -> None:
        for track_id in list(self.tracks):
            if timestamp - self.tracks[track_id].last_seen > max_missing_seconds:
                del self.tracks[track_id]

