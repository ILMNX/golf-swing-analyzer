"""Pre-analysis video quality and pose visibility checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config
from analyzer.exceptions import ValidationError
from analyzer.pose import PoseExtractor
from analyzer.tuning.schema import ValidationTuning
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


def validate_video(
    path: str,
    meta: VideoMeta,
    pose_extractor: PoseExtractor,
    tuning: ValidationTuning | None = None,
) -> ValidationReport:
    vt = tuning or ValidationTuning(
        min_sharpness=config.MIN_SHARPNESS,
        min_pose_confidence=config.MIN_POSE_CONFIDENCE,
        min_visible_keypoint_ratio=config.MIN_VISIBLE_KEYPOINT_RATIO,
        min_person_height_ratio=config.MIN_PERSON_HEIGHT_RATIO,
        min_side_view_score=0.4,
        validation_sample_frames=config.VALIDATION_SAMPLE_FRAMES,
    )

    validate_video_meta(meta)

    indices = sample_frame_indices(meta.frame_count, vt.validation_sample_frames)
    frames = read_sample_frames(path, indices)

    if not frames:
        raise ValidationError("Tidak dapat membaca frame dari video.", code="empty_video")

    sharpness_values = [measure_sharpness(f) for f in frames]
    avg_sharpness = float(np.mean(sharpness_values))
    if avg_sharpness < vt.min_sharpness:
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
        visible_ratios.append(PoseExtractor.visible_ratio(pose, vt.min_pose_confidence))
        height_ratios.append(PoseExtractor.person_height_ratio(pose, meta.height))

    if poses_found == 0:
        raise ValidationError(
            "Tidak terdeteksi tubuh manusia dalam video. Pastikan golfer terlihat penuh di frame.",
            code="no_person_detected",
        )

    avg_visible = float(np.mean(visible_ratios))
    if avg_visible < vt.min_visible_keypoint_ratio:
        raise ValidationError(
            "Terlalu banyak sendi tidak terlihat. Perbaiki sudut kamera — rekam dari samping dengan tubuh penuh.",
            code="poor_pose_visibility",
        )

    avg_height = float(np.mean(height_ratios))
    if avg_height < vt.min_person_height_ratio:
        raise ValidationError(
            "Golfer terlalu kecil dalam frame. Dekatkan kamera atau zoom agar tubuh memenuhi frame.",
            code="subject_too_small",
        )

    side_scores = []
    for frame in frames:
        pose = pose_extractor.detect(frame)
        if pose is None:
            continue
        kp = pose.keypoints
        side_scores.append(
            min(kp[5, 2], kp[6, 2], kp[11, 2], kp[12, 2]) >= vt.min_pose_confidence
        )

    if side_scores and float(np.mean(side_scores)) < vt.min_side_view_score:
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
