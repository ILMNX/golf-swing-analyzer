"""Golf club tracking via YOLO clubhead (primary) + shaft line fallback + Kalman.

When yolov8n-club.pt is present, clubhead detection drives the tip. Shaft is
grip (wrists) → tip. Line search is used only as address/takeaway fallback.
Kalman coasts through motion-blur misses.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import config
from analyzer.keypoints import KeypointIndex, SKELETON_CONNECTIONS
from analyzer.metrics.biomechanics import SwingPhases
from analyzer.pose import FramePose

SHAFT_LENGTH_SHOULDER_FACTOR = 2.6
MIN_GRIP_CONF = 0.45
RAY_ANGLE_STEP_DEG = 3.0
KALMAN_COAST_MAX = 8
MIN_YOLO_ACCEPT_CONF = 0.32
MIN_YOLO_ADDRESS_CONF = 0.22


@dataclass
class ClubFrameTrack:
    frame_index: int
    grip_xy: tuple[float, float] | None = None
    tip_xy: tuple[float, float] | None = None
    shaft_angle_deg: float | None = None
    confidence: float = 0.0
    source: str = "none"  # line | kalman | yolo | fused | fallback


@dataclass
class ClubTrackResult:
    tracks: list[ClubFrameTrack] = field(default_factory=list)
    impact_frame_hint: int | None = None
    tip_path_px: list[list[float]] = field(default_factory=list)
    shaft_lean_impact_deg: float | None = None
    path_smoothness: float = 0.0
    mean_confidence: float = 0.0
    detection_rate: float = 0.0
    proxy_rate: float = 0.0
    yolo_enabled: bool = False
    method: str = "line+kalman"

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "yolo_enabled": self.yolo_enabled,
            "impact_frame_hint": self.impact_frame_hint,
            "shaft_lean_impact_deg": self.shaft_lean_impact_deg,
            "path_smoothness": round(self.path_smoothness, 3),
            "mean_confidence": round(self.mean_confidence, 3),
            "detection_rate": round(self.detection_rate, 3),
            "proxy_rate": round(self.proxy_rate, 3),
            "frames_tracked": sum(1 for t in self.tracks if t.tip_xy is not None),
            "frames_total": len(self.tracks),
            "tip_path_sample": self.tip_path_px[:: max(1, len(self.tip_path_px) // 24)]
            if self.tip_path_px
            else [],
        }


def _point(kp: np.ndarray, idx: int, min_conf: float) -> np.ndarray | None:
    if float(kp[idx, 2]) < min_conf:
        return None
    return kp[idx, :2].astype(float)


def _trail_wrist_idx(handedness: str) -> int:
    return KeypointIndex.RIGHT_WRIST if handedness == "right" else KeypointIndex.LEFT_WRIST


def _lead_wrist_idx(handedness: str) -> int:
    return KeypointIndex.LEFT_WRIST if handedness == "right" else KeypointIndex.RIGHT_WRIST


def _shoulder_width(kp: np.ndarray, min_conf: float) -> float | None:
    ls = _point(kp, KeypointIndex.LEFT_SHOULDER, min_conf)
    rs = _point(kp, KeypointIndex.RIGHT_SHOULDER, min_conf)
    if ls is None or rs is None:
        return None
    return float(np.linalg.norm(ls - rs))


def _grip_from_pose(kp: np.ndarray, handedness: str) -> tuple[np.ndarray, float] | None:
    lead = _point(kp, _lead_wrist_idx(handedness), MIN_GRIP_CONF)
    trail = _point(kp, _trail_wrist_idx(handedness), MIN_GRIP_CONF * 0.85)
    if lead is not None and trail is not None:
        return 0.52 * lead + 0.48 * trail, 0.9
    if lead is not None:
        return lead.copy(), 0.7
    if trail is not None:
        return trail.copy(), 0.55
    return None


def _mid_hip(kp: np.ndarray) -> np.ndarray | None:
    lh = _point(kp, KeypointIndex.LEFT_HIP, 0.35)
    rh = _point(kp, KeypointIndex.RIGHT_HIP, 0.35)
    if lh is None or rh is None:
        return None
    return (lh + rh) * 0.5


def _mid_shoulder(kp: np.ndarray) -> np.ndarray | None:
    ls = _point(kp, KeypointIndex.LEFT_SHOULDER, 0.35)
    rs = _point(kp, KeypointIndex.RIGHT_SHOULDER, 0.35)
    if ls is None or rs is None:
        return None
    return (ls + rs) * 0.5


def _hands_below_shoulders(kp: np.ndarray, grip: np.ndarray) -> bool:
    mid_sh = _mid_shoulder(kp)
    if mid_sh is None:
        return True
    return float(grip[1]) > float(mid_sh[1]) - 6.0


def _median_shaft_length(poses: list[FramePose | None]) -> float:
    widths: list[float] = []
    for pose in poses:
        if pose is None:
            continue
        w = _shoulder_width(pose.keypoints, MIN_GRIP_CONF)
        if w is not None and w > 5:
            widths.append(w)
    if not widths:
        return 140.0
    return float(np.median(widths) * SHAFT_LENGTH_SHOULDER_FACTOR)


def _body_mask(frame_shape: tuple[int, int], kp: np.ndarray) -> np.ndarray:
    """Skeleton mask so shaft search does not snap onto thighs/torso.

    Legs are masked thinly; the gap between the ankles (where the shaft
    usually sits at address) is left open.
    """
    h, w = frame_shape
    mask = np.zeros((h, w), dtype=np.uint8)
    for i, j in SKELETON_CONNECTIONS:
        if kp[i, 2] < 0.35 or kp[j, 2] < 0.35:
            continue
        pt1 = (int(kp[i, 0]), int(kp[i, 1]))
        pt2 = (int(kp[j, 0]), int(kp[j, 1]))
        thickness = 10 if {i, j} <= {11, 12, 13, 14, 15, 16} else 14
        cv2.line(mask, pt1, pt2, 255, thickness, cv2.LINE_AA)
    return mask


def _sample_ray(
    image: np.ndarray,
    origin: np.ndarray,
    angle_rad: float,
    length: float,
    n: int = 28,
    skip_frac: float = 0.12,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = image.shape[:2]
    ts = np.linspace(skip_frac, 1.0, n)
    xs = origin[0] + np.cos(angle_rad) * length * ts
    ys = origin[1] + np.sin(angle_rad) * length * ts
    valid = (xs >= 1) & (xs < w - 1) & (ys >= 1) & (ys < h - 1)
    if not np.any(valid):
        return xs, ys, valid
    return xs, ys, valid


def _bilinear(image: np.ndarray, xs: np.ndarray, ys: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vals = np.zeros(len(xs), dtype=np.float32)
    h, w = image.shape[:2]
    # Recompute validity for possibly offset coordinates
    in_bounds = (xs >= 1) & (xs < w - 1) & (ys >= 1) & (ys < h - 1)
    usable = valid & in_bounds
    if not np.any(usable):
        return vals
    xv = xs[usable]
    yv = ys[usable]
    x0 = np.floor(xv).astype(int)
    y0 = np.floor(yv).astype(int)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    wx = xv - x0
    wy = yv - y0
    ia = image[y0, x0].astype(np.float32)
    ib = image[y0, x1].astype(np.float32)
    ic = image[y1, x0].astype(np.float32)
    id_ = image[y1, x1].astype(np.float32)
    vals[usable] = (
        ia * (1 - wx) * (1 - wy)
        + ib * wx * (1 - wy)
        + ic * (1 - wx) * wy
        + id_ * wx * wy
    )
    return vals


def _angle_span_deg(
    kp: np.ndarray,
    grip: np.ndarray,
    prev_angle_deg: float | None,
) -> np.ndarray:
    """Candidate shaft angles (image coords: 90° = straight down)."""
    if _hands_below_shoulders(kp, grip):
        # Tight downward band: wider ranges lock onto pant seams (~74°) not the shaft.
        locked = prev_angle_deg is None or abs(prev_angle_deg - 90.0) < 18.0
        if locked:
            return np.arange(84.0, 98.0 + 1e-6, 2.0)
        extra = np.arange(prev_angle_deg - 22.0, prev_angle_deg + 22.0 + 1e-6, RAY_ANGLE_STEP_DEG)
        down = np.arange(80.0, 105.0 + 1e-6, RAY_ANGLE_STEP_DEG)
        return np.unique(np.concatenate([down, extra]))

    if prev_angle_deg is not None:
        return np.arange(prev_angle_deg - 42.0, prev_angle_deg + 42.0 + 1e-6, RAY_ANGLE_STEP_DEG)

    mid_hip = _mid_hip(kp)
    if mid_hip is not None:
        away = grip - mid_hip
        base = math.degrees(math.atan2(away[1], away[0]))
        return np.arange(base - 55.0, base + 55.0 + 1e-6, RAY_ANGLE_STEP_DEG)

    return np.arange(0.0, 360.0, RAY_ANGLE_STEP_DEG * 2)


def _ridge_along_ray(
    gray: np.ndarray,
    origin: np.ndarray,
    angle_rad: float,
    length: float,
    body: np.ndarray,
    offset: float = 3.0,
) -> float:
    """Mean |center - neighbors| along a thin line — silver or dark shafts."""
    xs, ys, valid = _sample_ray(gray, origin, angle_rad, length, n=36, skip_frac=0.18)
    nx = -math.sin(angle_rad)
    ny = math.cos(angle_rad)
    center = _bilinear(gray, xs, ys, valid)
    left = _bilinear(gray, xs + offset * nx, ys + offset * ny, valid)
    right = _bilinear(gray, xs - offset * nx, ys - offset * ny, valid)
    bvals = _bilinear(body.astype(np.float32), xs, ys, valid)
    usable = valid & (bvals < 140)
    if int(np.count_nonzero(usable)) < 10:
        return 0.0
    contrast = np.abs(center - 0.5 * (left + right))
    return float(np.mean(contrast[usable]))


def _extend_tip(
    gray: np.ndarray,
    grip: np.ndarray,
    angle_rad: float,
    shaft_len: float,
    body: np.ndarray,
) -> float:
    """Walk along the ray and stop where the thin-line ridge dies."""
    max_len = shaft_len * 1.55
    min_len = shaft_len * 0.55
    last_good = shaft_len
    nx = -math.sin(angle_rad)
    ny = math.cos(angle_rad)
    for t in np.linspace(min_len, max_len, 32):
        p = grip + np.array([math.cos(angle_rad), math.sin(angle_rad)], dtype=float) * t
        xs = np.array([p[0]])
        ys = np.array([p[1]])
        valid = np.array([True])
        h, w = gray.shape[:2]
        if not (1 <= p[0] < w - 2 and 1 <= p[1] < h - 2):
            break
        c = float(_bilinear(gray, xs, ys, valid)[0])
        lft = float(_bilinear(gray, xs + 3 * nx, ys + 3 * ny, valid)[0])
        rgt = float(_bilinear(gray, xs - 3 * nx, ys - 3 * ny, valid)[0])
        b = float(_bilinear(body.astype(np.float32), xs, ys, valid)[0])
        ridge = abs(c - 0.5 * (lft + rgt))
        if ridge >= 9.0 and b < 170:
            last_good = float(t)
        elif t > shaft_len * 0.85 and ridge < 6.0:
            break
    return last_good


def search_shaft_line(
    frame_bgr: np.ndarray,
    kp: np.ndarray,
    grip: np.ndarray,
    shaft_len: float,
    prev_angle_deg: float | None = None,
) -> tuple[tuple[float, float], float, float] | None:
    """Return (tip_xy, confidence, angle_deg) for the strongest thin line from the grip."""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    body = _body_mask(gray.shape, kp)
    at_address = _hands_below_shoulders(kp, grip)
    probe_len = shaft_len * (1.35 if at_address else 1.05)

    angles = _angle_span_deg(kp, grip, prev_angle_deg)
    best: tuple[float, float] | None = None

    for ang_deg in angles:
        ang = math.radians(float(ang_deg))
        ridge = _ridge_along_ray(blur, grip, ang, probe_len, body)
        if ridge < 1e-3:
            continue
        score = ridge
        if at_address:
            score -= abs(float(ang_deg) - 90.0) * 0.45
            la = _point(kp, KeypointIndex.LEFT_ANKLE, 0.3)
            ra = _point(kp, KeypointIndex.RIGHT_ANKLE, 0.3)
            if la is not None and ra is not None:
                tip_x = float(grip[0] + math.cos(ang) * probe_len)
                target_x = float(la[0] * 0.55 + ra[0] * 0.45)
                span = abs(float(la[0] - ra[0])) + 8.0
                score -= abs(tip_x - target_x) / span * 8.0
        if best is None or score > best[0]:
            best = (score, float(ang_deg))

    if best is None:
        return None

    score, ang_deg = best
    if score < 8.5:
        return None

    ang = math.radians(ang_deg)
    if at_address:
        la = _point(kp, KeypointIndex.LEFT_ANKLE, 0.3)
        ra = _point(kp, KeypointIndex.RIGHT_ANKLE, 0.3)
        ground_y = None
        if la is not None and ra is not None:
            ground_y = float(max(la[1], ra[1]))
        elif la is not None:
            ground_y = float(la[1])
        elif ra is not None:
            ground_y = float(ra[1])
        sy = math.sin(ang)
        if ground_y is not None and abs(sy) > 0.25:
            length = (ground_y + 48.0 - float(grip[1])) / sy
            length = float(np.clip(length, probe_len * 0.85, probe_len * 2.0))
        else:
            length = _extend_tip(blur, grip, ang, probe_len, body)
    else:
        length = _extend_tip(blur, grip, ang, probe_len, body)
    tip = (
        float(grip[0] + math.cos(ang) * length),
        float(grip[1] + math.sin(ang) * length),
    )
    conf = float(np.clip((score - 8.5) / 18.0, 0.25, 0.95))
    return tip, conf, ang_deg


def _load_yolo_club_model():
    path = Path(config.CLUB_MODEL_PATH)
    if not path.is_file():
        return None
    try:
        from ultralytics import YOLO

        return YOLO(str(path))
    except Exception:
        return None


def _yolo_tip(
    model,
    frame: np.ndarray,
    predicted_tip: tuple[float, float] | None,
    grip: tuple[float, float] | None,
    shaft_len: float,
    prev_angle_deg: float | None = None,
) -> tuple[tuple[float, float], float] | None:
    """Return tip = bbox center of best clubhead detection near predicted tip / shaft ray."""
    try:
        results = model.predict(frame, verbose=False, conf=0.18, iou=0.45, imgsz=640)
    except Exception:
        return None
    if not results or results[0].boxes is None or len(results[0].boxes) == 0:
        return None

    best = None
    best_score = -1.0
    h, w = frame.shape[:2]
    for box in results[0].boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0].cpu().numpy())
        cx = float((xyxy[0] + xyxy[2]) * 0.5)
        cy = float((xyxy[1] + xyxy[3]) * 0.5)
        if not (0 <= cx < w and 0 <= cy < h):
            continue

        score = conf
        if predicted_tip is not None:
            dist = math.hypot(cx - predicted_tip[0], cy - predicted_tip[1])
            score = conf * math.exp(-dist / 90.0)
        if grip is not None:
            gdist = math.hypot(cx - grip[0], cy - grip[1])
            if gdist < max(28.0, shaft_len * 0.32):
                score *= 0.08
            elif gdist > shaft_len * 1.85:
                score *= 0.55
            if prev_angle_deg is not None and gdist > 20:
                ang = math.radians(prev_angle_deg)
                expected = (
                    grip[0] + math.cos(ang) * gdist,
                    grip[1] + math.sin(ang) * gdist,
                )
                off = math.hypot(cx - expected[0], cy - expected[1])
                score *= math.exp(-off / 55.0)
        if score > best_score:
            best_score = score
            best = ((cx, cy), conf)
    if best is None or best_score < 0.05:
        return None
    return best


class TipKalman:
    """Constant-velocity Kalman on clubhead (x, y, vx, vy)."""

    def __init__(self) -> None:
        self.x: np.ndarray | None = None
        self.P: np.ndarray | None = None
        self.misses = 0

    def predict(self) -> tuple[float, float] | None:
        if self.x is None or self.P is None:
            return None
        f = np.array(
            [
                [1.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 1.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        q = np.diag([12.0, 12.0, 40.0, 40.0])
        self.x = f @ self.x
        self.P = f @ self.P @ f.T + q
        return (float(self.x[0]), float(self.x[1]))

    def predicted_xy(self) -> tuple[float, float] | None:
        if self.x is None:
            return None
        return (float(self.x[0]), float(self.x[1]))

    def speed(self) -> float:
        if self.x is None:
            return 0.0
        return float(math.hypot(self.x[2], self.x[3]))

    def gate(self, z: tuple[float, float]) -> bool:
        pred = self.predicted_xy()
        if pred is None:
            return True
        limit = 36.0 + 2.4 * self.speed()
        return math.hypot(z[0] - pred[0], z[1] - pred[1]) < limit

    def update(self, z: tuple[float, float], conf: float) -> tuple[float, float]:
        if self.x is None:
            self.x = np.array([z[0], z[1], 0.0, 0.0], dtype=float)
            self.P = np.diag([50.0, 50.0, 80.0, 80.0])
            self.misses = 0
            return z
        h = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])
        r = np.eye(2) * (22.0 / max(conf, 0.2))
        y = np.array([z[0], z[1]], dtype=float) - h @ self.x
        s = h @ self.P @ h.T + r
        k = self.P @ h.T @ np.linalg.inv(s)
        self.x = self.x + k @ y
        self.P = (np.eye(4) - k @ h) @ self.P
        self.misses = 0
        return (float(self.x[0]), float(self.x[1]))

    def coast(self) -> tuple[float, float] | None:
        self.misses += 1
        if self.misses > KALMAN_COAST_MAX:
            return None
        return self.predicted_xy()


def _constrain_length(
    grip: np.ndarray,
    tip: tuple[float, float],
    shaft_len: float,
    *,
    loose: bool = False,
) -> tuple[float, float]:
    vec = np.array([tip[0] - grip[0], tip[1] - grip[1]], dtype=float)
    nrm = float(np.linalg.norm(vec))
    if nrm < 1e-3:
        return (float(grip[0]), float(grip[1] + shaft_len))
    lo = shaft_len * (0.7 if loose else 0.82)
    hi = shaft_len * (1.65 if loose else 1.22)
    scale = float(np.clip(nrm, lo, hi))
    out = grip + vec / nrm * scale
    return (float(out[0]), float(out[1]))


def _tip_plausible(
    kp: np.ndarray,
    grip: np.ndarray,
    tip: tuple[float, float],
    *,
    at_address: bool,
    shaft_len: float,
) -> bool:
    """Reject classic false tips (between legs / torso) when hands are raised."""
    if at_address:
        return True
    mid_hip = _mid_hip(kp)
    mid_sh = _mid_shoulder(kp)
    if mid_sh is None:
        return True
    hands_high = float(grip[1]) < float(mid_sh[1]) + 20.0
    if not hands_high:
        return True
    # Tip below hip line while hands are high → almost always legs / ground FP
    if mid_hip is not None and tip[1] > mid_hip[1] - 8.0:
        return False
    if mid_hip is not None:
        torso = 0.5 * (mid_hip + mid_sh)
        if math.hypot(tip[0] - torso[0], tip[1] - torso[1]) < max(36.0, shaft_len * 0.22):
            return False
    # Tip too close to either knee while hands high
    for idx in (KeypointIndex.LEFT_KNEE, KeypointIndex.RIGHT_KNEE):
        knee = _point(kp, idx, 0.3)
        if knee is not None and math.hypot(tip[0] - knee[0], tip[1] - knee[1]) < 42.0:
            return False
    return True


def track_club(
    video_path: str,
    poses: list[FramePose | None],
    handedness: str = "right",
    phases: SwingPhases | None = None,
    start_frame: int = 0,
    end_frame: int | None = None,
) -> ClubTrackResult:
    """YOLO clubhead primary; line search only as address fallback; Kalman coasts misses."""
    from analyzer.video_io import iter_frames

    shaft_len = _median_shaft_length(poses)
    locked_len: float | None = None
    yolo_model = _load_yolo_club_model()
    yolo_enabled = yolo_model is not None
    kalman = TipKalman()
    prev_angle: float | None = None
    tracks: list[ClubFrameTrack] = []

    address = phases.address if phases is not None else 0

    for i, frame in enumerate(iter_frames(video_path, start_frame, end_frame)):
        pose = poses[i] if i < len(poses) else None
        pred = kalman.predict()

        if pose is None:
            coast = kalman.coast()
            tracks.append(
                ClubFrameTrack(
                    frame_index=i,
                    tip_xy=coast,
                    confidence=0.08 if coast else 0.0,
                    source="kalman" if coast else "none",
                )
            )
            continue

        grip_hit = _grip_from_pose(pose.keypoints, handedness)
        if grip_hit is None:
            coast = kalman.coast()
            tracks.append(
                ClubFrameTrack(
                    frame_index=i,
                    tip_xy=coast,
                    confidence=0.08 if coast else 0.0,
                    source="kalman" if coast else "none",
                )
            )
            continue

        grip, grip_conf = grip_hit
        length = locked_len or shaft_len
        at_address = _hands_below_shoulders(pose.keypoints, grip)

        meas_tip: tuple[float, float] | None = None
        meas_conf = 0.0
        source = "fallback"

        # 1) YOLO clubhead — primary when weights exist
        if yolo_model is not None:
            yolo_hit = _yolo_tip(
                yolo_model,
                frame,
                pred,
                (float(grip[0]), float(grip[1])),
                length,
                prev_angle_deg=prev_angle,
            )
            if yolo_hit is not None:
                tip_y, conf_y = yolo_hit
                min_yolo = MIN_YOLO_ADDRESS_CONF if at_address else MIN_YOLO_ACCEPT_CONF
                if conf_y >= min_yolo and _tip_plausible(
                    pose.keypoints,
                    grip,
                    tip_y,
                    at_address=at_address,
                    shaft_len=length,
                ):
                    meas_tip, meas_conf = tip_y, conf_y
                    source = "yolo"

        # 2) Line search — address fallback (or when YOLO absent)
        if meas_tip is None and (not yolo_enabled or at_address):
            line_hit = search_shaft_line(
                frame,
                pose.keypoints,
                grip,
                length,
                prev_angle_deg=prev_angle,
            )
            if line_hit is not None:
                tip_l, conf_l, ang_l = line_hit
                if not (at_address and abs(ang_l - 90.0) > 16.0):
                    if _tip_plausible(
                        pose.keypoints,
                        grip,
                        tip_l,
                        at_address=at_address,
                        shaft_len=length,
                    ):
                        meas_tip, meas_conf = tip_l, conf_l
                        source = "line"

        accepted = False
        tip: tuple[float, float] | None = None
        conf = 0.0

        if meas_tip is not None and kalman.gate(meas_tip):
            tip = kalman.update(meas_tip, meas_conf)
            accepted = True
            conf = meas_conf
            if locked_len is None and source in ("line", "yolo", "fused"):
                if phases is None or i <= address + 12 or source == "yolo":
                    locked_len = float(
                        np.clip(
                            math.hypot(meas_tip[0] - grip[0], meas_tip[1] - grip[1]),
                            shaft_len * 0.7,
                            shaft_len * 1.55,
                        )
                    )
        else:
            coast = kalman.coast()
            if coast is not None and _tip_plausible(
                pose.keypoints,
                grip,
                coast,
                at_address=at_address,
                shaft_len=length,
            ):
                tip = coast
                source = "kalman"
                # Keep below overlay draw threshold so coast never paints a fake shaft
                conf = max(0.05, 0.28 - 0.04 * kalman.misses)
            else:
                # Do not invent a tip / poison Kalman — hide shaft until a real detect
                tip = None
                source = "none"
                conf = 0.0

        use_len = locked_len or shaft_len
        if tip is not None:
            if source == "yolo":
                tip = _constrain_length(grip, tip, use_len, loose=True)
            else:
                tip = _constrain_length(grip, tip, use_len, loose=at_address)

            if accepted and kalman.x is not None:
                kalman.x[0] = tip[0]
                kalman.x[1] = tip[1]

            if accepted:
                angle = float(math.degrees(math.atan2(tip[1] - grip[1], tip[0] - grip[0])))
                prev_angle = angle
            shaft_angle = (
                float(math.degrees(math.atan2(tip[1] - grip[1], tip[0] - grip[0])))
                if tip is not None
                else None
            )
        else:
            shaft_angle = None

        tracks.append(
            ClubFrameTrack(
                frame_index=i,
                grip_xy=(float(grip[0]), float(grip[1])),
                tip_xy=tip,
                shaft_angle_deg=shaft_angle,
                confidence=float(conf),
                source=source,
            )
        )

    return _summarize_tracks(tracks, phases, yolo_enabled=yolo_enabled)


def _summarize_tracks(
    tracks: list[ClubFrameTrack],
    phases: SwingPhases | None,
    yolo_enabled: bool,
) -> ClubTrackResult:
    tip_path: list[list[float]] = []
    confs: list[float] = []
    detect_n = 0

    for t in tracks:
        if t.tip_xy is not None:
            tip_path.append([round(t.tip_xy[0], 1), round(t.tip_xy[1], 1)])
            confs.append(t.confidence)
        if t.source in ("line", "fused", "yolo"):
            detect_n += 1

    n = max(len(tracks), 1)
    mean_conf = float(np.mean(confs)) if confs else 0.0
    detection_rate = detect_n / n
    proxy_rate = sum(1 for t in tracks if t.tip_xy is not None) / n

    smoothness = 0.0
    if len(tip_path) >= 3:
        pts = np.array(tip_path, dtype=float)
        deltas = np.diff(pts, axis=0)
        speeds = np.linalg.norm(deltas, axis=1)
        accel = np.diff(speeds)
        if len(accel) and float(np.mean(speeds)) > 1e-3:
            jerk = float(np.mean(np.abs(accel)) / (np.mean(speeds) + 1e-3))
            smoothness = float(np.clip(1.0 - jerk / 3.0, 0.0, 1.0))

    impact_hint = _impact_from_tips(tracks, phases)
    lean = None
    if impact_hint is not None and 0 <= impact_hint < len(tracks):
        t = tracks[impact_hint]
        if t.shaft_angle_deg is not None:
            # Smallest difference to image-down (90°); wrap-safe.
            lean = abs((t.shaft_angle_deg - 90.0 + 180.0) % 360.0 - 180.0)

    method = "line+yolo+kalman" if yolo_enabled else "line+kalman"
    return ClubTrackResult(
        tracks=tracks,
        impact_frame_hint=impact_hint,
        tip_path_px=tip_path,
        shaft_lean_impact_deg=round(lean, 1) if lean is not None else None,
        path_smoothness=smoothness,
        mean_confidence=mean_conf,
        detection_rate=detection_rate,
        proxy_rate=proxy_rate,
        yolo_enabled=yolo_enabled,
        method=method,
    )


def _impact_from_tips(
    tracks: list[ClubFrameTrack],
    phases: SwingPhases | None,
) -> int | None:
    if not tracks:
        return None

    if phases is not None:
        start = min(phases.top + 2, len(tracks) - 1)
        end = min(len(tracks) - 1, max(phases.impact + 12, phases.top + 8))
    else:
        start = max(0, len(tracks) // 4)
        end = len(tracks) - 1

    if end <= start:
        return phases.impact if phases else None

    best_i = None
    best_y = -1.0
    for i in range(start, end + 1):
        t = tracks[i]
        if t.tip_xy is None or t.confidence < 0.2:
            continue
        y = t.tip_xy[1]
        if y > best_y:
            best_y = y
            best_i = i

    return best_i


def refine_phases_with_club(
    phases: SwingPhases,
    club: ClubTrackResult,
) -> SwingPhases:
    hint = club.impact_frame_hint
    if hint is None or club.mean_confidence < 0.22:
        return phases
    if hint <= phases.top + 2:
        return phases
    if abs(hint - phases.impact) > max(18, phases.downswing_frames):
        blended = int(round(0.35 * phases.impact + 0.65 * hint))
    else:
        blended = hint

    blended = max(phases.top + 3, min(blended, len(club.tracks) - 1 if club.tracks else blended))
    return SwingPhases(
        address=phases.address,
        top=phases.top,
        impact=blended,
        backswing_frames=max(1, phases.top - phases.address),
        downswing_frames=max(1, blended - phases.top),
    )


def score_club_tracking(club: ClubTrackResult) -> int:
    if club.proxy_rate < 0.15:
        return 35
    base = 40 + club.mean_confidence * 35 + club.detection_rate * 20 + club.path_smoothness * 8
    if club.impact_frame_hint is not None:
        base += 5
    return int(np.clip(round(base), 0, 100))
