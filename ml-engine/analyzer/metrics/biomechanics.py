"""Biomechanics-based golf swing metrics from normalized pose sequences."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from analyzer.keypoints import KeypointIndex
from analyzer.pose import FramePose

# Master prompt: metric calculations require higher confidence than validation overlay.
BIOMECHANICS_MIN_CONFIDENCE = 0.5

# Right-handed default; lead/trail sides swap when inferred left-handed.
RIGHT_HANDED_LEAD = (KeypointIndex.LEFT_SHOULDER, KeypointIndex.LEFT_ELBOW, KeypointIndex.LEFT_WRIST)
RIGHT_HANDED_TRAIL_ANKLE = KeypointIndex.RIGHT_ANKLE
LEFT_HANDED_LEAD = (KeypointIndex.RIGHT_SHOULDER, KeypointIndex.RIGHT_ELBOW, KeypointIndex.RIGHT_WRIST)
LEFT_HANDED_TRAIL_ANKLE = KeypointIndex.LEFT_ANKLE


@dataclass
class SwingPhases:
    address: int = 0
    top: int = 0
    impact: int = 0
    backswing_frames: int = 0
    downswing_frames: int = 0


@dataclass
class BiomechanicsResult:
    handedness: str = "right"
    address_frame: int = 0
    address_shoulder_width: float = 0.0
    spine_angle_address_deg: float = 0.0
    spine_angle_impact_deg: float = 0.0
    spine_angle_retention_deg: float = 0.0
    head_movement_normalized: float = 0.0
    head_lateral_range_px: float = 0.0
    head_vertical_range_px: float = 0.0
    hip_sway_px: float = 0.0
    hip_sway_normalized: float = 0.0
    shoulder_rotation_max_deg: float = 0.0
    hip_rotation_max_deg: float = 0.0
    x_factor_deg: float = 0.0
    tempo_ratio: float = 0.0
    backswing_frames: int = 0
    downswing_frames: int = 0
    lead_arm_straightness_impact_deg: float = 0.0
    top_frame: int = 0
    impact_frame: int = 0
    detection_quality: float = 0.0
    phases: SwingPhases = field(default_factory=SwingPhases)


class GolfBiomechanicsAnalyzer:
    """Compute normalized golf swing metrics from a pose sequence."""

    def __init__(
        self,
        poses: list[FramePose],
        min_confidence: float = BIOMECHANICS_MIN_CONFIDENCE,
        handedness: str | None = None,
    ):
        self.min_confidence = min_confidence
        self.poses = poses
        self.n_frames = len(poses)
        self.keypoints = self._build_smoothed_keypoints(poses)
        self.handedness = handedness or self._infer_handedness()
        self._lead = RIGHT_HANDED_LEAD if self.handedness == "right" else LEFT_HANDED_LEAD
        self._trail_ankle = (
            RIGHT_HANDED_TRAIL_ANKLE if self.handedness == "right" else LEFT_HANDED_TRAIL_ANKLE
        )

    def analyze(self) -> BiomechanicsResult:
        if self.n_frames < 5:
            return BiomechanicsResult(detection_quality=self._detection_quality())

        phases = self._detect_swing_phases()
        address_width = self._shoulder_width(phases.address)
        if address_width < 1.0:
            address_width = self._median_shoulder_width() or 1.0

        spine_address = self._spine_angle_deg(phases.address)
        spine_impact = self._spine_angle_deg(phases.impact)
        spine_retention = abs(spine_address - spine_impact)

        head_norm, head_lat, head_vert = self._head_stability(
            phases.address, phases.impact, address_width
        )
        sway_px, sway_norm = self._hip_sway(phases.address, phases.top, address_width)
        shoulder_rot, hip_rot, x_factor = self._rotation_metrics(phases, address_width)
        tempo_ratio = self._tempo_ratio(phases)
        lead_arm = self._lead_arm_angle(phases.impact)

        return BiomechanicsResult(
            handedness=self.handedness,
            address_frame=phases.address,
            address_shoulder_width=round(address_width, 1),
            spine_angle_address_deg=round(spine_address, 1),
            spine_angle_impact_deg=round(spine_impact, 1),
            spine_angle_retention_deg=round(spine_retention, 1),
            head_movement_normalized=round(head_norm, 3),
            head_lateral_range_px=round(head_lat, 1),
            head_vertical_range_px=round(head_vert, 1),
            hip_sway_px=round(sway_px, 1),
            hip_sway_normalized=round(sway_norm, 3),
            shoulder_rotation_max_deg=round(shoulder_rot, 1),
            hip_rotation_max_deg=round(hip_rot, 1),
            x_factor_deg=round(x_factor, 1),
            tempo_ratio=round(tempo_ratio, 2),
            backswing_frames=phases.backswing_frames,
            downswing_frames=phases.downswing_frames,
            lead_arm_straightness_impact_deg=round(lead_arm, 1),
            top_frame=phases.top,
            impact_frame=phases.impact,
            detection_quality=round(self._detection_quality(), 3),
            phases=phases,
        )

    # ------------------------------------------------------------------
    # Keypoint preprocessing
    # ------------------------------------------------------------------

    def _build_smoothed_keypoints(self, poses: list[FramePose]) -> np.ndarray:
        """Shape (n_frames, 17, 3) with forward-fill then linear interpolation."""
        n = len(poses)
        raw = np.zeros((n, 17, 3), dtype=float)
        for i, pose in enumerate(poses):
            raw[i] = pose.keypoints

        smoothed = raw.copy()
        for kp in range(17):
            for axis in range(2):
                series = smoothed[:, kp, axis].copy()
                conf = smoothed[:, kp, 2]
                series = self._fill_series(series, conf)
                smoothed[:, kp, axis] = series
            # Confidence: carry forward valid values
            conf_series = smoothed[:, kp, 2]
            smoothed[:, kp, 2] = self._fill_confidence(conf_series)

        return smoothed

    def _fill_series(self, values: np.ndarray, confidences: np.ndarray) -> np.ndarray:
        valid = confidences >= self.min_confidence
        if not np.any(valid):
            return values

        out = values.copy()
        # Forward fill
        last_valid = None
        for i in range(len(out)):
            if valid[i]:
                last_valid = out[i]
            elif last_valid is not None:
                out[i] = last_valid

        # Backward fill leading gaps
        first_idx = int(np.argmax(valid))
        if first_idx > 0:
            out[:first_idx] = out[first_idx]

        # Linear interpolate remaining internal gaps
        indices = np.where(valid)[0]
        if len(indices) >= 2:
            out = np.interp(np.arange(len(out)), indices, out[indices])
        return out

    def _fill_confidence(self, conf: np.ndarray) -> np.ndarray:
        out = conf.copy()
        last = 0.0
        for i in range(len(out)):
            if out[i] >= self.min_confidence:
                last = out[i]
            elif last > 0:
                out[i] = last
        return out

    def _point(self, frame: int, idx: int) -> np.ndarray | None:
        if frame < 0 or frame >= self.n_frames:
            return None
        if self.keypoints[frame, idx, 2] < self.min_confidence:
            return None
        return self.keypoints[frame, idx, :2]

    def _mid_shoulder(self, frame: int) -> np.ndarray | None:
        ls = self._point(frame, KeypointIndex.LEFT_SHOULDER)
        rs = self._point(frame, KeypointIndex.RIGHT_SHOULDER)
        if ls is None or rs is None:
            return None
        return (ls + rs) / 2.0

    def _mid_hip(self, frame: int) -> np.ndarray | None:
        lh = self._point(frame, KeypointIndex.LEFT_HIP)
        rh = self._point(frame, KeypointIndex.RIGHT_HIP)
        if lh is None or rh is None:
            return None
        return (lh + rh) / 2.0

    def _shoulder_width(self, frame: int) -> float:
        ls = self._point(frame, KeypointIndex.LEFT_SHOULDER)
        rs = self._point(frame, KeypointIndex.RIGHT_SHOULDER)
        if ls is None or rs is None:
            return 0.0
        return float(np.linalg.norm(ls - rs))

    def _hip_width(self, frame: int) -> float:
        lh = self._point(frame, KeypointIndex.LEFT_HIP)
        rh = self._point(frame, KeypointIndex.RIGHT_HIP)
        if lh is None or rh is None:
            return 0.0
        return float(np.linalg.norm(lh - rh))

    def _median_shoulder_width(self) -> float:
        widths = [self._shoulder_width(i) for i in range(self.n_frames)]
        widths = [w for w in widths if w > 0]
        return float(np.median(widths)) if widths else 0.0

    def _infer_handedness(self) -> str:
        """
        Face-on heuristic for right-handed golfer:
        lead foot (left) is usually farther to the image-right than trail foot (right).
        """
        la = self._point(0, KeypointIndex.LEFT_ANKLE)
        ra = self._point(0, KeypointIndex.RIGHT_ANKLE)
        if la is None or ra is None:
            return "right"
        return "right" if float(la[0]) > float(ra[0]) else "left"

    def _detection_quality(self) -> float:
        core = [
            KeypointIndex.LEFT_SHOULDER,
            KeypointIndex.RIGHT_SHOULDER,
            KeypointIndex.LEFT_HIP,
            KeypointIndex.RIGHT_HIP,
            KeypointIndex.LEFT_WRIST,
            KeypointIndex.RIGHT_WRIST,
        ]
        confs = self.keypoints[:, core, 2]
        return float(np.mean(confs >= self.min_confidence))

    # ------------------------------------------------------------------
    # Metric calculations
    # ------------------------------------------------------------------

    def _spine_angle_deg(self, frame: int) -> float:
        """Angle of mid_hip → mid_shoulder line relative to vertical (degrees)."""
        mid_sh = self._mid_shoulder(frame)
        mid_hp = self._mid_hip(frame)
        if mid_sh is None or mid_hp is None:
            return 0.0

        dx = float(mid_sh[0] - mid_hp[0])
        dy = float(mid_sh[1] - mid_hp[1])
        if abs(dy) < 1e-6 and abs(dx) < 1e-6:
            return 0.0
        return float(math.degrees(math.atan2(abs(dx), abs(dy))))

    def _head_point(self, frame: int) -> np.ndarray | None:
        nose = self._point(frame, KeypointIndex.NOSE)
        if nose is not None:
            return nose

        le = self._point(frame, KeypointIndex.LEFT_EAR)
        re = self._point(frame, KeypointIndex.RIGHT_EAR)
        if le is not None and re is not None:
            return (le + re) / 2.0
        if le is not None:
            return le
        if re is not None:
            return re

        leye = self._point(frame, KeypointIndex.LEFT_EYE)
        reye = self._point(frame, KeypointIndex.RIGHT_EYE)
        if leye is not None and reye is not None:
            return (leye + reye) / 2.0
        return None

    def _head_stability(
        self, address: int, impact: int, address_shoulder_width: float
    ) -> tuple[float, float, float]:
        """
        Head drift from address to impact (not max-min over backswing).
        Lateral slide is penalized more than vertical dip/rotation.
        """
        head_addr = self._head_point(address)
        head_imp = self._head_point(impact)
        if head_addr is None or head_imp is None or address_shoulder_width < 1.0:
            return 0.0, 0.0, 0.0

        lateral = abs(float(head_imp[0] - head_addr[0]))
        vertical = abs(float(head_imp[1] - head_addr[1]))
        normalized = float(
            math.hypot(lateral, vertical * 0.35) / address_shoulder_width
        )
        return normalized, lateral, vertical

    def _hip_sway(self, address: int, top: int, address_shoulder_width: float) -> tuple[float, float]:
        trail_x_ref = None
        rel_positions: list[float] = []

        for i in range(address, top + 1):
            mid_hp = self._mid_hip(i)
            trail = self._point(i, self._trail_ankle)
            if mid_hp is None or trail is None:
                continue
            rel = float(mid_hp[0] - trail[0])
            rel_positions.append(rel)
            if i == address:
                trail_x_ref = rel

        if not rel_positions or trail_x_ref is None or address_shoulder_width < 1.0:
            return 0.0, 0.0

        sway = max(abs(r - trail_x_ref) for r in rel_positions)
        return sway, sway / address_shoulder_width

    @staticmethod
    def _rotation_from_width(current: float, address: float) -> float:
        if address < 1e-6:
            return 0.0
        ratio = float(np.clip(current / address, 0.0, 1.0))
        return float(np.degrees(np.arccos(ratio)))

    def _rotation_metrics(
        self, phases: SwingPhases, address_shoulder_width: float
    ) -> tuple[float, float, float]:
        address_hip = self._hip_width(phases.address)
        address_shoulder_angle = self._shoulder_line_angle_deg(phases.address)
        address_hip_angle = self._hip_line_angle_deg(phases.address)

        shoulder_rots: list[float] = []
        hip_rots: list[float] = []
        x_factors: list[float] = []

        for i in range(phases.address, phases.top + 1):
            width_shoulder = self._rotation_from_width(
                self._shoulder_width(i), address_shoulder_width
            )
            angle_shoulder = abs(
                self._shoulder_line_angle_deg(i) - address_shoulder_angle
            )
            # Width ratio works face-on; line angle better for down-the-line / partial occlusion
            s_rot = max(width_shoulder, angle_shoulder)

            width_hip = (
                self._rotation_from_width(self._hip_width(i), address_hip)
                if address_hip > 0
                else 0.0
            )
            angle_hip = abs(self._hip_line_angle_deg(i) - address_hip_angle)
            h_rot = max(width_hip, angle_hip)

            shoulder_rots.append(s_rot)
            hip_rots.append(h_rot)
            x_factors.append(s_rot - h_rot)

        if not shoulder_rots:
            return 0.0, 0.0, 0.0

        return max(shoulder_rots), max(hip_rots), max(x_factors)

    def _hip_line_angle_deg(self, frame: int) -> float:
        lh = self._point(frame, KeypointIndex.LEFT_HIP)
        rh = self._point(frame, KeypointIndex.RIGHT_HIP)
        if lh is None or rh is None:
            return 0.0
        return float(math.degrees(math.atan2(rh[1] - lh[1], rh[0] - lh[0])))

    def _shoulder_line_angle_deg(self, frame: int) -> float:
        ls = self._point(frame, KeypointIndex.LEFT_SHOULDER)
        rs = self._point(frame, KeypointIndex.RIGHT_SHOULDER)
        if ls is None or rs is None:
            return 0.0
        return float(math.degrees(math.atan2(rs[1] - ls[1], rs[0] - ls[0])))

    def _lead_wrist_y(self, frame: int) -> float | None:
        pt = self._point(frame, self._lead[2])
        return float(pt[1]) if pt is not None else None

    def _wrist_speed_series(self) -> list[float]:
        speeds = [0.0]
        for i in range(1, self.n_frames):
            total = 0.0
            count = 0
            for wrist in (KeypointIndex.LEFT_WRIST, KeypointIndex.RIGHT_WRIST):
                p0 = self._point(i - 1, wrist)
                p1 = self._point(i, wrist)
                if p0 is not None and p1 is not None:
                    total += float(np.linalg.norm(p1 - p0))
                    count += 1
            speeds.append(total / max(count, 1))
        return speeds

    def _detect_address_frame(self, speeds: list[float]) -> int:
        """Last quiet frame before backswing wrist motion begins."""
        sample = speeds[20:min(200, self.n_frames)]
        if not sample:
            return 0

        quiet = float(np.percentile(sample, 25))
        threshold = max(2.0, quiet * 3.5 + 0.8)

        movement_start: int | None = None
        for i in range(35, min(280, self.n_frames - 12)):
            if float(np.mean(speeds[i : i + 8])) > threshold:
                movement_start = i
                break

        if movement_start is None:
            return 0
        return max(0, movement_start - 10)

    def _shoulder_rotation_at(self, frame: int, address: int, address_width: float) -> float:
        width_rot = self._rotation_from_width(self._shoulder_width(frame), address_width)
        angle_rot = abs(
            self._shoulder_line_angle_deg(frame) - self._shoulder_line_angle_deg(address)
        )
        return max(width_rot, angle_rot)

    def _detect_swing_phases(self) -> SwingPhases:
        speeds = self._wrist_speed_series()
        address = self._detect_address_frame(speeds)
        address_width = self._shoulder_width(address) or self._median_shoulder_width() or 1.0
        address_y = self._lead_wrist_y(address)
        if address_y is None:
            address_y = 0.0

        search_end = min(self.n_frames - 1, address + 200)

        # Top: peak shoulder rotation (reliable for face-on; wrist-only top fires too early)
        top = address + 5
        best_rot = 0.0
        for i in range(address + 5, search_end):
            rot = self._shoulder_rotation_at(i, address, address_width)
            if rot > best_rot:
                best_rot = rot
                top = i

        # Fallback: highest hands if rotation signal is weak
        if best_rot < 5.0:
            wrist_heights: list[tuple[int, float]] = []
            for i in range(address + 5, search_end):
                wy = self._lead_wrist_y(i)
                if wy is not None:
                    wrist_heights.append((i, wy))
            if wrist_heights:
                top = min(wrist_heights, key=lambda t: t[1])[0]

        # Impact: after top, hands reach lowest point (max wrist Y in image coords)
        impact = min(top + 10, self.n_frames - 1)
        post_top_limit = min(self.n_frames - 1, top + 120)
        post_top: list[tuple[int, float]] = []
        for i in range(top + 5, post_top_limit):
            wy = self._lead_wrist_y(i)
            if wy is not None:
                post_top.append((i, wy))
        if post_top:
            impact = max(post_top, key=lambda t: t[1])[0]

        impact = max(impact, top + 5)
        impact = min(impact, self.n_frames - 1)

        backswing = max(1, top - address)
        downswing = max(1, impact - top)

        return SwingPhases(
            address=address,
            top=top,
            impact=impact,
            backswing_frames=backswing,
            downswing_frames=downswing,
        )

    def _tempo_ratio(self, phases: SwingPhases) -> float:
        if phases.downswing_frames < 1:
            return 0.0
        return phases.backswing_frames / phases.downswing_frames

    def _angle_deg(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        ba = a - b
        bc = c - b
        denom = float(np.linalg.norm(ba) * np.linalg.norm(bc))
        if denom < 1e-8:
            return 0.0
        cosine = float(np.clip(np.dot(ba, bc) / denom, -1.0, 1.0))
        return float(math.degrees(math.acos(cosine)))

    def _lead_arm_angle(self, frame: int) -> float:
        sh = self._point(frame, self._lead[0])
        el = self._point(frame, self._lead[1])
        wr = self._point(frame, self._lead[2])
        if sh is None or el is None or wr is None:
            return 0.0
        return self._angle_deg(sh, el, wr)


# ------------------------------------------------------------------
# Scoring: map biomechanics values → 0–100 summary scores
# ------------------------------------------------------------------

def score_posture(spine_retention_deg: float) -> int:
    """Lower spine angle change address→impact is better."""
    return int(np.clip(100 - spine_retention_deg * 4.0, 0, 100))


def score_head_stability(movement_normalized: float) -> int:
    """Address→impact head drift. Pro target: lateral drift < 20% shoulder width."""
    if movement_normalized <= 0.0:
        return 75
    if movement_normalized <= 0.18:
        return int(np.clip(92 - movement_normalized * 40, 85, 100))
    if movement_normalized <= 0.32:
        return int(np.clip(85 - (movement_normalized - 0.18) * 120, 60, 90))
    if movement_normalized <= 0.50:
        return int(np.clip(65 - (movement_normalized - 0.32) * 150, 35, 70))
    return int(np.clip(35 - (movement_normalized - 0.50) * 80, 0, 40))


def score_balance(sway_normalized: float) -> int:
    """Hip sway during backswing — some shift is normal on full swings."""
    if sway_normalized <= 0.0:
        return 75
    if sway_normalized <= 0.22:
        return int(np.clip(88 - sway_normalized * 60, 75, 95))
    if sway_normalized <= 0.42:
        return int(np.clip(88 - (sway_normalized - 0.22) * 140, 45, 85))
    return int(np.clip(50 - (sway_normalized - 0.42) * 90, 0, 50))


def score_rotation(x_factor_deg: float) -> int:
    """Peak X-factor; tour range roughly 10–40° in 2D pose estimation."""
    if x_factor_deg <= 0:
        return 55
    if 12.0 <= x_factor_deg <= 38.0:
        return int(np.clip(72 + (x_factor_deg - 12.0) * 1.1, 0, 100))
    if x_factor_deg < 12.0:
        return int(np.clip(45 + x_factor_deg * 2.2, 0, 72))
    return int(np.clip(100 - (x_factor_deg - 38.0) * 2.0, 50, 100))


def score_tempo(ratio: float) -> int:
    """Tour-average tempo ratio ≈ 3:1; allow wider band for consumer video frame rates."""
    if ratio <= 0:
        return 55
    if 2.0 <= ratio <= 4.0:
        return int(np.clip(95 - abs(ratio - 3.0) * 18, 55, 100))
    if ratio < 2.0:
        return int(np.clip(55 + ratio * 15, 45, 75))
    return int(np.clip(75 - (ratio - 4.0) * 12, 40, 75))


def biomechanics_to_summary(bio: BiomechanicsResult) -> dict[str, int]:
    quality_factor = 0.5 + 0.5 * bio.detection_quality

    scores = {
        "posture": score_posture(bio.spine_angle_retention_deg),
        "head_stability": score_head_stability(bio.head_movement_normalized),
        "balance": score_balance(bio.hip_sway_normalized),
        "rotation": score_rotation(bio.x_factor_deg),
        "tempo": score_tempo(bio.tempo_ratio),
    }

    # Down-weight scores when pose detection quality is poor
    return {k: int(round(v * quality_factor)) for k, v in scores.items()}


def biomechanics_to_dict(bio: BiomechanicsResult) -> dict[str, Any]:
    return {
        "handedness": bio.handedness,
        "address_frame": bio.address_frame,
        "address_shoulder_width_px": bio.address_shoulder_width,
        "spine_angle_address_deg": bio.spine_angle_address_deg,
        "spine_angle_impact_deg": bio.spine_angle_impact_deg,
        "spine_angle_retention_deg": bio.spine_angle_retention_deg,
        "head_movement_normalized": bio.head_movement_normalized,
        "hip_sway_px": bio.hip_sway_px,
        "hip_sway_normalized": bio.hip_sway_normalized,
        "shoulder_rotation_max_deg": bio.shoulder_rotation_max_deg,
        "hip_rotation_max_deg": bio.hip_rotation_max_deg,
        "x_factor_deg": bio.x_factor_deg,
        "tempo_ratio": bio.tempo_ratio,
        "backswing_frames": bio.backswing_frames,
        "downswing_frames": bio.downswing_frames,
        "lead_arm_straightness_impact_deg": bio.lead_arm_straightness_impact_deg,
        "top_frame": bio.top_frame,
        "impact_frame": bio.impact_frame,
        "detection_quality": bio.detection_quality,
    }
