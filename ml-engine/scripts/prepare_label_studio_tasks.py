#!/usr/bin/env python3
"""Build Label Studio task JSON from datasets/clubhead/to_label/*.jpg.

Local file serving expects DOCUMENT_ROOT = datasets/clubhead so paths look like:
  /data/local-files/?d=to_label/<name>.jpg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", default="datasets/clubhead/to_label")
    parser.add_argument(
        "--out",
        default="datasets/clubhead/label_studio_tasks.json",
        help="Tasks JSON for Label Studio Import",
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

    if not images.is_dir():
        print(f"Missing images dir: {images}", file=sys.stderr)
        sys.exit(1)

    tasks: list[dict] = []
    skipped = 0
    for img in sorted(images.glob("*.jpg")):
        if args.skip_labeled and img.with_suffix(".txt").is_file():
            skipped += 1
            continue
        # DOCUMENT_ROOT must be datasets/clubhead (parent of to_label)
        rel = f"to_label/{img.name}"
        tasks.append({"data": {"image": f"/data/local-files/?d={rel}"}})

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tasks, indent=2))
    print(f"Wrote {len(tasks)} tasks → {out}" + (f" (skipped {skipped} labeled)" if skipped else ""))
    print("DOCUMENT_ROOT should be:", images.parent)


if __name__ == "__main__":
    main()
