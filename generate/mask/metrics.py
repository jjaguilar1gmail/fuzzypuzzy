"""Metrics structures for mask generation."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MaskGenerationMetrics:
    """Metrics captured during mask generation.
    
    Attributes:
        pattern_id: Pattern identifier used
        cells_count: Number of cells blocked
        density: Fraction of grid blocked
        attempts: Number of generation attempts
        validation_time_ms: Time spent validating mask
        selected: Whether mask was successfully applied
    """
    pattern_id: Optional[str] = None
    cells_count: int = 0
    density: float = 0.0
    attempts: int = 0
    validation_time_ms: int = 0
    selected: bool = False
