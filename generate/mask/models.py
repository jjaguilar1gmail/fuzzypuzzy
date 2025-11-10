"""Data models for mask generation."""
from dataclasses import dataclass
from typing import Optional
from core.position import Position


@dataclass
class BlockMask:
    """Represents blocked cells applied before path generation.
    
    Attributes:
        grid_size: Size of the grid (NxN)
        cells: Set of blocked positions
        density: Fraction of total cells blocked
        pattern_id: Identifier for pattern type (e.g., "corridor", "ring")
        attempt_index: Which generation attempt produced this mask
        seed: Random seed used for generation
    """
    grid_size: int
    cells: set[tuple[int, int]]
    density: float
    pattern_id: str
    attempt_index: int
    seed: int
    
    def signature(self) -> str:
        """Stable hash for transposition table keying."""
        sorted_cells = sorted(self.cells)
        return f"{self.grid_size}:{','.join(f'{r},{c}' for r, c in sorted_cells)}"


@dataclass
class MaskPattern:
    """Template or procedural mask generation parameters.
    
    Attributes:
        name: Pattern identifier
        type: "template" or "procedural"
        min_size: Minimum grid size for this pattern
        max_density: Maximum allowed density
        params: Additional pattern-specific parameters
    """
    name: str
    type: str  # "template" | "procedural"
    min_size: int
    max_density: float
    params: dict
    
    def generate(self, size: int, rng) -> BlockMask:
        """Generate a mask using this pattern.
        
        This is a placeholder - actual implementation in pattern modules.
        """
        raise NotImplementedError("Pattern generation in specialized modules")
