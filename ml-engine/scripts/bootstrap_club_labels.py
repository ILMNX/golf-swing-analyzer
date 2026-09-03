#!/usr/bin/env python3
"""Bootstrap weak clubhead labels from pose + shaft line search (for first train).

Prefer hand annotation for production quality. This script seeds labels so the
YOLO pipeline can be trained/tested on the sample video without manual labeling.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _yolo_line(cx: float, cy: float, bw: float, bh: float, w: int, h: int) -> str:
    return (
        f"0 {cx / w:.6f} {cy / h:.6f} {bw / w:.6f} {bh / h:.6f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", default="video/golf_swing_front.mp4")
    parser.add_argument("--out", default="datasets/clubhead/to_label")
    parser.add_argument("--max-frames", type=int, default=220)
    parser.add_argument("--box-scale", type=float, default=0.12, help="Box size vs shoulder width")
    args = parser.parse_args()

    from ultralytics import YOLO

    import config
    from analyzer.club_track import (
        _grip_from_pose,
        _median_shaft_length,
        _shoulder_width,
        search_shaft_line,
        _hands_below_shoulders,
    )
    from analyzer.metrics.biomechanics import GolfBiomechanicsAnalyzer
    from analyzer.pose import PoseExtractor
    from analyzer.swing_trim import scout_trim_window
    from analyzer.video_io import iter_frames, read_video_meta
    from scripts.extract_club_frames import _sample_indices

    video = Path(args.video)
    if not video.is_absolute():
        video = ROOT / video
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(config.MODEL_PATH)
    pose_ex = PoseExtractor(model)
    meta = read_video_meta(str(video))
    trim = scout_trim_window(str(video), meta, pose_ex)

    poses = []
    frames = []
    for i, frame in enumerate(
        iter_frames(str(video), trim.source_start_frame, trim.source_end_frame)
    ):
        poses.append(pose_ex.detect(frame, i))
        frames.append(frame)

    valid = [p for p in poses if p is not None]
    bio = GolfBiomechanicsAnalyzer(valid, fps=meta.fps).analyze()
    handedness = bio.handedness
    shaft_len = _median_shaft_length(poses)

    n = len(frames)
    want = set(_sample_indices(n, min(args.max_frames, n)))
    # Always include address→impact neighborhood
    for i in range(max(0, bio.phases.address - 2), min(n, bio.phases.impact + 15)):
        want.add(i)

    stem = video.stem
    written = 0
    prev_ang = None

    for i in sorted(want):
        pose = poses[i]
        frame = frames[i]
        if pose is None:
            continue
        grip_hit = _grip_from_pose(pose.keypoints, handedness)
        if grip_hit is None:
            continue
        grip, _ = grip_hit
        hit = search_shaft_line(
            frame, pose.keypoints, grip, shaft_len, prev_angle_deg=prev_ang
        )
        tip = None
        conf = 0.0
        if hit is not None:
            tip, conf, ang = hit
            if _hands_below_shoulders(pose.keypoints, grip) and abs(ang - 90.0) > 18:
                tip = None
            else:
                prev_ang = ang

        # Downswing: tip from grip + last angle / downward bias if line fails
        if tip is None and prev_ang is not None:
            import math

            tip = (
                float(grip[0] + math.cos(math.radians(prev_ang)) * shaft_len),
                float(grip[1] + math.sin(math.radians(prev_ang)) * shaft_len),
            )
            conf = 0.25

        if tip is None:
            continue

        sw = _shoulder_width(pose.keypoints, 0.4) or 100.0
        box = max(28.0, sw * args.box_scale * (1.4 if conf < 0.4 else 1.0))
        h_img, w_img = frame.shape[:2]
        cx, cy = tip
        # Clamp box inside image
        bw = min(box, w_img - 2)
        bh = min(box * 0.9, h_img - 2)
        cx = float(np.clip(cx, bw / 2 + 1, w_img - bw / 2 - 1))
        cy = float(np.clip(cy, bh / 2 + 1, h_img - bh / 2 - 1))

        name = f"{stem}_f{trim.source_start_frame + i:06d}"
        cv2.imwrite(str(out_dir / f"{name}.jpg"), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        (out_dir / f"{name}.txt").write_text(_yolo_line(cx, cy, bw, bh, w_img, h_img) + "\n")
        written += 1

    print(f"Bootstrap wrote {written} labeled frames → {out_dir}")
    print("Review/fix labels before production training when possible.")


if __name__ == "__main__":
    main()
