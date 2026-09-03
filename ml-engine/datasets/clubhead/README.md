# Clubhead dataset — annotation guide

Train a single-class YOLOv8 detector for the **clubhead** (not the full shaft).
Weights are saved as `ml-engine/yolov8n-club.pt` and used automatically by club tracking.

> **Important:** Bootstrap auto-labels have been removed. Do **not** retrain until you
> hand-label frames. Weak line-search labels taught the model to miss during the swing.

## 1. Extract frames

From `ml-engine/`:

```bash
./venv/bin/python scripts/extract_club_frames.py \
  --videos video/golf_swing_front.mp4 \
  --out datasets/clubhead/to_label \
  --max-per-video 250
```

Frames already exist under `to_label/` (JPGs only). Add more face-on / DTL clips under
`video/` and pass them with `--videos`.

## 2. Annotate (required)

Label **only the clubhead** (metal/wood head, including motion-blur smear).

Do **not** box the entire shaft or the hands.

Tools that export YOLO `.txt` labels:

- [Label Studio](https://labelstud.io/) — YOLO export
- [Roboflow](https://roboflow.com/) — free tier
- [labelImg](https://github.com/HumanSignal/labelImg) — YOLO format

YOLO label line format (normalized 0–1):

```text
0 <cx> <cy> <width> <height>
```

Class id `0` = `clubhead`.

Put matching `*.txt` next to each `to_label/*.jpg`.

Prioritize **top → impact** blur frames; those decide high-speed tracking quality.

Old bootstrap labels (if you need them for reference) are under
`datasets/clubhead/_bootstrap_bak/` — do not train on them.

## 3. Split into train / val

```bash
./venv/bin/python scripts/split_club_labels.py \
  --src datasets/clubhead/to_label \
  --dataset datasets/clubhead \
  --val-ratio 0.15
```

Aim for ~85% train / ~15% val (at least ~30 val images). Target **200–400 correct** boxes.

## 4. Train

```bash
./venv/bin/python scripts/train_clubhead.py --epochs 100 --imgsz 640
```

Copies `best.pt` → `ml-engine/yolov8n-club.pt`.

CPU works for `yolov8n`; GPU is much faster. Expect val mAP50 ≳ 0.6 before swing
overlays look trustworthy.

## 5. Verify

Re-run analysis; `metrics.club.yolo_enabled` should be `true` and method `line+yolo+kalman`.

The red shaft overlay is drawn only for **YOLO / line** hits with sufficient confidence.
Kalman coast and body fallbacks are hidden so a miss does not paint a fake line into the legs.

## Tips

- Annotate blurred downswing frames — those matter most.
- Include face-on **and** DTL if possible.
- Prefer tight boxes around the head; leave a few pixels of margin.
- Never re-run `bootstrap_club_labels.py` for production weights.
