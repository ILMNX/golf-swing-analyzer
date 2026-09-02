"""Apply tuning profile to scores and recommendations."""

from __future__ import annotations

from typing import Any

from analyzer.tuning.schema import ExpectedRange, TuningProfile


# Maps expected_range keys to summary metric that gets penalized
_RANGE_TO_SUMMARY: dict[str, str] = {
    "x_factor_deg": "rotation",
    "shoulder_rotation_max_deg": "rotation",
    "hip_rotation_max_deg": "rotation",
    "tempo_ratio": "tempo",
    "spine_angle_retention_deg": "posture",
    "head_movement_normalized": "head_stability",
    "hip_sway_normalized": "balance",
    "lead_arm_straightness_impact_deg": "posture",
}


def _penalty_for_range(actual: float, expected: ExpectedRange) -> int:
    penalty = 0
    if expected.min is not None and actual < expected.min:
        gap = expected.min - actual
        penalty += min(8, int(gap / max(abs(expected.min), 1) * 10))
    if expected.max is not None and actual > expected.max:
        gap = actual - expected.max
        penalty += min(8, int(gap / max(abs(expected.max), 1) * 10))
    return penalty


def _extract_range_actuals(metrics: dict[str, Any]) -> dict[str, float]:
    bio = metrics.get("biomechanics", {})
    posture = metrics.get("posture", {})
    head = metrics.get("head", {})
    rotation = metrics.get("rotation", {})
    tempo = metrics.get("tempo", {})
    balance = metrics.get("balance", {})
    arms = metrics.get("arms", {})

    return {
        "x_factor_deg": float(rotation.get("x_factor_deg", bio.get("x_factor_deg", 0))),
        "shoulder_rotation_max_deg": float(
            rotation.get("shoulder_rotation_max_deg", bio.get("shoulder_rotation_max_deg", 0))
        ),
        "hip_rotation_max_deg": float(
            rotation.get("hip_rotation_max_deg", bio.get("hip_rotation_max_deg", 0))
        ),
        "tempo_ratio": float(tempo.get("ratio", bio.get("tempo_ratio", 0))),
        "spine_angle_retention_deg": float(
            posture.get("spine_angle_retention_deg", bio.get("spine_angle_retention_deg", 0))
        ),
        "head_movement_normalized": float(
            head.get("movement_normalized", bio.get("head_movement_normalized", 0))
        ),
        "hip_sway_normalized": float(
            balance.get("sway_normalized", bio.get("hip_sway_normalized", 0))
        ),
        "lead_arm_straightness_impact_deg": float(
            arms.get("lead_arm_straightness_impact_deg", bio.get("lead_arm_straightness_impact_deg", 0))
        ),
    }


def adjust_summary_for_ranges(
    summary: dict[str, int],
    metrics: dict[str, Any],
    profile: TuningProfile,
) -> dict[str, int]:
    """Apply small penalties when measured values fall outside expected ranges."""
    if not profile.expected_ranges:
        return dict(summary)

    adjusted = dict(summary)
    actuals = _extract_range_actuals(metrics)

    for range_name, expected in profile.expected_ranges.items():
        actual = actuals.get(range_name)
        if actual is None:
            continue
        penalty = _penalty_for_range(actual, expected)
        if penalty <= 0:
            continue
        summary_key = _RANGE_TO_SUMMARY.get(range_name, "rotation")
        adjusted[summary_key] = max(0, adjusted.get(summary_key, 0) - penalty)

    return adjusted


def build_recommendation(
    summary: dict[str, int],
    profile: TuningProfile,
) -> str:
    tips: list[str] = []

    for rule in profile.recommendation_rules:
        value = summary.get(rule.metric, 100)
        if value < rule.below:
            tips.append(rule.message)

    if not tips:
        return (
            f"Swing {profile.shot_type.replace('_', ' ')} dengan "
            f"{profile.club.replace('_', ' ')} terlihat solid. "
            "Pertahankan konsistensi dan fokus pada repeatability."
        )

    seen: set[str] = set()
    unique: list[str] = []
    for tip in tips:
        if tip not in seen:
            seen.add(tip)
            unique.append(tip)

    return " ".join(unique[:3])


def compute_overall_score(summary: dict[str, int], profile: TuningProfile) -> int:
    weights = profile.scoring_weights.normalized()
    total = sum(summary.get(k, 0) * w for k, w in weights.items())
    return int(round(max(0, min(100, total))))
