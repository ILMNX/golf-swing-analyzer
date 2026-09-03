#!/usr/bin/env python3
"""Convert Label Studio JSON export → YOLO .txt next to to_label/*.jpg.

Accepts:
  - Label Studio JSON export (list of tasks with annotations)
  - Or a directory of YOLO .txt already named like the images (copy-through)

YOLO line: 0 <cx> <cy> <w> <h>  (normalized)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _stem_from_image_url(url: str) -> str | None:
    # /data/local-files/?d=to_label/foo.jpg  or  upload/.../foo.jpg  or plain path
    m = re.search(r"([^/\\]+)\.(jpg|jpeg|png|webp)$", url, re.I)
    return m.group(1) if m else None


def _results_to_yolo(results: list[dict]) -> list[str]:
    lines: list[str] = []
    for r in results:
        if r.get("type") not in ("rectanglelabels", "rectangle"):
            continue
        val = r.get("value") or {}
        labels = val.get("rectanglelabels") or val.get("labels") or []
        if labels and "clubhead" not in labels and labels[0] not in ("clubhead", "0"):
            # single-class project — still accept any box if unlabeled oddly
            if "clubhead" not in {str(x).lower() for x in labels}:
                continue
        # Label Studio percentages 0–100
        x = float(val["x"]) / 100.0
        y = float(val["y"]) / 100.0
        w = float(val["width"]) / 100.0
        h = float(val["height"]) / 100.0
        cx = x + w / 2.0
        cy = y + h / 2.0
        if w <= 0 or h <= 0:
            continue
        lines.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return lines


def import_ls_json(export_path: Path, out_dir: Path) -> tuple[int, int]:
    data = json.loads(export_path.read_text())
    if not isinstance(data, list):
        print("Expected a JSON list export from Label Studio", file=sys.stderr)
        sys.exit(1)

    written = 0
    empty = 0
    for task in data:
        image_url = (task.get("data") or {}).get("image") or ""
        stem = _stem_from_image_url(image_url)
        if stem is None:
            continue

        lines: list[str] = []
        for ann in task.get("annotations") or []:
            if ann.get("was_cancelled"):
                continue
            lines.extend(_results_to_yolo(ann.get("result") or []))

        # Prefer completed annotations; fall back to predictions if empty
        if not lines:
            for pred in task.get("predictions") or []:
                lines.extend(_results_to_yolo(pred.get("result") or []))

        out_txt = out_dir / f"{stem}.txt"
        if not lines:
            # Skip creating empty labels (split requires pairs)
            empty += 1
            if out_txt.is_file():
                out_txt.unlink()
            continue
        out_txt.write_text("\n".join(lines) + "\n")
        written += 1
    return written, empty


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "export",
        help="Label Studio JSON export file (Project → Export → JSON)",
    )
    parser.add_argument(
        "--out",
        default="datasets/clubhead/to_label",
        help="Directory for YOLO .txt (same folder as JPGs)",
    )
    args = parser.parse_args()

    export_path = Path(args.export)
    if not export_path.is_absolute():
        export_path = Path.cwd() / export_path
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    if not export_path.is_file():
        print(f"Missing export: {export_path}", file=sys.stderr)
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    written, empty = import_ls_json(export_path, out_dir)
    print(f"Wrote {written} YOLO labels → {out_dir} ({empty} tasks with no boxes)")


if __name__ == "__main__":
    main()
