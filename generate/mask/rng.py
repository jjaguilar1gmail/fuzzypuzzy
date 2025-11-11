"""Reproducible RNG utilities for mask generation."""
from util.rng import RNG


def make_mask_rng(base_seed: int, size: int, difficulty: str, attempt_idx: int) -> RNG:
    """Create deterministic RNG for mask generation.
    
    Args:
        base_seed: Original puzzle generation seed
        size: Grid size
        difficulty: Difficulty level string
        attempt_idx: Current generation attempt number
        
    Returns:
        RNG instance seeded deterministically
    """
    # Combine parameters into stable seed
    difficulty_val = hash(difficulty) & 0xFFFFFF
    combined = (base_seed ^ size ^ difficulty_val ^ attempt_idx) & 0x7FFFFFFF
    return RNG(combined)
