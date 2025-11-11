"""
Size and difficulty-aware anchor policies for puzzle generation.

Constitution compliance: pure policy logic, no I/O.
"""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class AnchorPolicy:
    """Policy for anchor retention during clue removal."""
    difficulty: str  # easy | medium | hard
    size_tier: str  # small | medium | large | very_large
    retain_endpoints: bool = True
    max_turn_anchors: int = 0
    soft_turn_allowed: bool = False


def get_anchor_policy(difficulty: str, size: int) -> AnchorPolicy:
    """
    Get anchor policy based on difficulty and board size.
    
    Constitution principle: Endpoints always retained.
    
    Args:
        difficulty: easy, medium, or hard
        size: Board dimension (e.g., 5 for 5x5)
        
    Returns:
        Anchor policy for this puzzle profile
    """
    # Determine size tier
    cells = size * size
    if cells <= 25:
        size_tier = "small"
    elif cells <= 64:
        size_tier = "medium"
    elif cells <= 100:
        size_tier = "large"
    else:
        size_tier = "very_large"
    
    # Apply difficulty rules
    if difficulty == "easy":
        # Easy: endpoints + 2-3 evenly spaced turns (size-dependent)
        max_turns = max(2, min(3, size // 2))
        return AnchorPolicy(difficulty, size_tier, True, max_turns, False)
    elif difficulty == "medium":
        # Medium: endpoints + at most 1 soft turn (removable if spacing ok)
        return AnchorPolicy(difficulty, size_tier, True, 1, True)
    else:  # hard
        # Hard: endpoints only; extra turns only as repair
        return AnchorPolicy(difficulty, size_tier, True, 0, False)


def select_anchor_positions(path: List[Tuple[int, int]], policy: AnchorPolicy) -> List[int]:
    """
    Select which path indices should be anchor clues.
    
    Args:
        path: Full solution path as list of (row, col)
        policy: Anchor policy
        
    Returns:
        List of indices in path that should be anchored
    """
    anchors = []
    
    # Always keep endpoints
    if policy.retain_endpoints:
        anchors.append(0)
        anchors.append(len(path) - 1)
    
    # Add turn anchors based on policy
    # TODO: Implement turn detection and spacing logic
    
    return sorted(set(anchors))
