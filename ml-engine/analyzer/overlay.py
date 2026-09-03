"""Draw skeleton overlay, club shaft (red), and motion trails on video frames."""

from __future__ import annotations

from collections import deque

import cv2
import numpy as np

import config
from analyzer.club_track import ClubFrameTrack
from analyzer.keypoints import SKELETON_CONNECTIONS, TRAIL_JOINTS
from analyzer.pose import FramePose


def _draw_joint(frame: np.ndarray, x: float, y: float, conf: float) -> None:
    if conf < config.MIN_POSE_CONFIDENCE:
        return
    cv2.circle(frame, (int(x), int(y)), config.JOINT_RADIUS, config.COLOR_JOINT, -1, cv2.LINE_AA)


def draw_pose(frame: np.ndarray, pose: FramePose, trails: dict[int, deque]) -> np.ndarray:
    output = frame.copy()
    kp = pose.keypoints

    for i, j in SKELETON_CONNECTIONS:
        if kp[i, 2] < config.MIN_POSE_CONFIDENCE or kp[j, 2] < config.MIN_POSE_CONFIDENCE:
            continue
        pt1 = (int(kp[i, 0]), int(kp[i, 1]))
        pt2 = (int(kp[j, 0]), int(kp[j, 1]))
        cv2.line(output, pt1, pt2, config.COLOR_SKELETON, config.SKELETON_THICKNESS, cv2.LINE_AA)

    for idx in range(kp.shape[0]):
        _draw_joint(output, kp[idx, 0], kp[idx, 1], kp[idx, 2])
        if idx in TRAIL_JOINTS and kp[idx, 2] >= config.MIN_POSE_CONFIDENCE:
            trails[idx].append((int(kp[idx, 0]), int(kp[idx, 1])))

    for idx, points in trails.items():
        for i in range(1, len(points)):
            alpha = i / len(points)
            thickness = max(1, int(2 * alpha))
            cv2.line(output, points[i - 1], points[i], config.COLOR_TRAIL, thickness, cv2.LINE_AA)

    return output


# Only draw measured tips — never Kalman coast / body fallback (those look "ngawur").
_DRAW_CLUB_SOURCES = frozenset({"yolo", "line", "fused"})
_MIN_DRAW_CONF = 0.32


def draw_club(
    frame: np.ndarray,
    track: ClubFrameTrack | None,
    tip_trail: deque,
) -> np.ndarray:
    """Draw red shaft line, tip marker, and tip path trail."""
    if track is None or track.tip_xy is None or track.grip_xy is None:
        return frame
    if track.source not in _DRAW_CLUB_SOURCES or track.confidence < _MIN_DRAW_CONF:
        return frame

    output = frame
    grip = (int(track.grip_xy[0]), int(track.grip_xy[1]))
    tip = (int(track.tip_xy[0]), int(track.tip_xy[1]))

    cv2.line(
        output,
        grip,
        tip,
        config.COLOR_CLUB,
        config.CLUB_SHAFT_THICKNESS,
        cv2.LINE_AA,
    )
    cv2.circle(output, grip, 4, config.COLOR_CLUB, -1, cv2.LINE_AA)
    cv2.circle(output, tip, config.CLUB_TIP_RADIUS, config.COLOR_CLUB_TIP, -1, cv2.LINE_AA)
    cv2.circle(output, tip, config.CLUB_TIP_RADIUS + 2, config.COLOR_CLUB, 1, cv2.LINE_AA)

    tip_trail.append(tip)
    for i in range(1, len(tip_trail)):
        alpha = i / max(len(tip_trail), 1)
        thickness = max(1, int(3 * alpha))
        cv2.line(
            output,
            tip_trail[i - 1],
            tip_trail[i],
            config.COLOR_CLUB_TRAIL,
            thickness,
            cv2.LINE_AA,
        )

    return output


def render_annotated_video(
    input_path: str,
    output_path: str,
    poses: list[FramePose | None],
    meta_width: int,
    meta_height: int,
    meta_fps: float,
    start_frame: int = 0,
    end_frame: int | None = None,
    slow_output_path: str | None = None,
    slowmo_factor: int = 1,
    club_tracks: list[ClubFrameTrack] | None = None,
) -> None:
    from analyzer.video_io import create_video_writer, iter_frames, transcode_for_browser

    writer = create_video_writer(output_path, meta_width, meta_height, meta_fps)
    slow_writer = None
    repeats = max(1, slowmo_factor)
    if slow_output_path and repeats > 1:
        slow_writer = create_video_writer(slow_output_path, meta_width, meta_height, meta_fps)

    trails: dict[int, deque] = {idx: deque(maxlen=20) for idx in TRAIL_JOINTS}
    tip_trail: deque = deque(maxlen=12)

    try:
        for i, frame in enumerate(iter_frames(input_path, start_frame, end_frame)):
            pose = poses[i] if i < len(poses) else None
            if pose is not None:
                frame = draw_pose(frame, pose, trails)

            club = None
            if club_tracks is not None and i < len(club_tracks):
                club = club_tracks[i]
            frame = draw_club(frame, club, tip_trail)

            writer.write(frame)
            if slow_writer is not None:
                for _ in range(repeats):
                    slow_writer.write(frame)
    finally:
        writer.release()
        if slow_writer is not None:
            slow_writer.release()

    transcode_for_browser(output_path)
    if slow_output_path and repeats > 1:
        transcode_for_browser(slow_output_path)
