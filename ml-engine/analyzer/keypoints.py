"""COCO-17 keypoint definitions used by YOLOv8-pose."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class KeypointIndex(IntEnum):
    NOSE = 0
    LEFT_EYE = 1
    RIGHT_EYE = 2
    LEFT_EAR = 3
    RIGHT_EAR = 4
    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_ELBOW = 7
    RIGHT_ELBOW = 8
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16


@dataclass(frozen=True)
class KeypointName:
    index: int
    label: str
    group: str


KEYPOINTS: tuple[KeypointName, ...] = (
    KeypointName(0, "head", "head"),
    KeypointName(1, "left_eye", "head"),
    KeypointName(2, "right_eye", "head"),
    KeypointName(3, "left_ear", "head"),
    KeypointName(4, "right_ear", "head"),
    KeypointName(5, "left_shoulder", "shoulders"),
    KeypointName(6, "right_shoulder", "shoulders"),
    KeypointName(7, "left_elbow", "arms"),
    KeypointName(8, "right_elbow", "arms"),
    KeypointName(9, "left_wrist", "arms"),
    KeypointName(10, "right_wrist", "arms"),
    KeypointName(11, "left_hip", "hips"),
    KeypointName(12, "right_hip", "hips"),
    KeypointName(13, "left_knee", "legs"),
    KeypointName(14, "right_knee", "legs"),
    KeypointName(15, "left_ankle", "legs"),
    KeypointName(16, "right_ankle", "legs"),
)

# Pairs for skeleton rendering and distance metrics
SKELETON_CONNECTIONS: tuple[tuple[int, int], ...] = (
    (0, 1), (0, 2), (1, 3), (2, 4),
    (5, 6),
    (5, 7), (7, 9),
    (6, 8), (8, 10),
    (5, 11), (6, 12),
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),
)

DISTANCE_PAIRS: tuple[tuple[int, int, str], ...] = (
    (5, 6, "shoulder_width"),
    (11, 12, "hip_width"),
    (0, 5, "head_to_left_shoulder"),
    (0, 6, "head_to_right_shoulder"),
    (5, 7, "left_upper_arm"),
    (7, 9, "left_forearm"),
    (6, 8, "right_upper_arm"),
    (8, 10, "right_forearm"),
    (5, 11, "left_torso"),
    (6, 12, "right_torso"),
    (11, 13, "left_thigh"),
    (13, 15, "left_shin"),
    (12, 14, "right_thigh"),
    (14, 16, "right_shin"),
    (15, 16, "ankle_width"),
)

ANGLE_TRIPLETS: tuple[tuple[int, int, int, str], ...] = (
    (5, 7, 9, "left_elbow"),
    (6, 8, 10, "right_elbow"),
    (11, 13, 15, "left_knee"),
    (12, 14, 16, "right_knee"),
    (7, 5, 11, "left_shoulder"),
    (8, 6, 12, "right_shoulder"),
)

TRAIL_JOINTS: tuple[int, ...] = (0, 9, 10, 15, 16)  # head, wrists, ankles
