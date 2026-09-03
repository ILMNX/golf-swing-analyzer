#!/usr/bin/env python3
"""Import a Roboflow YOLOv8 export zip into to_label/ (matching JPG stems).

Expects a zip with labels under train/valid/test (or flat labels/) as:
  labels/**/<stem>.txt
  images/**/<stem>.jpg   (optional — we keep existing to_label JPGs)
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", help="Roboflow YOLOv8 export .zip")
    parser.add_argument("--out", default="datasets/clubhead/to_label")
    args = parser.parse_args()

    zpath = Path(args.zip_path)
    if not zpath.is_absolute():
        zpath = Path.cwd() / zpath
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    if not zpath.is_file():
        print(f"Missing zip: {zpath}", file=sys.stderr)
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(tmp_path)

        for txt in tmp_path.rglob("*.txt"):
            if txt.name in ("classes.txt", "notes.json"):
                continue
            # Skip data.yaml-adjacent junk; only YOLO label lines
            try:
                body = txt.read_text().strip()
            except OSError:
                continue
            if not body:
                continue
            # Basic YOLO sanity: first token int class id
            first = body.split()[0]
            if not first.isdigit():
                continue

            dest = out_dir / txt.name
            # Prefer stems that exist as JPG in to_label
            jpg = out_dir / f"{txt.stem}.jpg"
            if not jpg.is_file():
                # Still write — user may have renamed; warn
                print(f"warn: no matching JPG for {txt.name}", file=sys.stderr)
            shutil.copy2(txt, dest)
            copied += 1

    print(f"Imported {copied} label files → {out_dir}")
    print("Next: ./venv/bin/python scripts/split_club_labels.py && train_clubhead.py")


if __name__ == "__main__":
    main()
