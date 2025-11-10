"""Density heuristics and auto-disable logic for masks.

Determines appropriate mask density based on puzzle characteristics.
"""


def should_auto_disable_mask(size: int, difficulty: str) -> bool:
    """Check if mask should be auto-disabled for given parameters.
    
    Args:
        size: Grid size
        difficulty: Difficulty level (easy, medium, hard, extreme)
        
    Returns:
        True if mask should be disabled
    """
    # Auto-disable for small sizes
    if size < 6:
        return True
    
    # Auto-disable for easy difficulty (unless forced)
    if difficulty and difficulty == "easy":
        return True
    
    return False


def compute_density_heuristic(size: int, difficulty: str) -> float:
    """Compute recommended mask density based on size and difficulty.
    
    Args:
        size: Grid size
        difficulty: Difficulty level
        
    Returns:
        Recommended density (fraction 0.0-0.10)
    """
    # Base density by difficulty
    if difficulty == "easy":
        base = 0.01
    elif difficulty == "medium":
        base = 0.025
    elif difficulty == "hard":
        base = 0.05
    elif difficulty == "extreme":
        base = 0.08
    else:
        base = 0.03  # Default
    
    # Scale by size (larger boards can handle slightly more)
    if size >= 9:
        scale = 1.2
    elif size >= 7:
        scale = 1.0
    else:
        scale = 0.8
    
    density = base * scale
    
    # Clamp to max 10%
    return min(density, 0.10)


def select_default_pattern(size: int, difficulty: str) -> str:
    """Select default pattern based on puzzle characteristics.
    
    Args:
        size: Grid size
        difficulty: Difficulty level
        
    Returns:
        Pattern name (corridor, ring, spiral, cross)
    """
    # Larger boards benefit from corridors
    if size >= 8:
        return "corridor"
    
    # Medium boards work well with rings
    if size == 7:
        return "ring"
    
    # Smaller boards use cross
    return "cross"
