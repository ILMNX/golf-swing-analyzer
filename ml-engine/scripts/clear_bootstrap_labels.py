#!/usr/bin/env python3
"""Move weak bootstrap YOLO labels aside so they are not used for training."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _move_txts(src: Path, dst: Path) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in src.glob("*.txt"):
        shutil.move(str(p), str(dst / p.name))
        n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        default="datasets/clubhead",
        help="Dataset root under ml-engine",
    )
    args = parser.parse_args()

    root = Path(args.dataset)
    if not root.is_absolute():
        root = ROOT / root
    bak = root / "_bootstrap_bak" / "labels"

    moved = 0
    for split in ("train", "val"):
        moved += _move_txts(root / "labels" / split, bak / split)
    moved += _move_txts(root / "to_label", bak / "to_label")

    print(f"Moved {moved} label files → {bak}")
    print("Images kept. Annotate to_label/*.jpg, then split_club_labels.py + train.")


if __name__ == "__main__":
    main()
