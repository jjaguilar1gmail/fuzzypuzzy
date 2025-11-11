"""Metrics structures for ambiguity repair."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RepairMetrics:
    """Metrics captured during ambiguity repair.
    
    Attributes:
        enabled: Whether structural repair was enabled
        attempts: Total repair attempts made
        structural_blocks_applied: Number of structural blocks successfully placed
        clue_fallbacks_used: Number of times clue repair was used as fallback
        ambiguity_regions_detected: Number of distinct ambiguity regions found
        uniqueness_restored: Whether uniqueness was successfully restored
        repair_time_ms: Time spent on repair operations
    """
    enabled: bool = False
    attempts: int = 0
    structural_blocks_applied: int = 0
    clue_fallbacks_used: int = 0
    ambiguity_regions_detected: int = 0
    uniqueness_restored: bool = False
    repair_time_ms: float = 0.0
