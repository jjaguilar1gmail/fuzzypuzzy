"""Generate module: Anchor Policy

Adaptive turn anchor selection by difficulty.
Implements adaptive_v1 policy and legacy fallback.
"""
from dataclasses import dataclass, field
from typing import Optional
from core.position import Position
from util.rng import RNG


# Anchor kind constants (using strings to stay stdlib-only)
ANCHOR_KIND_HARD = "hard"
ANCHOR_KIND_SOFT = "soft"
ANCHOR_KIND_REPAIR = "repair"
ANCHOR_KIND_ENDPOINT = "endpoint"


@dataclass
class AnchorPolicy:
    """Policy configuration for adaptive anchor selection."""
    name: str  # "adaptive_v1" or "legacy"
    easy_range: tuple[int, int] = (2, 3)  # Count of hard anchors beyond endpoints
    medium_soft: bool = True  # Enable single soft anchor
    hard_repairs_enabled: bool = True
    extreme_repairs_enabled: bool = True
    min_index_gap: int = 2  # Minimum path indices between anchors
    prefer_four_neighbor_on_sparse: bool = False  # Future feature
    version: str = "1.0"
    
    def __post_init__(self):
        """Validate policy configuration."""
        if self.easy_range[0] < 0 or self.easy_range[1] < self.easy_range[0]:
            raise ValueError(f"Invalid easy_range: {self.easy_range}")
        if self.min_index_gap < 0:
            raise ValueError(f"min_index_gap must be >= 0, got {self.min_index_gap}")


@dataclass
class TurnAnchor:
    """A position selected as an anchor with metadata."""
    position: Position
    kind: str  # ANCHOR_KIND_HARD | SOFT | REPAIR | ENDPOINT
    reason: str  # "stability" | "option" | "repair" | "endpoints"
    path_index: int = -1  # Index in path for ordering


@dataclass
class AnchorMetrics:
    """Metrics about anchor selection for observability."""
    anchor_count: int
    hard_count: int
    soft_count: int
    repair_count: int
    endpoint_count: int
    positions: list[tuple[int, int]]  # (row, col) tuples
    policy_name: str
    anchor_selection_reason: str  # "policy" | "repair" | "legacy" | "disabled"
    min_index_gap_enforced: bool = False
    adjacency_mode: str = "8"  # "4" or "8"


@dataclass
class UniquenessRepairCandidate:
    """Candidate position for repair anchor placement."""
    segment_start: int  # Path index
    segment_end: int
    branching_factor: int
    midpoint_pos: tuple[int, int]  # (row, col)


@dataclass
class RepairDecision:
    """Decision about repair anchor placement."""
    chosen_pos: tuple[int, int]  # (row, col)
    rationale: str
    branching_factor: int
    alternative_positions: list[tuple[int, int]] = field(default_factory=list)


def get_policy(name: str) -> AnchorPolicy:
    """Get a named anchor policy.
    
    Args:
        name: Policy name ("adaptive_v1" or "legacy")
        
    Returns:
        AnchorPolicy instance
    """
    if name == "adaptive_v1":
        return AnchorPolicy(
            name="adaptive_v1",
            easy_range=(2, 3),
            medium_soft=True,
            hard_repairs_enabled=True,
            extreme_repairs_enabled=True,
            min_index_gap=2,
            version="1.0"
        )
    elif name == "legacy":
        return AnchorPolicy(
            name="legacy",
            easy_range=(4, 4),  # Legacy kept every other turn (approx)
            medium_soft=False,
            hard_repairs_enabled=False,
            extreme_repairs_enabled=False,
            min_index_gap=0,
            version="1.0"
        )
    else:
        raise ValueError(f"Unknown policy name: {name}")


def select_anchors(
    path: list[Position],
    difficulty: str,
    policy: AnchorPolicy,
    symmetry: Optional[str],
    rng: RNG
) -> tuple[list[TurnAnchor], AnchorMetrics]:
    """Select turn anchors based on difficulty and policy.
    
    Args:
        path: Hamiltonian path positions
        difficulty: One of {easy, medium, hard, extreme}
        policy: AnchorPolicy configuration
        symmetry: Optional symmetry mode ("rotational" | "horizontal")
        rng: RNG for deterministic selection
        
    Returns:
        (anchors, metrics) tuple
        
    Raises:
        ValueError: If difficulty is invalid or policy is malformed
    """
    if difficulty not in ['easy', 'medium', 'hard', 'extreme']:
        raise ValueError(f"Invalid difficulty: {difficulty}")
    
    anchors = []
    
    # T048: Always keep endpoints
    anchors.append(TurnAnchor(
        position=path[0],
        kind=ANCHOR_KIND_ENDPOINT,
        reason="endpoints",
        path_index=0
    ))
    anchors.append(TurnAnchor(
        position=path[-1],
        kind=ANCHOR_KIND_ENDPOINT,
        reason="endpoints",
        path_index=len(path) - 1
    ))
    
    # T048: Legacy policy - use all turn points (simplified for now)
    if policy.name == "legacy":
        turn_positions = _find_turn_positions(path)
        
        # Legacy: Keep some turns based on difficulty
        if difficulty == "easy" and len(turn_positions) > 4:
            selected_turns = turn_positions[::2][:4]
        elif difficulty == "medium" and len(turn_positions) > 6:
            selected_turns = turn_positions[::2][:6]
        else:
            selected_turns = turn_positions
        
        for idx, pos in selected_turns:
            anchors.append(TurnAnchor(
                position=pos,
                kind=ANCHOR_KIND_HARD,
                reason="stability",
                path_index=idx
            ))
        
        metrics = _build_metrics(anchors, policy.name, "legacy")
        return anchors, metrics
    
    # T048: Adaptive policy
    turn_positions = _find_turn_positions(path)
    min_gap_enforced = False  # T050: Track if spacing constraint applied
    
    if difficulty == "easy":
        # Easy: Add 2-3 hard turn anchors
        target_count = min(policy.easy_range[1], len(turn_positions))
        target_count = max(policy.easy_range[0], target_count)
        
        selected, gap_enforced = _select_spaced_turns(
            turn_positions,
            target_count,
            policy.min_index_gap,
            len(path)
        )
        min_gap_enforced = gap_enforced
        
        for idx, pos in selected:
            anchors.append(TurnAnchor(
                position=pos,
                kind=ANCHOR_KIND_HARD,
                reason="stability",
                path_index=idx
            ))
    
    elif difficulty == "medium":
        # Medium: Add 1 soft anchor (may be dropped later)
        if policy.medium_soft and len(turn_positions) > 0:
            # Pick a turn near the middle
            mid_turn = turn_positions[len(turn_positions) // 2]
            anchors.append(TurnAnchor(
                position=mid_turn[1],
                kind=ANCHOR_KIND_SOFT,
                reason="option",
                path_index=mid_turn[0]
            ))

    elif difficulty in ["hard", "extreme"]:
        # Hard/extreme: keep up to three spaced turns for structural stability
        if turn_positions:
            target_count = min(2, len(turn_positions))
            # Spread them out along the path
            gap = max(policy.min_index_gap, max(2, len(path) // 6))
            selected, gap_enforced_local = _select_spaced_turns(
                turn_positions,
                target_count,
                gap,
                len(path)
            )
            if gap_enforced_local:
                min_gap_enforced = True
            for idx, pos in selected:
                anchors.append(TurnAnchor(
                    position=pos,
                    kind=ANCHOR_KIND_HARD,
                    reason="stability",
                    path_index=idx
                ))
    
    metrics = _build_metrics(anchors, policy.name, "policy", min_gap_enforced)
    return anchors, metrics


def _find_turn_positions(path: list[Position]) -> list[tuple[int, Position]]:
    """Find all turn points in path where direction changes.
    
    Returns:
        List of (path_index, Position) tuples
    """
    if len(path) < 3:
        return []
    
    turns = []
    for i in range(1, len(path) - 1):
        prev_pos = path[i - 1]
        curr_pos = path[i]
        next_pos = path[i + 1]
        
        dr1 = curr_pos.row - prev_pos.row
        dc1 = curr_pos.col - prev_pos.col
        dr2 = next_pos.row - curr_pos.row
        dc2 = next_pos.col - curr_pos.col
        
        if (dr1, dc1) != (dr2, dc2):
            turns.append((i, curr_pos))
    
    return turns


def _select_spaced_turns(
    turn_positions: list[tuple[int, Position]],
    target_count: int,
    min_gap: int,
    path_length: int
) -> tuple[list[tuple[int, Position]], bool]:
    """Select turns with minimum spacing constraint.
    
    Args:
        turn_positions: Available turn positions with indices
        target_count: Desired number of anchors
        min_gap: Minimum index gap between selected anchors
        path_length: Total path length
        
    Returns:
        (selected_turns, gap_enforced) tuple where gap_enforced indicates
        if any turns were skipped due to spacing constraint
    """
    if not turn_positions or target_count == 0:
        return [], False
    
    selected = []
    last_index = -min_gap - 1  # Allow first turn to be selected
    gap_enforced = False
    
    for idx, pos in turn_positions:
        if len(selected) >= target_count:
            break
        
        if idx - last_index >= min_gap:
            selected.append((idx, pos))
            last_index = idx
        else:
            # T050: Track when turns are skipped due to min_gap
            gap_enforced = True
    
    return selected, gap_enforced


def _build_metrics(
    anchors: list[TurnAnchor],
    policy_name: str,
    selection_reason: str,
    min_gap_enforced: bool = False
) -> AnchorMetrics:
    """Build metrics summary from anchor list."""
    hard_count = sum(1 for a in anchors if a.kind == ANCHOR_KIND_HARD)
    soft_count = sum(1 for a in anchors if a.kind == ANCHOR_KIND_SOFT)
    repair_count = sum(1 for a in anchors if a.kind == ANCHOR_KIND_REPAIR)
    endpoint_count = sum(1 for a in anchors if a.kind == ANCHOR_KIND_ENDPOINT)
    
    positions = [(a.position.row, a.position.col) for a in anchors]
    
    return AnchorMetrics(
        anchor_count=len(anchors),
        hard_count=hard_count,
        soft_count=soft_count,
        repair_count=repair_count,
        endpoint_count=endpoint_count,
        positions=positions,
        policy_name=policy_name,
        anchor_selection_reason=selection_reason,
        min_index_gap_enforced=min_gap_enforced,  # T050: Pass through flag
        adjacency_mode="8"
    )


def evaluate_soft_anchor(puzzle, soft_anchor: TurnAnchor) -> bool:
    """Evaluate whether a soft anchor should be kept.
    
    Args:
        puzzle: Current puzzle state
        soft_anchor: Soft anchor to evaluate
        
    Returns:
        True if anchor should be kept, False if droppable
        
    Note: T049 - Stub implementation; always keeps for now
    """
    # TODO T049: Implement uniqueness check with/without soft anchor
    # For now, keep all soft anchors
    return True


def plan_repair(puzzle, solutions: list) -> Optional[RepairDecision]:
    """Plan repair anchor placement when uniqueness fails.
    
    Args:
        puzzle: Current puzzle state
        solutions: Multiple valid solutions found
        
    Returns:
        RepairDecision or None if repair not possible
        
    Note: T052 - Stub implementation
    """
    # TODO T052: Implement differing segment analysis
    # For now, return None (no repair)
    return None
