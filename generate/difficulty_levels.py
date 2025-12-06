"""Centralized helpers for new clue-based difficulty tiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

# Clue threshold used to separate the two primary buckets.
CLASSIC_CLUE_MIN = 11

# Percentile-based split points for the classic/expert sub-levels.
CLASSIC_LEVEL_SPLITS = (0.377100, 0.481863)
EXPERT_LEVEL_SPLITS = (0.876640, 1.217636)


@dataclass(frozen=True)
class DifficultyThresholds:
    """Configuration for mapping puzzles into intermediate levels."""

    classic: Tuple[float, float] = CLASSIC_LEVEL_SPLITS
    expert: Tuple[float, float] = EXPERT_LEVEL_SPLITS

    def as_metadata(self) -> Dict[str, Dict[str, float]]:
        """Serialize to a JSON-friendly dict."""
        return {
            "classic": {"p33": self.classic[0], "p66": self.classic[1]},
            "expert": {"p33": self.expert[0], "p66": self.expert[1]},
        }


DEFAULT_THRESHOLDS = DifficultyThresholds()


def classify_primary_difficulty(clue_count: int, classic_min: int = CLASSIC_CLUE_MIN) -> str:
    """Return 'classic' if clue_count >= threshold, else 'expert'."""
    return "classic" if clue_count >= classic_min else "expert"


def compute_difficulty_scores(
    clue_count: int,
    search_ratio: float | None,
    average_branching_factor: float | None,
) -> tuple[float, float]:
    """Compute the heuristic difficulty scores for downstream tooling."""
    search_ratio = search_ratio or 0.0
    average_branching_factor = average_branching_factor or 0.0
    difficulty_score_2 = search_ratio + (average_branching_factor / 200.0)
    difficulty_score_1 = (1 - (clue_count / 12.0)) + difficulty_score_2
    return difficulty_score_1, difficulty_score_2


def assign_intermediate_level(
    primary_label: str,
    difficulty_score_1: float,
    thresholds: DifficultyThresholds = DEFAULT_THRESHOLDS,
) -> int:
    """Map the composite score to a 1-3 level within the primary bucket."""
    splits = thresholds.classic if primary_label == "classic" else thresholds.expert
    lower, upper = splits
    if difficulty_score_1 <= lower:
        return 1
    if difficulty_score_1 <= upper:
        return 2
    return 3


def difficulty_metadata_payload(thresholds: DifficultyThresholds = DEFAULT_THRESHOLDS) -> Dict[str, object]:
    """Return metadata describing how difficulty levels are derived."""
    return {
        "primary_split": {
            "metric": "clue_count",
            "classic_min_clues": CLASSIC_CLUE_MIN,
        },
        "intermediate_levels": {
            "metric": "difficulty_score_1",
            "thresholds": thresholds.as_metadata(),
        },
        "scores": {
            "difficulty_score_1": "(1 - clue_count/12) + search_ratio + average_branching_factor/200",
            "difficulty_score_2": "search_ratio + average_branching_factor/200",
        },
    }
