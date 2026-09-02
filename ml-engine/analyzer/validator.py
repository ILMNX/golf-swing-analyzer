"""Pre-analysis video quality and pose visibility checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config
from analyzer.exceptions import ValidationError
from analyzer.pose import PoseExtractor
from analyzer.video_io import (
    VideoMeta,
    measure_sharpness,
    read_sample_frames,
    sample_frame_indices,
    validate_video_meta,
)


@dataclass(frozen=True)
class ValidationReport:
    sharpness: float
    visible_keypoint_ratio: float
    person_height_ratio: float
    sampled_frames: int
    poses_detected: int


def validate_video(path: str, meta: VideoMeta, pose_extractor: PoseExtractor) -> ValidationReport:
    validate_video_meta(meta)

    indices = sample_frame_indices(meta.frame_count, config.VALIDATION_SAMPLE_FRAMES)
    frames = read_sample_frames(path, indices)

    if not frames:
        raise ValidationError("Tidak dapat membaca frame dari video.", code="empty_video")

    sharpness_values = [measure_sharpness(f) for f in frames]
    avg_sharpness = float(np.mean(sharpness_values))
    if avg_sharpness < config.MIN_SHARPNESS:
        raise ValidationError(
            "Video terlalu buram. Pastikan fokus kamera tajam dan pencahayaan cukup.",
            code="video_blurry",
        )

    visible_ratios: list[float] = []
    height_ratios: list[float] = []
    poses_found = 0

    for frame in frames:
        pose = pose_extractor.detect(frame)
        if pose is None:
            continue
        poses_found += 1
        visible_ratios.append(PoseExtractor.visible_ratio(pose))
        height_ratios.append(PoseExtractor.person_height_ratio(pose, meta.height))

    if poses_found == 0:
        raise ValidationError(
            "Tidak terdeteksi tubuh manusia dalam video. Pastikan golfer terlihat penuh di frame.",
            code="no_person_detected",
        )

    avg_visible = float(np.mean(visible_ratios))
    if avg_visible < config.MIN_VISIBLE_KEYPOINT_RATIO:
        raise ValidationError(
            "Terlalu banyak sendi tidak terlihat. Perbaiki sudut kamera — rekam dari samping dengan tubuh penuh.",
            code="poor_pose_visibility",
        )

    avg_height = float(np.mean(height_ratios))
    if avg_height < config.MIN_PERSON_HEIGHT_RATIO:
        raise ValidationError(
            "Golfer terlalu kecil dalam frame. Dekatkan kamera atau zoom agar tubuh memenuhi minimal 25% frame.",
            code="subject_too_small",
        )

    # Side-view heuristic: shoulders and hips should both be reasonably visible
    side_scores = []
    for frame in frames:
        pose = pose_extractor.detect(frame)
        if pose is None:
            continue
        kp = pose.keypoints
        left_shoulder = kp[5, 2]
        right_shoulder = kp[6, 2]
        left_hip = kp[11, 2]
        right_hip = kp[12, 2]
        side_scores.append(
            min(left_shoulder, right_shoulder, left_hip, right_hip) >= config.MIN_POSE_CONFIDENCE
        )

    if side_scores and float(np.mean(side_scores)) < 0.4:
        raise ValidationError(
            "Sudut kamera kurang ideal. Rekam dari samping (face-on atau down-the-line) dengan bahu dan pinggul terlihat.",
            code="bad_camera_angle",
        )

    return ValidationReport(
        sharpness=avg_sharpness,
        visible_keypoint_ratio=avg_visible,
        person_height_ratio=avg_height,
        sampled_frames=len(frames),
        poses_detected=poses_found,
    )
