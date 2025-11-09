"""Generate module: Models

Data models for puzzle generation.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GenerationConfig:
    """Configuration for puzzle generation."""
    size: int
    allow_diagonal: bool = True
    blocked: Optional[list[tuple[int, int]]] = None
    difficulty: Optional[str] = None
    percent_fill: Optional[float] = None
    seed: Optional[int] = None
    path_mode: str = "serpentine"
    clue_mode: str = "anchor_removal_v1"
    symmetry: Optional[str] = None
    turn_anchors: bool = True
    timeout_ms: int = 5000
    max_attempts: int = 5
    uniqueness_node_cap: int = 1000
    uniqueness_timeout_ms: int = 2000
    
    def __post_init__(self):
        """Validate configuration."""
        if self.size < 2 or self.size > 9:
            raise ValueError(f"Size must be between 2 and 9, got {self.size}")
        if self.difficulty and self.difficulty not in ['easy', 'medium', 'hard', 'extreme']:
            raise ValueError(f"Invalid difficulty: {self.difficulty}")
        if self.percent_fill and (self.percent_fill < 0.0 or self.percent_fill > 1.0):
            raise ValueError(f"percent_fill must be 0.0-1.0, got {self.percent_fill}")


@dataclass
class UniquenessCheckResult:
    """Result of uniqueness verification."""
    is_unique: bool
    solutions_found: int
    nodes: int
    depth: int
    elapsed_ms: int


@dataclass
class DifficultyProfile:
    """Difficulty band profile definition."""
    name: str
    clue_density_min: float
    clue_density_max: float
    max_search_depth: int
    expected_max_nodes: int
    metrics_thresholds: dict = field(default_factory=dict)


@dataclass
class GeneratedPuzzle:
    """Complete generated puzzle with metadata."""
    size: int
    allow_diagonal: bool
    blocked_cells: list[tuple[int, int]]
    givens: list[tuple[int, int, int]]  # (row, col, value)
    solution: list[tuple[int, int, int]]  # full grid values
    difficulty_label: str
    difficulty_score: float
    clue_count: int
    uniqueness_verified: bool
    attempts_used: int
    seed: int
    path_mode: str
    clue_mode: str
    symmetry: Optional[str]
    timings_ms: dict
    solver_metrics: dict
    version: str = "1.0"
    
    def to_json(self):
        """Serialize to dict for JSON export."""
        return {
            "size": self.size,
            "allow_diagonal": self.allow_diagonal,
            "blocked_cells": sorted(self.blocked_cells),
            "givens": sorted(self.givens),
            "solution": sorted(self.solution),
            "difficulty_label": self.difficulty_label,
            "difficulty_score": self.difficulty_score,
            "clue_count": self.clue_count,
            "uniqueness_verified": self.uniqueness_verified,
            "attempts_used": self.attempts_used,
            "seed": self.seed,
            "path_mode": self.path_mode,
            "clue_mode": self.clue_mode,
            "symmetry": self.symmetry,
            "timings_ms": self.timings_ms,
            "solver_metrics": self.solver_metrics,
            "version": self.version,
        }
