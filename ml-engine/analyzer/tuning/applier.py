"""Apply tuning profile to scores and recommendations."""

from __future__ import annotations

from typing import Any

from analyzer.tuning.schema import ExpectedRange, TuningProfile


# Maps expected_range keys to summary metric that gets penalized
_RANGE_TO_SUMMARY: dict[str, str] = {
    "shoulder_rotation_px": "rotation",
    "hip_rotation_px": "rotation",
    "right_wrist_travel_px": "tempo",
    "lateral_head_movement_px": "head_stability",
    "stance_width_px": "balance",
}


def _penalty_for_range(actual: float, expected: ExpectedRange) -> int:
    penalty = 0
    if expected.min is not None and actual < expected.min:
        gap = expected.min - actual
        penalty += min(12, int(gap / max(expected.min, 1) * 15))
    if expected.max is not None and actual > expected.max:
        gap = actual - expected.max
        penalty += min(12, int(gap / max(expected.max, 1) * 15))
    if expected.ideal is not None and expected.min is None and expected.max is None:
        pass
    return penalty


def _extract_range_actuals(metrics: dict[str, Any]) -> dict[str, float]:
    shoulders = metrics.get("shoulders", {})
    hips = metrics.get("hips", {})
    arms = metrics.get("arms", {})
    head = metrics.get("head", {})
    legs = metrics.get("legs", {})

    return {
        "shoulder_rotation_px": float(shoulders.get("rotation_range_px", 0)),
        "hip_rotation_px": float(hips.get("rotation_range_px", 0)),
        "right_wrist_travel_px": float(arms.get("right_wrist_travel_px", 0)),
        "lateral_head_movement_px": float(head.get("lateral_movement_px", 0)),
        "stance_width_px": float(legs.get("stance_width_px", {}).get("avg", 0)),
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

    # Deduplicate while preserving order
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
