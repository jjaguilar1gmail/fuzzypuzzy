"""Configuration for staged uniqueness validation."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class UniquenessConfig:
    """Configuration for staged uniqueness checking.
    
    Attributes:
        size: Puzzle size (e.g., 7 for 7x7)
        difficulty: Target difficulty level
        total_budget_ms: Total wall-time budget across all stages
        stage_budget_split: Percentage allocation per stage (must sum to 1.0)
        seed: Random seed for reproducibility
        strategy_flags: Enable/disable flags for each stage
    """
    
    size: int
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
        'sat': False  # Disabled by default per FR-012
    })
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.total_budget_ms <= 0:
            raise ValueError(f"total_budget_ms must be > 0, got {self.total_budget_ms}")
        
        # Validate budget split sums to 1.0 (within tolerance)
        total = sum(self.stage_budget_split.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"stage_budget_split must sum to 1.0, got {total}")
        
        # Validate difficulty
        valid_difficulties = {'easy', 'medium', 'hard'}
        if self.difficulty not in valid_difficulties:
            raise ValueError(f"difficulty must be one of {valid_difficulties}, got {self.difficulty}")
    
    @classmethod
    def from_difficulty(cls, size: int, difficulty: str, seed: int = 0) -> 'UniquenessConfig':
        """Create config with default budgets for given difficulty.
        
        Per FR-014:
        - Easy: 600 ms
        - Medium: 500 ms  
        - Hard: 400 ms
        
        Small boards (≤5x5): 100 ms enumeration target
        """
        if size <= 5:
            budget_ms = 100
        else:
            budget_map = {
                'easy': 600,
                'medium': 500,
                'hard': 400
            }
            budget_ms = budget_map.get(difficulty, 500)
        
        return cls(
            size=size,
            difficulty=difficulty,
            total_budget_ms=budget_ms,
            seed=seed
        )
    
    def validate_budget_allocation(self) -> None:
        """Validate that budget split is reasonable.
        
        Note: It's acceptable for disabled stages to have budget allocation
        since they'll just be skipped. This method only validates that the
        budget split sums to approximately 1.0.
        
        Raises:
            ValueError: If budget split doesn't sum to 1.0 (within tolerance)
        """
        total = sum(self.stage_budget_split.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"stage_budget_split must sum to 1.0, got {total}"
            )
    
    def get_stage_budget(self, stage_name: str) -> int:
        """Calculate actual time budget for a specific stage.
        
        Args:
            stage_name: Name of stage ('early_exit', 'probes', 'sat')
            
        Returns:
            Budget in milliseconds for this stage
            
        Raises:
            KeyError: If stage name is unknown
        """
        if stage_name not in self.stage_budget_split:
            raise KeyError(f"Unknown stage: {stage_name}")
        
        budget_share = self.stage_budget_split[stage_name]
        return int(self.total_budget_ms * budget_share)

