#!/usr/bin/env python3
"""Train YOLOv8n clubhead detector and export yolov8n-club.pt."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="datasets/clubhead/data.yaml")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--model", default="yolov8n.pt", help="Base detect weights")
    parser.add_argument("--device", default=None, help="cpu / 0 / cuda:0 (auto if omitted)")
    parser.add_argument(
        "--out",
        default="yolov8n-club.pt",
        help="Destination path for best weights (relative to ml-engine)",
    )
    args = parser.parse_args()

    data = Path(args.data)
    if not data.is_absolute():
        data = ROOT / data
    if not data.is_file():
        print(f"Missing data.yaml: {data}", file=sys.stderr)
        sys.exit(1)

    # Ensure YAML `path:` points at the dataset root (Ultralytics is picky).
    dataset_root = data.parent
    data.write_text(
        "# Auto-synced by train_clubhead.py\n"
        f"path: {dataset_root}\n"
        "train: images/train\n"
        "val: images/val\n"
        "\n"
        "names:\n"
        "  0: clubhead\n"
    )

    train_imgs = list((ROOT / "datasets/clubhead/images/train").glob("*.jpg"))
    train_labels = list((ROOT / "datasets/clubhead/labels/train").glob("*.txt"))
    if len(train_imgs) < 10 or len(train_labels) < 10:
        print(
            "Need at least ~10 labeled train images. "
            "See datasets/clubhead/README.md",
            file=sys.stderr,
        )
        sys.exit(1)

    from ultralytics import YOLO

    model = YOLO(args.model)
    train_kwargs = dict(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(ROOT / "runs" / "clubhead"),
        name="train",
        exist_ok=True,
        patience=25,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
        degrees=8.0,
        translate=0.08,
        scale=0.4,
        fliplr=0.5,
        mosaic=0.8,
        erasing=0.15,
    )
    if args.device is not None:
        train_kwargs["device"] = args.device

    results = model.train(**train_kwargs)
    best = Path(results.save_dir) / "weights" / "best.pt"
    if not best.is_file():
        # Ultralytics may return path differently across versions
        best = ROOT / "runs" / "clubhead" / "train" / "weights" / "best.pt"
    if not best.is_file():
        print(f"best.pt not found after training ({best})", file=sys.stderr)
        sys.exit(1)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    shutil.copy2(best, out)
    print(f"Exported {best} → {out}")


if __name__ == "__main__":
    main()
