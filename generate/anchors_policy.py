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
    if policy.max_turn_anchors > 0:
        turn_indices = _find_turns(path)
        selected_turns = _select_spaced_turns(
            turn_indices,
            policy.max_turn_anchors,
            policy.difficulty,
            len(path)
        )
        anchors.extend(selected_turns)
    
    return sorted(set(anchors))


def _find_turns(path: List[Tuple[int, int]]) -> List[int]:
    """
    Find all turn positions in path where direction changes.
    
    Args:
        path: Solution path as list of (row, col) tuples
        
    Returns:
        List of path indices where turns occur
    """
    if len(path) < 3:
        return []
    
    turns = []
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        next_pos = path[i + 1]
        
        # Calculate direction vectors
        dr1 = curr[0] - prev[0]
        dc1 = curr[1] - prev[1]
        dr2 = next_pos[0] - curr[0]
        dc2 = next_pos[1] - curr[1]
        
        # Turn detected if direction changes
        if (dr1, dc1) != (dr2, dc2):
            turns.append(i)
    
    return turns


def _select_spaced_turns(
    turn_indices: List[int],
    max_count: int,
    difficulty: str,
    path_length: int
) -> List[int]:
    """
    Select evenly spaced turns from available turn positions.
    
    Args:
        turn_indices: Available turn indices
        max_count: Maximum turns to select
        difficulty: Puzzle difficulty (affects spacing)
        path_length: Total path length
        
    Returns:
        Selected turn indices
    """
    if not turn_indices or max_count == 0:
        return []
    
    # Calculate minimum spacing based on difficulty
    # Easy: more lenient spacing, Medium/Hard: stricter
    if difficulty == "easy":
        min_gap = max(3, path_length // (max_count + 2))
    else:
        min_gap = max(5, path_length // (max_count + 1))
    
    selected = []
    last_index = -min_gap - 1  # Allow first turn to be selected
    
    for idx in turn_indices:
        if len(selected) >= max_count:
            break
        
        if idx - last_index >= min_gap:
            selected.append(idx)
            last_index = idx
    
    return selected

