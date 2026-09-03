#!/usr/bin/env python3
"""Extract stratified frames from swing videos for clubhead annotation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _sample_indices(n: int, max_frames: int) -> list[int]:
    """Denser samples in the latter half of the clip (top → impact → follow)."""
    if n <= 0:
        return []
    if n <= max_frames:
        return list(range(n))

    early = int(max_frames * 0.25)
    mid = int(max_frames * 0.35)
    late = max_frames - early - mid

    early_idx = np.linspace(0, max(0, n // 3 - 1), early, dtype=int)
    mid_idx = np.linspace(n // 3, max(n // 3, (2 * n) // 3 - 1), mid, dtype=int)
    late_idx = np.linspace((2 * n) // 3, n - 1, late, dtype=int)
    return sorted(set(int(i) for i in np.concatenate([early_idx, mid_idx, late_idx])))


def extract_video(video_path: Path, out_dir: Path, max_per_video: int) -> int:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"SKIP (unreadable): {video_path}")
        return 0

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = set(_sample_indices(total, max_per_video))
    stem = video_path.stem
    written = 0

    for i in range(total):
        ok, frame = cap.read()
        if not ok:
            break
        if i not in indices:
            continue
        name = f"{stem}_f{i:06d}.jpg"
        cv2.imwrite(str(out_dir / name), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        written += 1

    cap.release()
    print(f"{video_path.name}: wrote {written} / {total} frames → {out_dir}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--videos",
        nargs="+",
        required=True,
        help="Video paths (relative to ml-engine or absolute)",
    )
    parser.add_argument(
        "--out",
        default="datasets/clubhead/to_label",
        help="Output directory for JPG frames",
    )
    parser.add_argument("--max-per-video", type=int, default=250)
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for v in args.videos:
        path = Path(v)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            print(f"SKIP (missing): {path}")
            continue
        total += extract_video(path, out_dir, args.max_per_video)

    print(f"Done. {total} frames in {out_dir}")


if __name__ == "__main__":
    main()
