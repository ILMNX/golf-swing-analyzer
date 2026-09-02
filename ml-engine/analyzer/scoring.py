"""Overall score and coaching recommendations — delegates to tuning applier."""

from __future__ import annotations

from typing import Any

from analyzer.tuning.applier import (
    adjust_summary_for_ranges,
    build_recommendation,
    compute_overall_score,
)
from analyzer.tuning.schema import TuningProfile


def score_swing(
    metrics: dict[str, Any],
    profile: TuningProfile,
) -> dict[str, Any]:
    """Apply tuning profile to raw metrics and return score + recommendation."""
    raw_summary = metrics["summary"]
    adjusted_summary = adjust_summary_for_ranges(raw_summary, metrics, profile)
    score = compute_overall_score(adjusted_summary, profile)
    recommendation = build_recommendation(adjusted_summary, profile)

    return {
        "score": score,
        "recommendation": recommendation,
        "summary": adjusted_summary,
    }
