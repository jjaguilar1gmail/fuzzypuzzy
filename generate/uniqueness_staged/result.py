"""Result types for staged uniqueness validation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.puzzle import Puzzle


class UniquenessDecision(Enum):
    """Tri-state uniqueness decision."""
    UNIQUE = "unique"
    NON_UNIQUE = "non_unique"
    INCONCLUSIVE = "inconclusive"


@dataclass
class UniquenessCheckRequest:
    """Request for uniqueness validation.
    
    Attributes:
        puzzle: Puzzle object to check
        size: Grid size
        adjacency: Adjacency mode (4 or 8 neighbors)
        difficulty: Difficulty level
        total_budget_ms: Total time budget across all stages
        stage_budget_split: Budget allocation per stage
        seed: Random seed for reproducibility
        strategy_flags: Enable/disable flags per stage
    """
    
    puzzle: 'Puzzle'  # Type hint as string to avoid circular import
    size: int
    adjacency: int = 8
    difficulty: str = "medium"
    total_budget_ms: int = 500
    stage_budget_split: Dict[str, float] = field(default_factory=lambda: {
        'early_exit': 0.4,
        'probes': 0.4,
        'sat': 0.2
    })
    seed: int = 0
    strategy_flags: Dict[str, bool] = field(default_factory=lambda: {
        'early_exit': True,
        'probes': True,
        'sat': False
    })
    
    def __post_init__(self):
        """Validate request after initialization."""
        if self.total_budget_ms <= 0:
            raise ValueError(f"total_budget_ms must be > 0, got {self.total_budget_ms}")
        
        if self.size <= 0:
            raise ValueError(f"size must be > 0, got {self.size}")
        
        if self.adjacency not in {4, 8}:
            raise ValueError(f"adjacency must be 4 or 8, got {self.adjacency}")


@dataclass
class UniquenessCheckResult:
    """Result from uniqueness validation.
    
    Attributes:
        decision: Unique, Non-Unique, or Inconclusive
        stage_decided: Name of stage that made the decision
        elapsed_ms: Total elapsed time
        per_stage_ms: Time spent per stage
        nodes_explored: Nodes explored per stage
        probes_run: Number of probes executed
        notes: Additional context or reasons
    """
    
    decision: UniquenessDecision
    stage_decided: str
    elapsed_ms: int
    per_stage_ms: Dict[str, int] = field(default_factory=dict)
    nodes_explored: Dict[str, int] = field(default_factory=dict)
    probes_run: int = 0
    notes: str = ""
    
    @property
    def is_unique(self) -> bool:
        """Convenience property for Unique decision."""
        return self.decision == UniquenessDecision.UNIQUE
    
    @property
    def is_non_unique(self) -> bool:
        """Convenience property for Non-Unique decision."""
        return self.decision == UniquenessDecision.NON_UNIQUE
    
    @property
    def is_inconclusive(self) -> bool:
        """Convenience property for Inconclusive decision."""
        return self.decision == UniquenessDecision.INCONCLUSIVE


@dataclass
class StrategyProfile:
    """Configuration for a uniqueness checking strategy.
    
    Attributes:
        id: Unique strategy identifier
        enabled: Whether this strategy is active
        budget_share: Fraction of total budget allocated
        params: Strategy-specific parameters
        capabilities: What this strategy can detect
    """
    
    id: str
    enabled: bool = True
    budget_share: float = 0.0
    params: Dict[str, any] = field(default_factory=dict)
    capabilities: set = field(default_factory=lambda: {'detect_non_unique'})
    
    def __post_init__(self):
        """Validate profile after initialization."""
        if not (0.0 <= self.budget_share <= 1.0):
            raise ValueError(f"budget_share must be in [0,1], got {self.budget_share}")


def aggregate_metrics(results: list[UniquenessCheckResult]) -> Dict[str, any]:
    """Aggregate metrics from multiple uniqueness check results.
    
    Args:
        results: List of results to aggregate
        
    Returns:
        Dictionary with aggregated statistics
    """
    if not results:
        return {}
    
    total_time = sum(r.elapsed_ms for r in results)
    total_nodes = sum(sum(r.nodes_explored.values()) for r in results)
    total_probes = sum(r.probes_run for r in results)
    
    decisions = {
        'unique': sum(1 for r in results if r.is_unique),
        'non_unique': sum(1 for r in results if r.is_non_unique),
        'inconclusive': sum(1 for r in results if r.is_inconclusive)
    }
    
    return {
        'total_checks': len(results),
        'total_time_ms': total_time,
        'avg_time_ms': total_time / len(results),
        'total_nodes': total_nodes,
        'total_probes': total_probes,
        'decisions': decisions
    }
