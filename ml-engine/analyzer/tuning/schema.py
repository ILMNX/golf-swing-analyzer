"""Tuning profile schema — single source of truth for config types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationTuning:
    min_sharpness: float = 50.0
    min_pose_confidence: float = 0.35
    min_visible_keypoint_ratio: float = 0.55
    min_person_height_ratio: float = 0.25
    min_side_view_score: float = 0.4
    validation_sample_frames: int = 12


@dataclass
class ScoringWeights:
    tempo: float = 0.20
    posture: float = 0.25
    rotation: float = 0.25
    balance: float = 0.20
    head_stability: float = 0.10

    def normalized(self) -> dict[str, float]:
        raw = {
            "tempo": self.tempo,
            "posture": self.posture,
            "rotation": self.rotation,
            "balance": self.balance,
            "head_stability": self.head_stability,
        }
        total = sum(raw.values()) or 1.0
        return {k: v / total for k, v in raw.items()}


@dataclass
class RecommendationRule:
    metric: str
    below: int
    message: str


@dataclass
class ExpectedRange:
    min: float | None = None
    ideal: float | None = None
    max: float | None = None


@dataclass
class TuningProfile:
    version: str = "1.0"
    shot_type: str = "full_swing"
    club: str = "iron_7"
    club_category: str = "irons"
    validation: ValidationTuning = field(default_factory=ValidationTuning)
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)
    recommendation_rules: list[RecommendationRule] = field(default_factory=list)
    expected_ranges: dict[str, ExpectedRange] = field(default_factory=dict)
    metrics_focus: list[str] = field(default_factory=list)

    @property
    def profile_id(self) -> str:
        return f"{self.shot_type}:{self.club}"

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "shot_type": self.shot_type,
            "club": self.club,
            "club_category": self.club_category,
            "profile_id": self.profile_id,
            "metrics_focus": self.metrics_focus,
        }
