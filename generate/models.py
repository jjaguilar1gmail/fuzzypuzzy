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
    # T002: Smart path mode configuration (placeholders)
    allow_partial_paths: bool = False
    min_cover_ratio: float = 0.85
    path_time_ms: Optional[int] = None  # None = auto tiered by size
    # T046: Adaptive anchor policy configuration
    anchor_policy_name: str = "adaptive_v1"
    adaptive_turn_anchors: bool = True
    anchor_counts: Optional[dict] = None  # Per-difficulty overrides
    anchor_tolerance: float = 0.0  # Future tuning parameter
    # T16: Solver-driven pruning configuration
    pruning_enabled: bool = True
    pruning_max_repairs: int = 2
    # Target density ranges by difficulty
    pruning_target_density_easy_min: float = 0.50
    pruning_target_density_easy_max: float = 1.00
    pruning_target_density_medium_min: float = 0.35
    pruning_target_density_medium_max: float = 0.50
    pruning_target_density_hard_min: float = 0.24
    pruning_target_density_hard_max: float = 0.32
    pruning_linear_fallback_k: int = 6
    pruning_alternates_count: int = 5
    pruning_repair_topn: int = 5
    # T002: Mask-driven blocking configuration
    mask_enabled: bool = False
    mask_mode: str = "auto"  # "auto" | "template" | "procedural"
    mask_template: Optional[str] = None  # e.g., "corridor", "ring", "spiral"
    mask_density: Optional[float] = None  # None = auto heuristic
    mask_max_attempts: int = 5
    # T002: Ambiguity-aware structural repair configuration
    structural_repair_enabled: bool = False
    structural_repair_max: int = 2
    structural_repair_timeout_ms: int = 400
    
    def __post_init__(self):
        """Validate configuration."""
        if self.size < 2 or self.size > 9:
            raise ValueError(f"Size must be between 2 and 9, got {self.size}")
        if self.difficulty and self.difficulty not in ['easy', 'medium', 'hard', 'extreme']:
            raise ValueError(f"Invalid difficulty: {self.difficulty}")
        if self.percent_fill and (self.percent_fill < 0.0 or self.percent_fill > 1.0):
            raise ValueError(f"percent_fill must be 0.0-1.0, got {self.percent_fill}")
        # T009: Validate new path config
        if self.min_cover_ratio < 0.5 or self.min_cover_ratio > 1.0:
            raise ValueError(f"min_cover_ratio must be 0.5-1.0, got {self.min_cover_ratio}")
        if self.path_time_ms is not None and self.path_time_ms < 100:
            raise ValueError(f"path_time_ms must be >= 100ms, got {self.path_time_ms}")
        # T046: Validate anchor policy config
        if self.anchor_policy_name not in ['adaptive_v1', 'legacy']:
            raise ValueError(f"anchor_policy_name must be 'adaptive_v1' or 'legacy', got {self.anchor_policy_name}")
        if self.anchor_tolerance < 0.0:
            raise ValueError(f"anchor_tolerance must be >= 0.0, got {self.anchor_tolerance}")
        # T16: Validate pruning config
        if self.pruning_max_repairs < 0:
            raise ValueError(f"pruning_max_repairs must be >= 0, got {self.pruning_max_repairs}")
        # Easy
        if not (0.3 <= self.pruning_target_density_easy_min <= 1.0):
            raise ValueError(f"pruning_target_density_easy_min must be 0.3-1.0, got {self.pruning_target_density_easy_min}")
        if not (0.3 <= self.pruning_target_density_easy_max <= 1.0):
            raise ValueError(f"pruning_target_density_easy_max must be 0.3-1.0, got {self.pruning_target_density_easy_max}")
        if self.pruning_target_density_easy_min >= self.pruning_target_density_easy_max:
            raise ValueError(f"pruning_target_density_easy_min must be < max")
        # Medium
        if not (0.2 <= self.pruning_target_density_medium_min <= 0.8):
            raise ValueError(f"pruning_target_density_medium_min must be 0.2-0.8, got {self.pruning_target_density_medium_min}")
        if not (0.2 <= self.pruning_target_density_medium_max <= 0.8):
            raise ValueError(f"pruning_target_density_medium_max must be 0.2-0.8, got {self.pruning_target_density_medium_max}")
        if self.pruning_target_density_medium_min >= self.pruning_target_density_medium_max:
            raise ValueError(f"pruning_target_density_medium_min must be < max")
        # Hard
        if not (0.1 <= self.pruning_target_density_hard_min <= 0.5):
            raise ValueError(f"pruning_target_density_hard_min must be 0.1-0.5, got {self.pruning_target_density_hard_min}")
        if not (0.1 <= self.pruning_target_density_hard_max <= 0.9):
            raise ValueError(f"pruning_target_density_hard_max must be 0.1-0.9, got {self.pruning_target_density_hard_max}")
        if self.pruning_target_density_hard_min >= self.pruning_target_density_hard_max:
            raise ValueError(f"pruning_target_density_hard_min must be < max")
        if self.pruning_linear_fallback_k < 1:
            raise ValueError(f"pruning_linear_fallback_k must be >= 1, got {self.pruning_linear_fallback_k}")
        if self.pruning_alternates_count < 1:
            raise ValueError(f"pruning_alternates_count must be >= 1, got {self.pruning_alternates_count}")
        if self.pruning_repair_topn < 1:
            raise ValueError(f"pruning_repair_topn must be >= 1, got {self.pruning_repair_topn}")
        # T002: Validate mask config
        if self.mask_mode not in ['auto', 'template', 'procedural']:
            raise ValueError(f"mask_mode must be 'auto', 'template', or 'procedural', got {self.mask_mode}")
        if self.mask_density is not None and (self.mask_density < 0.0 or self.mask_density > 0.10):
            raise ValueError(f"mask_density must be 0.0-0.10, got {self.mask_density}")
        if self.mask_max_attempts < 1:
            raise ValueError(f"mask_max_attempts must be >= 1, got {self.mask_max_attempts}")
        if self.structural_repair_max < 0:
            raise ValueError(f"structural_repair_max must be >= 0, got {self.structural_repair_max}")
        if self.structural_repair_timeout_ms < 100:
            raise ValueError(f"structural_repair_timeout_ms must be >= 100ms, got {self.structural_repair_timeout_ms}")


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
    # US1: Mask metrics
    mask_metrics: Optional[dict] = None
    # US2: Repair metrics
    repair_metrics: Optional[dict] = None
    
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
            "mask_metrics": self.mask_metrics,
            "repair_metrics": self.repair_metrics,
            "version": self.version,
        }
