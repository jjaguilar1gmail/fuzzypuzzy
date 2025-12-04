#!/usr/bin/env python3
"""Utility to recompute percentile-based difficulty splits for any pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from generate.difficulty_levels import DifficultyThresholds, assign_intermediate_level


def _percentile(values: List[float], pct: float) -> float:
    """Return the interpolated percentile for a sorted list."""
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * pct
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] * (c - k) + values[c] * (k - f)


def _load_scores(puzzles_dir: Path) -> Dict[str, List[float]]:
    """Load difficulty_score_1 values keyed by difficulty."""
    scores: Dict[str, List[float]] = {}
    for puzzle_file in sorted(puzzles_dir.glob("*.json")):
        data = json.loads(puzzle_file.read_text(encoding="utf-8"))
        label = data.get("difficulty")
        score = data.get("difficulty_score_1")
        if label and score is not None:
            scores.setdefault(label, []).append(score)
    return scores


def _apply_levels(puzzles_dir: Path, thresholds: DifficultyThresholds) -> None:
    """Rewrite puzzles with updated intermediate levels."""
    for puzzle_file in sorted(puzzles_dir.glob("*.json")):
        data = json.loads(puzzle_file.read_text(encoding="utf-8"))
        label = data.get("difficulty")
        score = data.get("difficulty_score_1")
        if label is None or score is None:
            continue
        level = assign_intermediate_level(label, score, thresholds)
        if data.get("intermediate_level") != level:
            data["intermediate_level"] = level
            puzzle_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        required=True,
        help="Path to the pack directory containing metadata.json and puzzles/.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite puzzle files with the recomputed intermediate levels.",
    )
    args = parser.parse_args()

    pack_path = Path(args.pack)
    puzzles_dir = pack_path / "puzzles"
    if not puzzles_dir.exists():
        raise SystemExit(f"No puzzles/ directory at {puzzles_dir}")

    scores = _load_scores(puzzles_dir)
    if not scores:
        raise SystemExit("No difficulty_score_1 values found.")

    summary: Dict[str, Tuple[float, float]] = {}
    for label, values in scores.items():
        p33 = _percentile(values, 0.33)
        p66 = _percentile(values, 0.66)
        summary[label] = (p33, p66)

    print("Difficulty split percentiles:")
    for label, (p33, p66) in summary.items():
        print(f"  {label}: p33={p33:.6f}, p66={p66:.6f} (n={len(scores[label])})")

    if args.apply:
        thresholds = DifficultyThresholds(
            classic=summary.get("classic", DifficultyThresholds().classic),
            expert=summary.get("expert", DifficultyThresholds().expert),
        )
        _apply_levels(puzzles_dir, thresholds)
        print("Updated intermediate_level fields using the new thresholds.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
