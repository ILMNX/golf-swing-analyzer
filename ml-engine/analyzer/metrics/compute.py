"""Metric computation from pose sequences."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import config
from analyzer.keypoints import ANGLE_TRIPLETS, DISTANCE_PAIRS, KeypointIndex
from analyzer.pose import FramePose, PoseExtractor


def _valid_point(kp: np.ndarray, idx: int) -> bool:
    return float(kp[idx, 2]) >= config.MIN_POSE_CONFIDENCE


def _point(kp: np.ndarray, idx: int) -> np.ndarray | None:
    if not _valid_point(kp, idx):
        return None
    return kp[idx, :2]


def _distance(p1: np.ndarray, p2: np.ndarray) -> float:
    return float(np.linalg.norm(p1 - p2))


def _angle_deg(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Angle at point b formed by a-b-c."""
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = float(np.clip(cosine, -1.0, 1.0))
    return math.degrees(math.acos(cosine))


def _stat(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "std": 0.0}
    arr = np.array(values, dtype=float)
    return {
        "min": float(arr.min()),
        "max": float(arr.max()),
        "avg": float(arr.mean()),
        "std": float(arr.std()),
    }


def compute_frame_distances(kp: np.ndarray) -> dict[str, float]:
    distances: dict[str, float] = {}
    for i, j, name in DISTANCE_PAIRS:
        p1, p2 = _point(kp, i), _point(kp, j)
        if p1 is not None and p2 is not None:
            distances[name] = _distance(p1, p2)
    return distances


def compute_frame_angles(kp: np.ndarray) -> dict[str, float]:
    angles: dict[str, float] = {}
    for a, b, c, name in ANGLE_TRIPLETS:
        pa, pb, pc = _point(kp, a), _point(kp, b), _point(kp, c)
        if pa is not None and pb is not None and pc is not None:
            angles[name] = _angle_deg(pa, pb, pc)
    return angles


def compute_head_metrics(poses: list[FramePose]) -> dict[str, Any]:
    xs, ys = [], []
    for pose in poses:
        pt = _point(pose.keypoints, KeypointIndex.NOSE)
        if pt is not None:
            xs.append(float(pt[0]))
            ys.append(float(pt[1]))

    if not xs:
        return {"stability_score": 0, "lateral_movement_px": 0, "vertical_movement_px": 0}

    lateral = max(xs) - min(xs)
    vertical = max(ys) - min(ys)
    # Lower movement = higher stability (normalize heuristically)
    stability = max(0, 100 - int((lateral + vertical) / 4))

    return {
        "stability_score": stability,
        "lateral_movement_px": round(lateral, 1),
        "vertical_movement_px": round(vertical, 1),
    }


def compute_shoulder_metrics(poses: list[FramePose]) -> dict[str, Any]:
    widths, tilts = [], []
    for pose in poses:
        ls, rs = _point(pose.keypoints, 5), _point(pose.keypoints, 6)
        if ls is not None and rs is not None:
            widths.append(_distance(ls, rs))
            tilts.append(abs(float(ls[1] - rs[1])))

    width_stats = _stat(widths)
    tilt_stats = _stat(tilts)
    level_score = max(0, 100 - int(tilt_stats["avg"] * 2))

    return {
        "width_px": width_stats,
        "tilt_px": tilt_stats,
        "level_score": level_score,
        "rotation_range_px": round(width_stats["max"] - width_stats["min"], 1),
    }


def compute_hip_metrics(poses: list[FramePose]) -> dict[str, Any]:
    widths = []
    for pose in poses:
        lh, rh = _point(pose.keypoints, 11), _point(pose.keypoints, 12)
        if lh is not None and rh is not None:
            widths.append(_distance(lh, rh))

    stats = _stat(widths)
    return {
        "width_px": stats,
        "rotation_range_px": round(stats["max"] - stats["min"], 1),
    }


def compute_arm_metrics(poses: list[FramePose]) -> dict[str, Any]:
    left_elbow, right_elbow = [], []
    left_wrist_y, right_wrist_y = [], []

    for pose in poses:
        angles = compute_frame_angles(pose.keypoints)
        if "left_elbow" in angles:
            left_elbow.append(angles["left_elbow"])
        if "right_elbow" in angles:
            right_elbow.append(angles["right_elbow"])

        lw = _point(pose.keypoints, 9)
        rw = _point(pose.keypoints, 10)
        if lw is not None:
            left_wrist_y.append(float(lw[1]))
        if rw is not None:
            right_wrist_y.append(float(rw[1]))

    return {
        "left_elbow_angle_deg": _stat(left_elbow),
        "right_elbow_angle_deg": _stat(right_elbow),
        "left_wrist_travel_px": round(max(left_wrist_y) - min(left_wrist_y), 1) if left_wrist_y else 0,
        "right_wrist_travel_px": round(max(right_wrist_y) - min(right_wrist_y), 1) if right_wrist_y else 0,
    }


def compute_leg_metrics(poses: list[FramePose]) -> dict[str, Any]:
    left_knee, right_knee = [], []
    stance_widths = []

    for pose in poses:
        angles = compute_frame_angles(pose.keypoints)
        if "left_knee" in angles:
            left_knee.append(angles["left_knee"])
        if "right_knee" in angles:
            right_knee.append(angles["right_knee"])

        la, ra = _point(pose.keypoints, 15), _point(pose.keypoints, 16)
        if la is not None and ra is not None:
            stance_widths.append(_distance(la, ra))

    return {
        "left_knee_angle_deg": _stat(left_knee),
        "right_knee_angle_deg": _stat(right_knee),
        "stance_width_px": _stat(stance_widths),
    }


def compute_joint_distances(poses: list[FramePose]) -> dict[str, dict[str, float]]:
    series: dict[str, list[float]] = {name: [] for _, _, name in DISTANCE_PAIRS}

    for pose in poses:
        frame_dist = compute_frame_distances(pose.keypoints)
        for name, value in frame_dist.items():
            series[name].append(value)

    return {name: _stat(values) for name, values in series.items() if values}


def compute_joint_angles(poses: list[FramePose]) -> dict[str, dict[str, float]]:
    series: dict[str, list[float]] = {name: [] for *_, name in ANGLE_TRIPLETS}

    for pose in poses:
        frame_angles = compute_frame_angles(pose.keypoints)
        for name, value in frame_angles.items():
            series[name].append(value)

    return {name: _stat(values) for name, values in series.items() if values}


def compute_summary_scores(
    head: dict,
    shoulders: dict,
    hips: dict,
    arms: dict,
    legs: dict,
) -> dict[str, int]:
    tempo = min(100, int(arms["right_wrist_travel_px"] / 3 + 50))
    posture = shoulders["level_score"]
    rotation = min(100, int(shoulders["rotation_range_px"] + hips["rotation_range_px"]))
    balance = min(100, int(legs["stance_width_px"]["std"] * -2 + 85))

    return {
        "tempo": max(0, min(100, tempo)),
        "posture": max(0, min(100, posture)),
        "rotation": max(0, min(100, rotation)),
        "balance": max(0, min(100, balance)),
        "head_stability": head["stability_score"],
    }


def compute_all_metrics(poses: list[FramePose]) -> dict[str, Any]:
    valid_poses = [p for p in poses if PoseExtractor.visible_ratio(p) > 0.3]
    if not valid_poses:
        valid_poses = poses

    head = compute_head_metrics(valid_poses)
    shoulders = compute_shoulder_metrics(valid_poses)
    hips = compute_hip_metrics(valid_poses)
    arms = compute_arm_metrics(valid_poses)
    legs = compute_leg_metrics(valid_poses)
    distances = compute_joint_distances(valid_poses)
    angles = compute_joint_angles(valid_poses)
    summary = compute_summary_scores(head, shoulders, hips, arms, legs)

    return {
        "summary": summary,
        "head": head,
        "shoulders": shoulders,
        "hips": hips,
        "arms": arms,
        "legs": legs,
        "joint_distances": distances,
        "joint_angles": angles,
        "frames_analyzed": len(valid_poses),
    }
