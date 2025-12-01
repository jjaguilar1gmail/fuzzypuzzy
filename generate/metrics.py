"""Utility helpers for structural and solver-derived metrics."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List, Sequence, Tuple

from core.position import Position


@dataclass(frozen=True)
class StructuralInputs:
    """Lightweight bundle of inputs required to compute structural metrics."""

    size: int
    givens: Sequence[Tuple[int, int, int]]
    path: Sequence[Position]
    anchor_positions: Sequence[Tuple[int, int]]
    solver_metrics: dict


def _compute_givens_distribution(size: int, givens: Sequence[Tuple[int, int, int]]) -> dict:
    """Calculate row/column/quadrant clue distributions."""
    row_counts = [0] * size
    col_counts = [0] * size
    quadrant_counts = {
        "top_left": 0,
        "top_right": 0,
        "bottom_left": 0,
        "bottom_right": 0,
    }
    half = size / 2

    for row, col, _ in givens:
        if 0 <= row < size:
            row_counts[row] += 1
        if 0 <= col < size:
            col_counts[col] += 1

        quadrant_row = "top" if row < half else "bottom"
        quadrant_col = "left" if col < half else "right"
        quadrant_key = f"{quadrant_row}_{quadrant_col}"
        quadrant_counts[quadrant_key] += 1

    return {
        "row_counts": row_counts,
        "column_counts": col_counts,
        "quadrants": quadrant_counts,
    }


def _compute_anchor_spacing(
    path: Sequence[Position],
    anchor_positions: Sequence[Tuple[int, int]],
) -> dict:
    """Compute spacing statistics for anchors along the solution path."""
    if not anchor_positions:
        return {
            "count": 0,
            "density": 0.0,
            "gaps": {"min": None, "max": None, "avg": None},
        }

    path_lookup = {(pos.row, pos.col): idx for idx, pos in enumerate(path)}
    anchor_indices: List[int] = []
    for row, col in anchor_positions:
        if (row, col) in path_lookup:
            anchor_indices.append(path_lookup[(row, col)])

    anchor_indices = sorted(set(anchor_indices))
    if not anchor_indices:
        return {
            "count": 0,
            "density": 0.0,
            "gaps": {"min": None, "max": None, "avg": None},
        }

    gaps = [
        anchor_indices[i + 1] - anchor_indices[i]
        for i in range(len(anchor_indices) - 1)
    ]

    density = len(anchor_indices) / max(len(path), 1)
    gap_stats = {
        "min": min(gaps) if gaps else None,
        "max": max(gaps) if gaps else None,
        "avg": mean(gaps) if gaps else None,
    }
    return {
        "count": len(anchor_indices),
        "density": round(density, 4),
        "gaps": gap_stats,
    }


def _compute_branching_stats(solver_metrics: dict) -> dict:
    """Estimate branching behavior from solver metrics."""
    nodes = solver_metrics.get("nodes", 0)
    depth = solver_metrics.get("depth", 0)
    steps = solver_metrics.get("steps", 0)
    logic_ratio = solver_metrics.get("logic_ratio", 1.0)

    avg_branching = nodes / depth if depth else 0.0
    search_ratio = 1.0 - logic_ratio if logic_ratio is not None else None

    return {
        "nodes": nodes,
        "depth": depth,
        "steps": steps,
        "average_branching_factor": round(avg_branching, 4) if avg_branching else 0.0,
        "search_ratio": round(search_ratio, 4) if search_ratio is not None else None,
    }


def build_structural_metrics(inputs: StructuralInputs) -> dict:
    """Compute derived structural metrics for export."""
    givens_distribution = _compute_givens_distribution(inputs.size, inputs.givens)
    anchor_spacing = _compute_anchor_spacing(inputs.path, inputs.anchor_positions)
    branching = _compute_branching_stats(inputs.solver_metrics or {})

    return {
        "givens": {
            "total": len(inputs.givens),
            "density": inputs.solver_metrics.get("clue_density"),
            **givens_distribution,
        },
        "anchors": anchor_spacing,
        "branching": branching,
    }
