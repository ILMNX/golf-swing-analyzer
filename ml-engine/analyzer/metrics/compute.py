"""Metric computation from pose sequences — delegates to GolfBiomechanicsAnalyzer."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from analyzer.club_track import ClubTrackResult, refine_phases_with_club, score_club_tracking
from analyzer.keypoints import ANGLE_TRIPLETS, DISTANCE_PAIRS
from analyzer.metrics.biomechanics import (
    BIOMECHANICS_MIN_CONFIDENCE,
    GolfBiomechanicsAnalyzer,
    SwingPhases,
    biomechanics_to_dict,
    biomechanics_to_summary,
)
from analyzer.pose import FramePose, PoseExtractor
from analyzer.tuning.schema import TuningProfile


def _valid_point(kp: np.ndarray, idx: int, min_conf: float) -> bool:
    return float(kp[idx, 2]) >= min_conf


def _point(kp: np.ndarray, idx: int, min_conf: float) -> np.ndarray | None:
    if not _valid_point(kp, idx, min_conf):
        return None
    return kp[idx, :2]


def _distance(p1: np.ndarray, p2: np.ndarray) -> float:
    return float(np.linalg.norm(p1 - p2))


def _angle_deg(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
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


def compute_frame_distances(kp: np.ndarray, min_conf: float) -> dict[str, float]:
    distances: dict[str, float] = {}
    for i, j, name in DISTANCE_PAIRS:
        p1, p2 = _point(kp, i, min_conf), _point(kp, j, min_conf)
        if p1 is not None and p2 is not None:
            distances[name] = _distance(p1, p2)
    return distances


def compute_frame_angles(kp: np.ndarray, min_conf: float) -> dict[str, float]:
    angles: dict[str, float] = {}
    for a, b, c, name in ANGLE_TRIPLETS:
        pa, pb, pc = _point(kp, a, min_conf), _point(kp, b, min_conf), _point(kp, c, min_conf)
        if pa is not None and pb is not None and pc is not None:
            angles[name] = _angle_deg(pa, pb, pc)
    return angles


def compute_joint_distances(poses: list[FramePose], min_conf: float) -> dict[str, dict[str, float]]:
    series: dict[str, list[float]] = {name: [] for _, _, name in DISTANCE_PAIRS}
    for pose in poses:
        frame_dist = compute_frame_distances(pose.keypoints, min_conf)
        for name, value in frame_dist.items():
            series[name].append(value)
    return {name: _stat(values) for name, values in series.items() if values}


def compute_joint_angles(poses: list[FramePose], min_conf: float) -> dict[str, dict[str, float]]:
    series: dict[str, list[float]] = {name: [] for *_, name in ANGLE_TRIPLETS}
    for pose in poses:
        frame_angles = compute_frame_angles(pose.keypoints, min_conf)
        for name, value in frame_angles.items():
            series[name].append(value)
    return {name: _stat(values) for name, values in series.items() if values}


def _pack_metrics(
    bio,
    summary: dict[str, int],
    valid_poses: list[FramePose],
    profile: TuningProfile | None,
    fps: float | None,
    club: ClubTrackResult | None = None,
) -> dict[str, Any]:
    min_conf = BIOMECHANICS_MIN_CONFIDENCE
    payload: dict[str, Any] = {
        "summary": summary,
        "biomechanics": biomechanics_to_dict(bio),
        "posture": {
            "spine_angle_address_deg": bio.spine_angle_address_deg,
            "spine_angle_impact_deg": bio.spine_angle_impact_deg,
            "spine_angle_retention_deg": bio.spine_angle_retention_deg,
        },
        "head": {
            "stability_score": summary["head_stability"],
            "movement_normalized": bio.head_movement_normalized,
            "lateral_range_px": bio.head_lateral_range_px,
            "vertical_range_px": bio.head_vertical_range_px,
            "reference_shoulder_width_px": bio.address_shoulder_width,
        },
        "rotation": {
            "shoulder_rotation_max_deg": bio.shoulder_rotation_max_deg,
            "hip_rotation_max_deg": bio.hip_rotation_max_deg,
            "x_factor_deg": bio.x_factor_deg,
        },
        "tempo": {
            "ratio": bio.tempo_ratio,
            "confidence": bio.tempo_confidence,
            "backswing_frames": bio.backswing_frames,
            "downswing_frames": bio.downswing_frames,
            "top_frame": bio.top_frame,
            "impact_frame": bio.impact_frame,
            "address_frame": bio.address_frame,
        },
        "balance": {
            "sway_px": bio.hip_sway_px,
            "sway_normalized": bio.hip_sway_normalized,
        },
        "arms": {
            "lead_arm_straightness_impact_deg": bio.lead_arm_straightness_impact_deg,
            "handedness": bio.handedness,
        },
        "quality": {
            "detection_quality": bio.detection_quality,
            "min_keypoint_confidence": min_conf,
            "tempo_confidence": bio.tempo_confidence,
            "low_fps_warning": bool(fps is not None and fps < 45.0),
        },
        "joint_distances": compute_joint_distances(valid_poses, min_conf),
        "joint_angles": compute_joint_angles(valid_poses, min_conf),
        "frames_analyzed": len(valid_poses),
        "metrics_focus": list(profile.metrics_focus) if profile else [],
    }

    if club is not None:
        club_score = score_club_tracking(club)
        wrist_impact = getattr(club, "_wrist_impact_before_refine", bio.impact_frame)
        payload["club"] = {
            **club.to_dict(),
            "tracking_score": club_score,
            "wrist_impact_frame": wrist_impact,
            "club_impact_frame": club.impact_frame_hint,
            "impact_refined": bool(
                club.impact_frame_hint is not None
                and abs(int(wrist_impact) - bio.impact_frame) >= 1
            ),
            "final_impact_frame": bio.impact_frame,
        }
        if club.impact_frame_hint is not None and abs(int(wrist_impact) - bio.impact_frame) >= 1:
            payload["tempo"]["impact_source"] = "club_tip"
        else:
            payload["tempo"]["impact_source"] = "wrist"

    return payload


def compute_all_metrics(
    poses: list[FramePose],
    profile: TuningProfile | None = None,
    phase_hints: SwingPhases | None = None,
    fps: float | None = None,
    club: ClubTrackResult | None = None,
) -> dict[str, Any]:
    valid_poses = [p for p in poses if PoseExtractor.visible_ratio(p) > 0.3]
    if not valid_poses:
        valid_poses = [p for p in poses if p is not None]

    analyzer = GolfBiomechanicsAnalyzer(valid_poses, fps=fps)
    bio = analyzer.analyze(phase_hints=phase_hints)

    if club is not None and club.impact_frame_hint is not None:
        wrist_impact = bio.phases.impact
        refined = refine_phases_with_club(bio.phases, club)
        if refined.impact != bio.phases.impact:
            bio = analyzer.reanalyze_with_phases(refined)
            if club.mean_confidence >= 0.35 and club.detection_rate >= 0.2:
                bio.tempo_confidence = round(min(1.0, bio.tempo_confidence + 0.08), 3)
        club._wrist_impact_before_refine = wrist_impact  # type: ignore[attr-defined]

    summary = biomechanics_to_summary(bio)
    return _pack_metrics(bio, summary, valid_poses, profile, fps, club=club)
