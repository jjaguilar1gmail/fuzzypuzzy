"""Data models for ambiguity repair."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AmbiguityRegion:
    """Cluster of cells where divergent solutions differ.
    
    Attributes:
        cells: Set of positions in this ambiguity region
        divergence_count: Number of distinct solution paths touching region
        corridor_width: Computed width via flood (lower = more constrained)
        distance_from_clues: Minimum Manhattan distance to any clue
        score: Calculated priority score for blocking
    """
    cells: set[tuple[int, int]]
    divergence_count: int = 0
    corridor_width: int = 0
    distance_from_clues: int = 0
    score: float = 0.0


@dataclass
class RepairAction:
    """Structural modification attempt during uniqueness repair.
    
    Attributes:
        action_type: "block" or "clue"
        position: Target cell (row, col)
        reason: Human-readable explanation
        applied: Whether action was successfully applied
    """
    action_type: str  # "block" | "clue"
    position: tuple[int, int]
    reason: str
    applied: bool = False
