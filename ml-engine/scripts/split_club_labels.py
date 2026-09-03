#!/usr/bin/env python3
"""Split labeled JPG+TXT pairs from to_label/ into train/val YOLO folders."""

from __future__ import annotations

import argparse
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default="datasets/clubhead/to_label")
    parser.add_argument("--dataset", default="datasets/clubhead")
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    src = Path(args.src)
    dataset = Path(args.dataset)
    if not src.is_absolute():
        src = ROOT / src
    if not dataset.is_absolute():
        dataset = ROOT / dataset

    pairs: list[tuple[Path, Path]] = []
    for img in sorted(src.glob("*.jpg")):
        label = img.with_suffix(".txt")
        if label.is_file():
            pairs.append((img, label))

    if not pairs:
        print(f"No JPG+TXT pairs in {src}", file=sys.stderr)
        sys.exit(1)

    random.seed(args.seed)
    random.shuffle(pairs)
    n_val = max(1, int(round(len(pairs) * args.val_ratio)))
    val_set = set(pairs[:n_val])

    for split in ("train", "val"):
        (dataset / "images" / split).mkdir(parents=True, exist_ok=True)
        (dataset / "labels" / split).mkdir(parents=True, exist_ok=True)

    for img, label in pairs:
        split = "val" if (img, label) in val_set else "train"
        shutil.copy2(img, dataset / "images" / split / img.name)
        shutil.copy2(label, dataset / "labels" / split / label.name)

    print(f"Split {len(pairs)} pairs → train={len(pairs) - n_val}, val={n_val}")


if __name__ == "__main__":
    main()
