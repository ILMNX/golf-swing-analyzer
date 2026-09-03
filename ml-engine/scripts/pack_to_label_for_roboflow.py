#!/usr/bin/env python3
"""Zip to_label JPGs for Roboflow upload (web UI or CLI)."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", default="datasets/clubhead/to_label")
    parser.add_argument(
        "--out",
        default="datasets/clubhead/roboflow_upload_to_label.zip",
    )
    parser.add_argument(
        "--skip-labeled",
        action="store_true",
        help="Omit images that already have a matching .txt",
    )
    args = parser.parse_args()

    images = Path(args.images)
    if not images.is_absolute():
        images = ROOT / images
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out

    jpgs = sorted(images.glob("*.jpg"))
    if args.skip_labeled:
        jpgs = [p for p in jpgs if not p.with_suffix(".txt").is_file()]
    if not jpgs:
        print(f"No images to pack in {images}", file=sys.stderr)
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for img in jpgs:
            zf.write(img, arcname=img.name)
    print(f"Packed {len(jpgs)} images → {out}")
    print("Roboflow: New Project → Object Detection → Upload zip → class 'clubhead'")
    print("Export: YOLOv8 → download zip → scripts/import_roboflow_yolo.py <zip>")


if __name__ == "__main__":
    main()
