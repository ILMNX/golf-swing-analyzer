"""Load and merge layered tuning YAML configs."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from analyzer.tuning.schema import (
    ExpectedRange,
    RecommendationRule,
    ScoringWeights,
    TuningProfile,
    ValidationTuning,
)

TUNING_DIR = Path(__file__).resolve().parent

CLUB_CATEGORY_MAP: dict[str, str] = {
    "driver": "driver",
    "wood_3": "woods",
    "wood_5": "woods",
    "iron_3": "irons",
    "iron_5": "irons",
    "iron_7": "irons",
    "iron_9": "irons",
    "wedge": "wedges",
    "putter": "putter",
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base."""
    result = dict(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_delta(weights: dict[str, float], delta: dict[str, float]) -> dict[str, float]:
    merged = dict(weights)
    for key, change in delta.items():
        merged[key] = max(0.0, merged.get(key, 0.0) + change)
    return merged


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        return {}
    return data


@lru_cache(maxsize=32)
def _load_yaml_cached(relative: str) -> dict[str, Any]:
    return _load_yaml(TUNING_DIR / relative)


def _load_with_extends(relative: str) -> dict[str, Any]:
    data = _load_yaml_cached(relative)
    extends = data.get("extends")
    if extends:
        parent = _load_with_extends(extends)
        data = _deep_merge(parent, data)
    return data


def _parse_validation(data: dict[str, Any]) -> ValidationTuning:
    v = data.get("validation", {})
    return ValidationTuning(
        min_sharpness=float(v.get("min_sharpness", 50.0)),
        min_pose_confidence=float(v.get("min_pose_confidence", 0.35)),
        min_visible_keypoint_ratio=float(v.get("min_visible_keypoint_ratio", 0.55)),
        min_person_height_ratio=float(v.get("min_person_height_ratio", 0.25)),
        min_side_view_score=float(v.get("min_side_view_score", 0.4)),
        validation_sample_frames=int(v.get("validation_sample_frames", 12)),
    )


def _parse_weights(data: dict[str, Any]) -> ScoringWeights:
    w = data.get("scoring_weights", {})
    return ScoringWeights(
        tempo=float(w.get("tempo", 0.20)),
        posture=float(w.get("posture", 0.25)),
        rotation=float(w.get("rotation", 0.25)),
        balance=float(w.get("balance", 0.20)),
        head_stability=float(w.get("head_stability", 0.10)),
    )


def _parse_rules(data: dict[str, Any]) -> list[RecommendationRule]:
    rules = []
    for item in data.get("recommendation_rules", []) or []:
        rules.append(RecommendationRule(
            metric=str(item["metric"]),
            below=int(item["below"]),
            message=str(item["message"]),
        ))
    return rules


def _parse_ranges(data: dict[str, Any]) -> dict[str, ExpectedRange]:
    ranges: dict[str, ExpectedRange] = {}
    for name, spec in (data.get("expected_ranges") or {}).items():
        ranges[name] = ExpectedRange(
            min=spec.get("min"),
            ideal=spec.get("ideal"),
            max=spec.get("max"),
        )
    return ranges


def _dict_to_profile(data: dict[str, Any], shot_type: str, club: str, category: str) -> TuningProfile:
    return TuningProfile(
        version=str(data.get("version", "1.0")),
        shot_type=shot_type,
        club=club,
        club_category=category,
        validation=_parse_validation(data),
        scoring_weights=_parse_weights(data),
        recommendation_rules=_parse_rules(data),
        expected_ranges=_parse_ranges(data),
        metrics_focus=list(data.get("metrics_focus") or []),
    )


def _resolve_club_layer(club: str, category: str) -> dict[str, Any]:
    club_file = f"clubs/{category}.yaml"
    club_data = _load_with_extends(club_file)

    merged: dict[str, Any] = {}
    defaults = club_data.get("defaults", {})
    if defaults:
        merged = _deep_merge(merged, defaults)

    club_block = club_data.get(club, {})
    if club_block:
        merged = _deep_merge(merged, club_block)

    return merged


def resolve_profile(shot_type: str = "full_swing", club: str = "iron_7") -> TuningProfile:
    """
    Merge tuning layers: defaults → shot_type → club category → club-specific block.
    """
    category = CLUB_CATEGORY_MAP.get(club, "irons")

    merged = _load_with_extends("defaults.yaml")
    shot_data = _load_with_extends(f"shots/{shot_type}.yaml")
    merged = _deep_merge(merged, shot_data)

    club_layer = _resolve_club_layer(club, category)
    merged = _deep_merge(merged, club_layer)

    # Optional explicit combo override: profiles/full_swing_iron_7.yaml
    combo_path = f"profiles/{shot_type}_{club}.yaml"
    combo_data = _load_yaml_cached(combo_path)
    if combo_data:
        merged = _deep_merge(merged, combo_data)

    weights = merged.get("scoring_weights", {})
    delta = merged.get("scoring_weights_delta", {})
    if delta:
        merged["scoring_weights"] = _apply_delta(weights, delta)

    return _dict_to_profile(merged, shot_type, club, category)
