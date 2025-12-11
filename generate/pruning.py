"""Generate module: Solver-Driven Pruning

Interval reduction and frequency-based uniqueness repair for minimal clue counts.
"""
from dataclasses import dataclass, field
from random import random
from typing import Optional, TYPE_CHECKING
from enum import Enum

from core.position import Position
from core.puzzle import Puzzle
from generate.repair import apply_structural_repair

if TYPE_CHECKING:
    from generate.models import GenerationConfig


class PruningStatus(Enum):
    """Pruning outcome classification."""
    SUCCESS = "success"
    SUCCESS_WITH_REPAIRS = "success_with_repairs"
    ABORTED_MAX_REPAIRS = "aborted_max_repairs"
    ABORTED_TIMEOUT = "aborted_timeout"


@dataclass
class IntervalState:
    """Current removable clue range during binary search."""
    low_index: int
    high_index: int
    contraction_reason: Optional[str] = None


@dataclass
class RemovalBatch:
    """Proposed batch of clues to remove."""
    batch_size: int
    candidate_positions: list[Position]
    attempt_index: int


@dataclass
class AmbiguityProfile:
    """Ranking of cells by divergence frequency across alternates."""
    entries: list[dict]  # {position, frequency_score, segment_index}
    computed_from_alternates: int
    
    def top_n(self, n: int) -> list[dict]:
        """Return top N entries by frequency_score."""
        return sorted(self.entries, key=lambda e: e['frequency_score'], reverse=True)[:n]


@dataclass
class RepairCandidate:
    """Selected clue for uniqueness repair."""
    position: Position
    rationale: str
    score: float


@dataclass
class PruningSession:
    """Tracks metrics across pruning iterations."""
    iteration_count: int = 0
    uniqueness_failures: int = 0
    repairs_used: int = 0
    interval_contractions: int = 0
    history: list[IntervalState] = field(default_factory=list)
    timeout_occurred: bool = False
    
    def record_iteration(self):
        """Increment iteration counter."""
        self.iteration_count += 1
    
    def record_uniqueness_failure(self):
        """Increment uniqueness failure counter."""
        self.uniqueness_failures += 1
    
    def record_repair(self):
        """Increment repair counter."""
        self.repairs_used += 1
    
    def record_interval_contraction(self, state: IntervalState):
        """Record interval state and increment contraction counter."""
        self.history.append(state)
        self.interval_contractions += 1
    
    def record_timeout(self):
        """Mark timeout occurrence."""
        self.timeout_occurred = True
    
    def to_metrics(self) -> dict:
        """Export as metrics dict."""
        return {
            "pruning_iterations": self.iteration_count,
            "interval_contractions": self.interval_contractions,
            "uniqueness_failures": self.uniqueness_failures,
            "repairs_used": self.repairs_used,
            "timeout_occurred": self.timeout_occurred,
        }


@dataclass
class PruningResult:
    """Result of solver-driven pruning."""
    puzzle: Puzzle
    status: PruningStatus
    session: PruningSession
    final_clue_count: int
    final_density: float
    time_ms: float
    
    def to_dict(self) -> dict:
        """Export as dict."""
        return {
            "status": self.status.value,
            "final_clue_count": self.final_clue_count,
            "final_density": self.final_density,
            "time_ms": self.time_ms,
            **self.session.to_metrics(),
        }


def order_removable_clues(puzzle: Puzzle, path: list[Position]) -> list[Position]:
    """Order removable clues by structural relevance.
    
    T01: Heuristic uses distance from endpoints + corridor centrality.
    Endpoints always excluded from removal.
    
    Args:
        puzzle: Current puzzle state
        path: Hamiltonian path (ordered positions)
    
    Returns:
        Ordered list of removable clue positions (descending priority for removal)
    """
    if not path or len(path) < 2:
        return []
    
    endpoints = {path[0], path[-1]}
    givens = {cell.pos for cell in puzzle.grid.iter_cells() if cell.given}
    removable = list(givens - endpoints)
    
    if not removable:
        return []
    
    # Build position -> path index map
    path_index = {pos: i for i, pos in enumerate(path)}
    
    # Score each removable clue: distance from endpoints + mid-segment weight
    def score_clue(pos: Position) -> float:
        idx = path_index.get(pos, len(path) // 2)
        dist_from_start = idx
        dist_from_end = len(path) - 1 - idx
        min_dist_endpoint = min(dist_from_start, dist_from_end)
        # Higher score = more central, further from endpoints = remove first
        return min_dist_endpoint
    
    # Sort descending by score (remove central clues first)
    removable.sort(key=score_clue, reverse=True)
    return removable


def _given_values_along_path(puzzle: Puzzle, path: list[Position]) -> list[int]:
    """Return sorted list of values that are currently given along the path.

    Uses path index (1-based) as the value mapping.
    """
    given_vals = []
    for i, pos in enumerate(path, start=1):
        cell = puzzle.grid.get_cell(pos)
        if cell.given:
            given_vals.append(i)
    return sorted(given_vals)


def compute_minimal_spine(
    path: list[Position],
    puzzle: Puzzle,
    max_gap: int = 12,
) -> set[Position]:
    """Compute minimal spine of anchor values to enforce max_gap constraint.
    
    Strategy:
    - Always include endpoints (value 1 and value N)
    - Scan current given values; for each gap > max_gap, inject one anchor near midpoint
    - Returns set of positions to inject (does not modify puzzle)
    
    This replaces quartile injection with a gap-driven approach.
    """
    if not path:
        return set()
    
    N = len(path)
    given_vals = _given_values_along_path(puzzle, path)
    
    # Ensure endpoints are given
    spine_positions = set()
    if 1 not in given_vals:
        spine_positions.add(path[0])
    if N not in given_vals:
        spine_positions.add(path[N - 1])
    
    # Scan gaps
    given_vals_set = set(given_vals)
    for a, b in zip(given_vals, given_vals[1:]):
        gap = b - a
        if gap > max_gap:
            # Inject anchor near midpoint of gap
            mid = (a + b) // 2
            if 1 <= mid <= N and mid not in given_vals_set:
                spine_positions.add(path[mid - 1])
                given_vals_set.add(mid)  # Prevent re-injection
    
    return spine_positions


def ensure_sparse_gap_anchors(
    puzzle: Puzzle,
    path: list[Position],
    gap_threshold: int = 20,
    max_per_gap: int = 2,
) -> set[Position]:
    """Inject a small number of anchors inside large value gaps.

    Strategy:
    - Scan given values along the path; for any gap (b - a) > gap_threshold
      inject up to max_per_gap anchors evenly spaced by value index between a and b.
    - This reduces huge free spans without flooding the grid with clues.

    Returns set of injected positions (to optionally protect during removal).
    
    DEPRECATED: Replaced by compute_minimal_spine for more targeted approach.
    """
    injected_positions: set[Position] = set()
    if not path:
        return injected_positions

    given_vals = _given_values_along_path(puzzle, path)
    if not given_vals:
        return injected_positions

    # Include endpoints if they're givens; ensure we consider all consecutive pairs
    for a, b in zip(given_vals, given_vals[1:]):
        gap = b - a
        if gap <= gap_threshold:
            continue
        # Plan k injections
        k = min(max_per_gap, max(0, gap // (gap_threshold + 1)))
        if k <= 0:
            k = 1  # at least one if gap exceeds threshold
        step = gap // (k + 1)
        for j in range(1, k + 1):
            v = a + j * step
            if 1 <= v <= len(path):
                pos = path[v - 1]
                cell = puzzle.grid.get_cell(pos)
                if not cell.blocked and not cell.given:
                    cell.given = True
                    cell.value = v
                    injected_positions.add(pos)
    return injected_positions


def _find_given_clusters(puzzle: Puzzle, allow_diagonal: bool = True) -> list[list[Position]]:
    """Find clusters of given cells connected by 8- or 4-neighborhood.

    Returns list of clusters, each a list of Positions.
    """
    neighbors8 = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]
    neighbors4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    deltas = neighbors8 if allow_diagonal else neighbors4

    rows, cols = puzzle.grid.rows, puzzle.grid.cols
    visited = set()
    clusters: list[list[Position]] = []

    for cell in puzzle.grid.iter_cells():
        if cell.pos in visited or cell.blocked or not cell.given:
            continue
        # BFS
        from collections import deque
        q = deque([cell.pos])
        visited.add(cell.pos)
        cluster = [cell.pos]
        while q:
            p = q.popleft()
            for dr, dc in deltas:
                nr, nc = p.row + dr, p.col + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    npos = Position(nr, nc)
                    if npos in visited:
                        continue
                    ncell = puzzle.grid.get_cell(npos)
                    if not ncell.blocked and ncell.given:
                        visited.add(npos)
                        q.append(npos)
                        cluster.append(npos)
        clusters.append(cluster)
    return clusters


def _cluster_interior_candidates(puzzle: Puzzle, cluster: list[Position], allow_diagonal: bool = True, reverse=False) -> list[Position]:
    """Return interior given positions within a cluster prioritized for removal.

    Interior heuristic: cells with the most given neighbors first.
    """
    neighbors8 = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]
    neighbors4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    deltas = neighbors8 if allow_diagonal else neighbors4

    def given_neighbor_count(pos: Position) -> int:
        cnt = 0
        for dr, dc in deltas:
            nr, nc = pos.row + dr, pos.col + dc
            if 0 <= nr < puzzle.grid.rows and 0 <= nc < puzzle.grid.cols:
                ncell = puzzle.grid.get_cell(Position(nr, nc))
                if not ncell.blocked and ncell.given:
                    cnt += 1
        return cnt

    # Sort by descending neighbor count (more interior first)
    candidates = sorted(cluster, key=given_neighbor_count, reverse=reverse)
    return candidates


def score_removal_candidate(
    pos: Position,
    puzzle: Puzzle,
    path: list[Position],
    max_gap: int = 12,
) -> tuple[float, bool]:
    """Score a candidate for removal based on cluster interiorness and gap impact.
    
    Returns:
        (score, is_safe): score is higher for better removal candidates
                          is_safe is True if removal won't violate max_gap
    
    Score components:
    - cluster_interiorness: cells with more given neighbors score higher
    - endpoint_distance: cells further from path endpoints score higher
    - gap_impact_penalty: if removing creates gap > max_gap, heavily penalize
    """
    # Build path index
    path_index = {p: i for i, p in enumerate(path)}
    idx = path_index.get(pos, len(path) // 2)
    value = idx + 1  # 1-indexed
    
    # Endpoint distance component
    dist_start = idx
    dist_end = len(path) - 1 - idx
    min_dist_endpoint = min(dist_start, dist_end)
    endpoint_score = min_dist_endpoint / len(path)  # Normalized [0, 1]
    
    # Cluster interiorness
    neighbors8 = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]
    deltas = neighbors8 if puzzle.constraints.allow_diagonal else [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    given_neighbors = 0
    for dr, dc in deltas:
        nr, nc = pos.row + dr, pos.col + dc
        if 0 <= nr < puzzle.grid.rows and 0 <= nc < puzzle.grid.cols:
            ncell = puzzle.grid.get_cell(Position(nr, nc))
            if not ncell.blocked and ncell.given:
                given_neighbors += 1
    
    max_neighbors = len(deltas)
    interiorness_score = given_neighbors / max_neighbors  # Normalized [0, 1]
    
    # Gap impact simulation
    # Temporarily remove and compute max_gap
    cell = puzzle.grid.get_cell(pos)
    was_given = cell.given
    cell.given = False
    
    given_vals = _given_values_along_path(puzzle, path)
    new_max_gap = 0
    if len(given_vals) >= 2:
        for a, b in zip(given_vals, given_vals[1:]):
            new_max_gap = max(new_max_gap, b - a)
    
    cell.given = was_given  # Restore
    
    is_safe = (new_max_gap <= max_gap)
    gap_penalty = 0.0 if is_safe else 10.0  # Heavy penalty for unsafe removal
    
    # Combined score: higher is better for removal
    # Weights: interiorness (0.6) + endpoint_distance (0.4) - gap_penalty
    score = 0.6 * interiorness_score + 0.4 * endpoint_score - gap_penalty
    
    return (score, is_safe)


def dechunk_given_clusters(
    puzzle: Puzzle,
    path: list[Position],
    solver_mode: str,
    max_cluster_size: int = 8,
    removal_budget: int = 10,
    reverse: bool = False,
) -> int:
    """Reduce overly large contiguous clusters of givens while preserving uniqueness.

    Attempts to remove interior givens from clusters whose size exceeds max_cluster_size.
    Stops when budget is exhausted or no further safe removals found.

    Returns the number of clues removed.
    """
    removed = 0
  
    # Exclude endpoints
    endpoints = [path[0], path[-1]]

    clusters = _find_given_clusters(puzzle, allow_diagonal=puzzle.constraints.allow_diagonal)
    # Process largest clusters first
    clusters.sort(key=len, reverse=True)
    for cluster in clusters:
        if removed >= removal_budget:
            break
        if len(cluster) <= max_cluster_size:
            continue
        candidates = _cluster_interior_candidates(puzzle, cluster, allow_diagonal=puzzle.constraints.allow_diagonal,reverse=reverse)
        for pos in candidates:
            if removed >= removal_budget:
                break
            cell = puzzle.grid.get_cell(pos)
            if not cell.given or cell.blocked or pos in endpoints:
                continue
            # Tentatively remove and test
            cell.given = False
            if check_puzzle_uniqueness(puzzle, solver_mode):
                removed += 1
            else:
                # revert
                cell.given = True
        # Continue to next cluster
    return removed


def iterative_gap_safe_thinning(
    puzzle: Puzzle,
    path: list[Position],
    solver_mode: str,
    target_min_density: float,
    target_max_density: float,
    max_gap: int = 12,
    max_iterations: int = 20,
    batch_size_init: int = 5,
) -> int:
    """Iteratively remove clues while maintaining max_gap and uniqueness constraints.
    
    Strategy:
    - While density > target_max:
      - Score all safe-to-remove candidates (gap impact check)
      - Select top K by score
      - Attempt batch removal, verify uniqueness
      - On failure: revert, shrink batch size, retry with next-best candidates
      - On success: update state, continue
    - Stop when density <= target_max or no safe candidates remain
    
    Returns number of clues removed.
    """
    removed_total = 0
    batch_size = batch_size_init
    
    for iteration in range(max_iterations):
        current_clue_count = sum(
            1 for row in puzzle.grid.cells for cell in row
            if not cell.blocked and cell.given
        )
        current_density = current_clue_count / len(path)
        
        # Stop if within target or below minimum
        if current_density <= target_max_density:
            break
        if current_density < target_min_density:
            break
        
        # Find all given positions
        given_positions = [
            cell.pos for row in puzzle.grid.cells for cell in row
            if not cell.blocked and cell.given
        ]
        
        # Exclude endpoints
        endpoints = {path[0], path[-1]}
        candidates = [pos for pos in given_positions if pos not in endpoints]
        
        if not candidates:
            break
        
        # Score candidates
        scored = []
        for pos in candidates:
            score, is_safe = score_removal_candidate(pos, puzzle, path, max_gap)
            if is_safe:  # Only consider safe candidates
                scored.append((score, pos))
        
        if not scored:
            # No safe candidates left
            break
        
        # Sort descending by score
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # Select top batch_size candidates
        batch_candidates = [pos for _, pos in scored[:batch_size]]
        
        # Snapshot before removal
        snapshot = snapshot_puzzle_state(puzzle)
        
        # Remove batch
        for pos in batch_candidates:
            puzzle.grid.get_cell(pos).given = False
        
        # Verify uniqueness
        if check_puzzle_uniqueness(puzzle, solver_mode):
            # Success
            removed_total += len(batch_candidates)
            # Reset batch size for next iteration
            batch_size = batch_size_init
        else:
            # Failure: revert
            restore_puzzle_state(puzzle, snapshot)
            # Shrink batch size
            batch_size = max(1, batch_size // 2)
            # If batch size is 1 and still failing, no progress possible
            if batch_size == 1 and len(batch_candidates) == 1:
                break
    
    return removed_total


def contract_interval(low: int, high: int, reason: str) -> IntervalState:
    """Contract interval after failure or success.
    
    Args:
        low: Current low index
        high: Current high index
        reason: Why contracting (e.g., "uniqueness_fail", "density_met")
    
    Returns:
        New IntervalState with contracted range
    """
    mid = (low + high) // 2
    if reason == "uniqueness_fail":
        # Failed at mid; shrink upper bound
        return IntervalState(low, mid - 1, reason)
    else:
        # Success at mid; try more aggressive removal
        return IntervalState(mid + 1, high, reason)


def should_fallback_to_linear(removable_count: int, fallback_k: int) -> bool:
    """Check if interval reduction should switch to linear probing.
    
    T04: Fallback when remaining removable clues <= K.
    
    Args:
        removable_count: Number of removable clues left
        fallback_k: Threshold for fallback
    
    Returns:
        True if should switch to linear removal
    """
    return removable_count <= fallback_k


def snapshot_puzzle_state(puzzle: Puzzle) -> dict:
    """Create snapshot of current puzzle state for revert.
    
    T03: Snapshot given flags before batch removal.
    
    Args:
        puzzle: Puzzle to snapshot
    
    Returns:
        Dict with given_positions set and blocked_positions set
    """
    given_positions = set()
    blocked_positions = set()
    for row in puzzle.grid.cells:
        for cell in row:
            if cell.blocked:
                blocked_positions.add(cell.pos)
            if not cell.blocked and cell.given:
                given_positions.add(cell.pos)
    return {"given_positions": given_positions, "blocked_positions": blocked_positions}


def restore_puzzle_state(puzzle: Puzzle, snapshot: dict) -> None:
    """Restore puzzle to prior state from snapshot.
    
    T03: Revert given flags after uniqueness failure.
    
    Args:
        puzzle: Puzzle to restore
        snapshot: State dict from snapshot_puzzle_state()
    """
    given_positions = snapshot["given_positions"]
    blocked_positions = snapshot.get("blocked_positions")

    # Restore blocked flags first (important if structural repairs added blocks)
    if blocked_positions is not None:
        for row in puzzle.grid.cells:
            for cell in row:
                cell.blocked = cell.pos in blocked_positions
                # Optional safety: clear given on blocked cells
                if cell.blocked:
                    cell.given = False
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked:
                cell.given = cell.pos in given_positions


def _compute_clue_density(puzzle: Puzzle) -> float:
    """Compute ratio of given cells over non-blocked cells."""
    total = 0
    givens = 0
    for row in puzzle.grid.cells:
        for cell in row:
            if cell.blocked:
                continue
            total += 1
            if cell.given:
                givens += 1
    return (givens / total) if total > 0 else 1.0


def _estimate_ambiguity_score(puzzle: Puzzle) -> int:
    """Estimate ambiguity via count of flexible v→v+1 links.

    Heuristic: for each placed value v whose successor v+1 isn't placed yet,
    count how many empty neighbors v has. Each case with >=2 choices is one
    ambiguous link. Sum across all v. Higher score suggests likely non-uniqueness
    in sparse, diagonal-adjacency puzzles.
    """
    # Build map of placed values to positions and set of placed values
    placed = {}
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.value is not None:
                placed[cell.value] = cell.pos

    min_v = puzzle.constraints.min_value
    max_v = puzzle.constraints.max_value

    ambiguous_links = 0
    for v, pos in placed.items():
        if v < min_v or v >= max_v:
            continue
        succ = v + 1
        # Skip if successor is already placed
        if succ in placed:
            continue
        # Count empty neighbors around v
        empty_neighbors = 0
        for npos in puzzle.grid.neighbors_of(pos):
            ncell = puzzle.grid.get_cell(npos)
            if not ncell.blocked and ncell.value is None:
                empty_neighbors += 1
        if empty_neighbors >= 2:
            ambiguous_links += 1
    return ambiguous_links


def _detect_high_value_tail(puzzle: Puzzle) -> tuple[int, int]:
    """Detect length of consecutive given tail ending near max value.

    Returns (tail_len, tail_start_value). Tail is counted over given cells only,
    descending from max_value while each value is present as a given.
    """
    given_values = set()
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given and cell.value is not None:
                given_values.add(cell.value)

    min_v = puzzle.constraints.min_value
    max_v = puzzle.constraints.max_value

    v = max_v
    tail_len = 0
    while v >= min_v and v in given_values:
        tail_len += 1
        v -= 1
    tail_start_value = v + 1 if tail_len > 0 else max_v
    return tail_len, tail_start_value


# Heuristic thresholds for sparse 9x9+ diagonal boards
TAIL_REJECT_LEN = 7          # Reject if tail of consecutive givens at max end >= 7
AMBIGUITY_STRICT_THRESHOLD = 2  # If ambiguous links >= 2, run stricter verification
SPARSE_DENSITY_THRESHOLD = 0.30  # Consider sparse if clue density below this
MAX_VALUE_GAP = 12          # Reject if largest gap between consecutive given values exceeds this


def _detect_low_value_head(puzzle: Puzzle) -> tuple[int, int]:
    """Detect length of consecutive given head starting from min value.

    Returns (head_len, head_end_value). Head is counted over given cells only,
    ascending from min_value while each value is present as a given.
    """
    given_values = set()
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given and cell.value is not None:
                given_values.add(cell.value)

    min_v = puzzle.constraints.min_value
    max_v = puzzle.constraints.max_value

    v = min_v
    head_len = 0
    while v <= max_v and v in given_values:
        head_len += 1
        v += 1
    head_end_value = v - 1 if head_len > 0 else min_v
    return head_len, head_end_value


def _compute_anchor_dispersion(puzzle: Puzzle) -> int:
    """Compute largest gap between consecutive given values (A: Dispersion metric).
    
    Returns the maximum span of consecutive missing values between any two adjacent givens.
    Large gaps indicate poor anchor distribution and high ambiguity risk.
    """
    given_values = []
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given and cell.value is not None:
                given_values.append(cell.value)
    
    if len(given_values) < 2:
        return 0
    
    given_values.sort()
    max_gap = 0
    for i in range(len(given_values) - 1):
        gap = given_values[i + 1] - given_values[i] - 1
        max_gap = max(max_gap, gap)
    
    return max_gap



def check_puzzle_uniqueness(puzzle: Puzzle, solver_mode: str) -> bool:
    """Check if puzzle has exactly one solution.
    
    Args:
        puzzle: Puzzle to check
        solver_mode: Solver mode string (unused, kept for signature compatibility)
    
    Returns:
        True if puzzle has unique solution (exactly 1 solution, not just solvable)
        
    Notes:
        Uses staged uniqueness validation with bounded search and time budgets.
        Falls back to old method if staged checker returns inconclusive.
    """
    # Option 1: Use staged uniqueness checker (ENABLED)
    from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision
    
    # Determine adjacency (4 or 8)
    adjacency = 8 if puzzle.constraints.allow_diagonal else 4
    
    request = create_request(
        puzzle=puzzle,
        size=puzzle.grid.rows,  # Use actual grid size
        adjacency=adjacency,
        difficulty='hard',  # Conservative budget (500ms)
        enable_early_exit=True,
        enable_probes=True,  # Disable probes for now (placeholder logic)
        enable_sat=False,
    )
    # Override the small-board 100ms cap
    request.total_budget_ms = 2000   # try 1500–2000ms
    request.stage_budget_split = {'early_exit': 0.5, 'probes': 0.5, 'sat': 0.0} # even split
    request.strategy_flags['probes'] = True  # Enable probes explicitly
    result = check_uniqueness(request)
    #print(result)
    # Honor tri-state decision per FR-008
    if result.decision == UniquenessDecision.UNIQUE:
        # Extra guardrail for sparse 8-neighbor puzzles (high ambiguity risk)
        density = _compute_clue_density(puzzle)
        
        # A: Check anchor dispersion ALWAYS for 8-neighbor puzzles (critical structural check)
        if puzzle.constraints.allow_diagonal and puzzle.grid.rows >= 9:
            max_gap = _compute_anchor_dispersion(puzzle)
            if max_gap > MAX_VALUE_GAP:
                return False
        
        if (puzzle.constraints.allow_diagonal
                and puzzle.grid.rows >= 9
                and density < SPARSE_DENSITY_THRESHOLD):
            
            # D: For large gaps, use bi-directional search to detect alternates
            if max_gap > 15:
                path_count = _bidirectional_path_search(puzzle, max_gap, time_cap_ms=2000)
                if path_count >= 2:
                    return False  # Found multiple distinct paths
            
            # C: Check region span fit - reject if large capacity mismatch
            region_mismatch = _compute_region_span_fit(puzzle)
            if region_mismatch > 20:  # Threshold for 9x9 boards
                return False
            
            # E: Check flex zone size - reject if too many unconstrained cells
            # (This is expensive, only run if other checks passed but still sparse)
            if density < 0.28:
                flex_zone_size = _compute_flex_zone_size(puzzle)
                if flex_zone_size > 30:  # Large unconstrained area
                    return False
            
            tail_len, tail_start = _detect_high_value_tail(puzzle)
            head_len, head_end = _detect_low_value_head(puzzle)
            # New stricter policy: any tail >= threshold triggers rejection to drive anchor retention
            if tail_len >= TAIL_REJECT_LEN or head_len >= TAIL_REJECT_LEN:
                return False
            ambiguity = _estimate_ambiguity_score(puzzle)
            if ambiguity >= AMBIGUITY_STRICT_THRESHOLD:
                from generate.uniqueness import count_solutions
                strict = count_solutions(
                    puzzle, cap=2, node_cap=25000, timeout_ms=12000
                )
                return strict.is_unique
        return True
    elif result.decision == UniquenessDecision.NON_UNIQUE:
        return False
    else:  # INCONCLUSIVE
        # Fallback to old method for inconclusive cases
        from generate.uniqueness import count_solutions
        density = _compute_clue_density(puzzle)
        node_cap = 40000
        timeout_ms = 100000
        # Increase budgets for sparse diagonal puzzles
        if puzzle.constraints.allow_diagonal and density < SPARSE_DENSITY_THRESHOLD:
            node_cap = 300000
            timeout_ms = 200000
        fallback_result = count_solutions(puzzle, cap=2, node_cap=node_cap, timeout_ms=timeout_ms)
        print(f'density:{density}, fallback_result:{fallback_result}')
        if not fallback_result.is_unique and fallback_result.solutions_found >= 2:
            return False
        
        # A: Check anchor dispersion ALWAYS for 8-neighbor puzzles (even if not sparse)
        if (fallback_result.is_unique
                and puzzle.constraints.allow_diagonal
                and puzzle.grid.rows >= 9):
            max_gap = _compute_anchor_dispersion(puzzle)
            if max_gap > MAX_VALUE_GAP:
                return False
        
        # Apply same tail guardrail even if staged checker was inconclusive
        if (fallback_result.is_unique
                and puzzle.constraints.allow_diagonal
                and puzzle.grid.rows >= 9
                and density < SPARSE_DENSITY_THRESHOLD):
            # C: Check region span fit in fallback too
            region_mismatch = _compute_region_span_fit(puzzle)
            if region_mismatch > 20:
                return False
            
            tail_len, _ = _detect_high_value_tail(puzzle)
            head_len, _ = _detect_low_value_head(puzzle)
            if tail_len >= TAIL_REJECT_LEN or head_len >= TAIL_REJECT_LEN:
                return False
        # As a last resort, attempt alternate sampling to expose ambiguity
        alternates = sample_alternate_solutions(
            puzzle, path=[], solver_mode=solver_mode, alternates_count=3, time_cap_ms=3000
        )
        if len(alternates) >= 2:
            # If we found two distinct completions, it's not unique
            # Compare first two alternates on any differing cell
            a0 = alternates[0]
            for a in alternates[1:]:
                if any((pos in a0 and pos in a and a0[pos] != a[pos]) for pos in a0.keys() & a.keys()):
                    return False
        return fallback_result.is_unique



def sample_alternate_solutions(
    puzzle: Puzzle,
    path: list[Position],
    solver_mode: str,
    alternates_count: int,
    time_cap_ms: float = 5000
) -> list[dict]:
    """Sample alternate solutions by varying solver behavior.
    
    T05: Generate 3-5 alternate solutions with time cap.
    Uses different search orderings to find diverse solutions.
    
    Args:
        puzzle: Non-unique puzzle to solve
        path: Original solution path positions
        solver_mode: Solver mode string
        alternates_count: Number of alternates to sample
        time_cap_ms: Total time budget for all alternates
    
    Returns:
        List of alternate solution dicts with position->value mappings
    """
    import time
    from solve.solver import Solver
    
    alternates = []
    start_time = time.time()
    
    # Try different solver orderings/tie-breaks to get diversity
    orderings = ["row_col", "col_row", "value_asc", "value_desc", "random"]
    
    for i in range(alternates_count):
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms >= time_cap_ms:
            break
        
        # Use different ordering for each alternate
        ordering = orderings[i % len(orderings)]
        
        # Solve with specific ordering
        result = Solver.solve(
            puzzle, 
            mode=solver_mode,
            ordering=ordering,
            max_time_ms=int((time_cap_ms - elapsed_ms) / (alternates_count - i))
        )
        
        if result.solved:
            # Extract solution as position->value dict
            solution = {}
            for row in result.solved_puzzle.grid.cells:
                for cell in row:
                    if not cell.blocked and cell.value is not None:
                        solution[cell.pos] = cell.value
            alternates.append(solution)
    
    return alternates


def build_ambiguity_profile(
    alternates: list[dict],
    path: list[Position],
    givens: set[Position]
) -> AmbiguityProfile:
    """Build ambiguity profile from alternate solutions.
    
    T06: Compute divergence frequencies for repair candidate selection.
    
    Args:
        alternates: List of alternate solution dicts (pos->value)
        path: Original solution path
        givens: Current given positions (to exclude from profile)
    
    Returns:
        AmbiguityProfile with frequency-scored entries
    """
    from collections import Counter
    
    if not alternates:
        return AmbiguityProfile([], len(alternates))
    
    # Count value divergences at each position
    divergence_counts = Counter()
    
    for pos in path:
        if pos in givens:
            continue  # Skip givens
        
        # Check if values differ across alternates
        values = set()
        for alt in alternates:
            if pos in alt:
                values.add(alt[pos])
        
        # If multiple values exist, this position has ambiguity
        if len(values) > 1:
            divergence_counts[pos] = len(values)
    
    # Convert to profile entries with scores
    entries = []
    for pos, frequency in divergence_counts.items():
        # Score = frequency (simple version; can add corridor weighting later)
        score = float(frequency)
        entries.append({
            "position": pos,
            "frequency": frequency,
            "score": score
        })
    
    # Sort by score descending
    entries.sort(key=lambda e: e["score"], reverse=True)
    
    return AmbiguityProfile(entries, len(alternates))


def select_repair_candidates(
    profile: AmbiguityProfile,
    path: list[Position],
    top_n: int
) -> list[RepairCandidate]:
    """Select top-N repair candidates from ambiguity profile.
    
    T07: Choose repair clues from mid-segment high-frequency positions.
    
    Args:
        profile: Ambiguity profile with scored entries
        path: Solution path for position indexing
        top_n: Number of candidates to return
    
    Returns:
        List of RepairCandidate objects with position and rationale
    """
    candidates = []
    
    # Filter to mid-segment positions (exclude first/last 10% of path)
    path_len = len(path)
    mid_start = int(path_len * 0.1)
    mid_end = int(path_len * 0.9)
    mid_positions = set(path[mid_start:mid_end])
    
    for entry in profile.entries:
        pos = entry["position"]
        
        # Only consider mid-segment positions
        if pos not in mid_positions:
            continue
        
        frequency = entry["frequency"]
        score = entry["score"]
        
        candidates.append(RepairCandidate(
            position=pos,
            rationale=f"ambiguity_freq_{frequency}",
            score=score
        ))
        
        if len(candidates) >= top_n:
            break
    
    return candidates


def apply_repair_clue(puzzle: Puzzle, candidate: RepairCandidate) -> None:
    """Apply a repair clue by marking position as given.
    
    Args:
        puzzle: Puzzle to repair
        candidate: Repair candidate with position
    """
    cell = puzzle.grid.get_cell(candidate.position)
    cell.given = True


def ensure_quartile_anchors(puzzle: Puzzle, path: list[Position]) -> tuple[int, set[Position]]:
    """B: Ensure at least one anchor per quartile of value range.
    
    Injects mid-range anchors if any quartile is missing givens. This improves
    uniqueness by preventing large unanchored spans.
    
    Args:
        puzzle: Puzzle to check/modify
        path: Hamiltonian path (ordered positions)
        
    Returns:
        Tuple of (number of anchors injected, set of injected positions to protect)
    """
    min_v = puzzle.constraints.min_value
    max_v = puzzle.constraints.max_value
    span = max_v - min_v + 1
    
    # Define quartile ranges
    q1_end = min_v + span // 4
    q2_end = min_v + span // 2
    q3_end = min_v + 3 * span // 4
    
    quartiles = [
        (min_v, q1_end, "Q1"),
        (q1_end + 1, q2_end, "Q2"),
        (q2_end + 1, q3_end, "Q3"),
        (q3_end + 1, max_v, "Q4"),
    ]
    
    # Collect given values
    given_values = set()
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given and cell.value is not None:
                given_values.add(cell.value)
    
    injected = 0
    protected_positions = set()
    
    for q_start, q_end, q_name in quartiles:
        # Check if this quartile has at least one given
        has_anchor = any(q_start <= v <= q_end for v in given_values)
        if not has_anchor:
            # Pick mid-value of this quartile
            target_value = (q_start + q_end) // 2
            # Find cell at path position (value-1) and mark as given
            if 1 <= target_value <= len(path):
                pos = path[target_value - 1]  # path is 0-indexed, values are 1-indexed
                cell = puzzle.grid.get_cell(pos)
                if not cell.blocked and not cell.given:
                    cell.given = True
                    cell.value = target_value
                    injected += 1
                    protected_positions.add(pos)  # Mark for protection
    
    return injected, protected_positions


def _flood_fill_region(puzzle: Puzzle, start_pos: Position, visited: set) -> set:
    """C: Flood-fill to find connected empty region starting from a position.
    
    Args:
        puzzle: Puzzle to analyze
        start_pos: Starting position for flood fill
        visited: Global visited set (modified in-place)
        
    Returns:
        Set of positions in this connected region
    """
    from collections import deque
    
    region = set()
    queue = deque([start_pos])
    region.add(start_pos)
    visited.add(start_pos)
    
    while queue:
        pos = queue.popleft()
        for neighbor_pos in puzzle.grid.neighbors_of(pos):
            if neighbor_pos in visited:
                continue
            neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
            if neighbor_cell.blocked:
                continue
            # Include cells that are empty or non-given (solution value but not anchor)
            if neighbor_cell.value is None or not neighbor_cell.given:
                visited.add(neighbor_pos)
                region.add(neighbor_pos)
                queue.append(neighbor_pos)
    
    return region


def _compute_region_span_fit(puzzle: Puzzle) -> int:
    """C: Compute maximum region span mismatch (capacity vs needed values).
    
    Analyzes empty regions and checks if the span of values that must pass through
    each region exceeds its capacity (or vice versa), indicating ambiguity risk.
    
    Returns:
        Maximum span mismatch across all regions (0 if all fit well)
    """
    # Find all empty regions via flood fill
    visited = set()
    regions = []
    
    for row in puzzle.grid.cells:
        for cell in row:
            if cell.blocked:
                continue
            if cell.pos in visited:
                continue
            # Start flood fill from empty or non-given cells
            if cell.value is None or not cell.given:
                region = _flood_fill_region(puzzle, cell.pos, visited)
                if len(region) > 1:  # Only care about multi-cell regions
                    regions.append(region)
    
    # For each region, compute span of values that must occupy it
    max_mismatch = 0
    for region in regions:
        # Find boundary given values (neighbors of region cells)
        boundary_values = set()
        for pos in region:
            for neighbor_pos in puzzle.grid.neighbors_of(pos):
                neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
                if not neighbor_cell.blocked and neighbor_cell.given and neighbor_cell.value is not None:
                    boundary_values.add(neighbor_cell.value)
        
        if len(boundary_values) < 2:
            continue  # Can't determine span without boundaries
        
        # Span of values that must pass through this region
        min_boundary = min(boundary_values)
        max_boundary = max(boundary_values)
        needed_span = max_boundary - min_boundary - 1  # Excluding boundaries
        
        # Region capacity
        region_capacity = len(region)
        
        # Mismatch: if capacity >> needed, there's routing freedom (ambiguity)
        # Slack factor: allow 1.5x capacity for reasonable routing
        if region_capacity > needed_span * 1.5 and needed_span > 5:
            mismatch = region_capacity - needed_span
            max_mismatch = max(max_mismatch, mismatch)
    
    return max_mismatch


def _bidirectional_path_search(puzzle: Puzzle, max_gap: int, time_cap_ms: int = 3000) -> int:
    """D: Bi-directional path search to detect multiple solutions for large gaps.
    
    When a large value gap exists (e.g., givens 1-15 and 66-81, gap ≈50), attempts
    to construct two distinct paths from low cluster to high cluster. If successful,
    confirms non-uniqueness without exhaustive search.
    
    Args:
        puzzle: Puzzle to analyze
        max_gap: Size of largest gap between consecutive givens
        time_cap_ms: Time budget in milliseconds
        
    Returns:
        Number of distinct bridge paths found (0, 1, or 2+)
    """
    import time
    from collections import deque
    
    if max_gap < 8:
        return 1  # Small gap, assume unique (not worth expensive search)
    
    start_time = time.time()
    
    # Find gap boundaries: lowest high anchor and highest low anchor
    given_values = []
    value_to_pos = {}
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given and cell.value is not None:
                given_values.append(cell.value)
                value_to_pos[cell.value] = cell.pos
    
    if len(given_values) < 2:
        return 1
    
    given_values.sort()
    
    # Find largest gap
    largest_gap_start = None
    largest_gap_end = None
    largest_gap_size = 0
    
    for i in range(len(given_values) - 1):
        gap_size = given_values[i + 1] - given_values[i] - 1
        if gap_size > largest_gap_size:
            largest_gap_size = gap_size
            largest_gap_start = given_values[i]
            largest_gap_end = given_values[i + 1]
    
    if largest_gap_size < 8:
        return 1
    
    # Bi-directional BFS to find two distinct paths through the gap
    # Path 1: Greedy forward from start
    # Path 2: Greedy backward from end (then reverse)
    
    def build_greedy_forward_path(start_val, end_val, start_pos):
        """Build path from start_val toward end_val using greedy adjacency."""
        path = [start_pos]
        current_val = start_val
        current_pos = start_pos
        
        for next_val in range(start_val + 1, end_val):
            if (time.time() - start_time) * 1000 > time_cap_ms:
                return None
            
            # Find an empty neighbor
            neighbors = puzzle.grid.neighbors_of(current_pos)
            candidates = []
            for npos in neighbors:
                ncell = puzzle.grid.get_cell(npos)
                if ncell.blocked or (ncell.given and ncell.value != next_val):
                    continue
                if npos not in path:  # Avoid cycles
                    candidates.append(npos)
            
            if not candidates:
                return None  # Dead end
            
            # Greedy: pick neighbor closest to end (Manhattan distance heuristic)
            end_pos = value_to_pos.get(end_val)
            if end_pos:
                candidates.sort(key=lambda p: abs(p.row - end_pos.row) + abs(p.col - end_pos.col))
            
            current_pos = candidates[0]
            path.append(current_pos)
            current_val = next_val
        
        return path
    
    def build_greedy_backward_path(start_val, end_val, end_pos):
        """Build path from end_val backward toward start_val."""
        path = [end_pos]
        current_val = end_val
        current_pos = end_pos
        
        for prev_val in range(end_val - 1, start_val, -1):
            if (time.time() - start_time) * 1000 > time_cap_ms:
                return None
            
            neighbors = puzzle.grid.neighbors_of(current_pos)
            candidates = []
            for npos in neighbors:
                ncell = puzzle.grid.get_cell(npos)
                if ncell.blocked or (ncell.given and ncell.value != prev_val):
                    continue
                if npos not in path:
                    candidates.append(npos)
            
            if not candidates:
                return None
            
            # Greedy: pick neighbor closest to start
            start_pos = value_to_pos.get(start_val)
            if start_pos:
                candidates.sort(key=lambda p: abs(p.row - start_pos.row) + abs(p.col - start_pos.col))
            
            current_pos = candidates[0]
            path.append(current_pos)
            current_val = prev_val
        
        return list(reversed(path))
    
    # Try both directions
    start_pos = value_to_pos.get(largest_gap_start)
    end_pos = value_to_pos.get(largest_gap_end)
    
    if not start_pos or not end_pos:
        return 1
    
    path1 = build_greedy_forward_path(largest_gap_start, largest_gap_end, start_pos)
    path2 = build_greedy_backward_path(largest_gap_start, largest_gap_end, end_pos)
    
    # Check if both paths succeeded and differ
    if path1 is None or path2 is None:
        return 1  # Couldn't build alternate, assume unique
    
    # Compare paths
    if len(path1) != len(path2):
        return 2  # Different lengths → non-unique
    
    for i in range(len(path1)):
        if path1[i] != path2[i]:
            return 2  # Paths diverge → non-unique
    
    return 1  # Paths identical


def _compute_flex_zone_size(puzzle: Puzzle) -> int:
    """E: Compute size of flex zone (cells removable without affecting constraints).
    
    A flex zone is a set of empty cells that, if removed (blocked), wouldn't
    change the ambiguous link count or immediate constraint structure. Large
    flex zones indicate routing freedom and ambiguity risk.
    
    Returns:
        Number of cells in the largest flex zone
    """
    # Baseline ambiguity score
    baseline_ambiguity = _estimate_ambiguity_score(puzzle)
    
    flex_cells = []
    
    # Test each non-given cell
    for row in puzzle.grid.cells:
        for cell in row:
            if cell.blocked or cell.given:
                continue
            
            # Temporarily mark as blocked
            original_blocked = cell.blocked
            cell.blocked = True
            
            # Re-compute ambiguity
            new_ambiguity = _estimate_ambiguity_score(puzzle)
            
            # Restore
            cell.blocked = original_blocked
            
            # If ambiguity unchanged, this cell is in the flex zone
            if new_ambiguity == baseline_ambiguity:
                flex_cells.append(cell.pos)
    
    return len(flex_cells)


def apply_structural_repair_stub(puzzle: Puzzle, config: 'GenerationConfig') -> bool:
    """Attempt structural repair via ambiguity-aware blocking (T013 stub).
    
    This is a placeholder for US2 implementation. When enabled, it will:
    - Detect ambiguity regions from multiple solutions
    - Score candidate block positions
    - Insert structural block if connectivity preserved
    - Return True if uniqueness restored
    
    Args:
        puzzle: Puzzle with ambiguity
        config: Configuration with structural_repair_enabled flag
        
    Returns:
        True if structural repair succeeded, False otherwise
    """
    # T013: Stub returns False (no repair yet)
    # US2 implementation will add actual logic here
    return False


def remove_clue_batch(puzzle: Puzzle, positions: list[Position]) -> None:
    """Remove given flags from specified positions.
    
    Args:
        puzzle: Puzzle to modify
        positions: Positions to mark as non-given
    """
    for pos in positions:
        puzzle.grid.get_cell(pos).given = False


def prune_puzzle(
    puzzle: Puzzle,
    path: list[Position],
    config: 'GenerationConfig',
    solver_mode: str = "logic_v2",
    timeout_ms: float = None,
    difficulty: str = None
) -> PruningResult:
    """Solver-driven clue pruning with interval reduction.
    
    T02: Main pruning loop with binary search and uniqueness checks.
    T03: Snapshot/revert on uniqueness failure.
    T04: Fallback to linear when count <= K.
    T15: Timeout handling with aborted_timeout status.
    
    Args:
        puzzle: Puzzle with full path as givens
        path: Hamiltonian path positions
        config: Generation configuration
        solver_mode: Solver mode for uniqueness checks
        timeout_ms: Optional timeout override (uses config.timeout_ms if None)
        difficulty: Target difficulty (uses config.difficulty if None)
    
    Returns:
        PruningResult with final puzzle state and metrics
    """
    import time
    start_time = time.time()
    timeout_limit_ms = timeout_ms if timeout_ms is not None else config.timeout_ms
    target_difficulty = difficulty if difficulty is not None else config.difficulty
    
    session = PruningSession()
    
    # Pre-pruning anchoring: enforce a small maximum value gap along the path
    # This is computed purely from path indices so it still triggers even when all cells start as givens.
    protected_positions = set()
    max_gap = 6  # aim to keep value anchors every <=10 steps on the path
    if path:
        spine_indices = list(range(0, len(path), max_gap))
        if spine_indices[-1] != len(path) - 1:
            spine_indices.append(len(path) - 1)
        for idx in spine_indices:
            pos = path[idx]
            cell = puzzle.grid.get_cell(pos)
            if not cell.blocked and not cell.given:
                cell.given = True
                cell.value = idx + 1
            protected_positions.add(pos)
            session.record_repair()
    
    removable = order_removable_clues(puzzle, path)
    
    # Remove protected positions from removable list
    if protected_positions:
        removable = [pos for pos in removable if pos not in protected_positions]
    
    # Shuffle removal order to explore different clue configurations
    import random
    random.shuffle(removable)
    
    if not removable:
        clue_count = sum(
            1 for row in puzzle.grid.cells for cell in row 
            if not cell.blocked and cell.given
        )
        return PruningResult(
            puzzle=puzzle,
            status=PruningStatus.SUCCESS,
            session=session,
            final_clue_count=clue_count,
            final_density=clue_count / len(path),
            time_ms=(time.time() - start_time) * 1000
        )
    
    # Interval reduction phase
    low_index, high_index = 0, len(removable) - 1
    last_unique_snapshot = snapshot_puzzle_state(puzzle)
    
    while low_index <= high_index:
        # T15: Check timeout
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms >= timeout_limit_ms:
            session.timeout_occurred = True
            restore_puzzle_state(puzzle, last_unique_snapshot)
            break
        
        session.record_iteration()
        
        # Check if we've reached target density (stop if in range)
        current_clue_count = sum(
            1 for row in puzzle.grid.cells for cell in row 
            if not cell.blocked and cell.given
        )
        current_density = current_clue_count / len(path)
        
        # Get target density range for current difficulty
        min_density, max_density = 0.0, 1.0
        if target_difficulty == "easy":
            min_density = config.pruning_target_density_easy_min
            max_density = config.pruning_target_density_easy_max
        elif target_difficulty == "medium":
            min_density = config.pruning_target_density_medium_min
            max_density = config.pruning_target_density_medium_max
        elif target_difficulty in "hard":
            min_density = config.pruning_target_density_hard_min
            max_density = config.pruning_target_density_hard_max
        elif target_difficulty in "extreme":
            min_density = config.pruning_target_density_extreme_min
            max_density = config.pruning_target_density_extreme_max

        # Dynamic guardrail: for sparse 9x9+ diagonal puzzles with long head/tail,
        # enforce a higher minimum density to reduce ambiguity bands.
        if (target_difficulty in ["hard", "extreme"]
                and puzzle.constraints.allow_diagonal
                and puzzle.grid.rows >= 9):
            t_len, _ = _detect_high_value_tail(puzzle)
            h_len, _ = _detect_low_value_head(puzzle)
            if t_len >= TAIL_REJECT_LEN or h_len >= TAIL_REJECT_LEN:
                min_density = max(min_density, 0.34)
                max_density = max(max_density, 0.40)
        
        # Check if we're below minimum - stop to avoid going too low
        if current_density < min_density:
            # Already below minimum, stop pruning
            break
        
        # For non-easy modes, also stop if we're in the target range
        # For easy mode, continue removing as long as we're above minimum and unique
        if target_difficulty != "easy":
            if min_density <= current_density <= max_density:
                # Within target range - stop pruning
                break
        
        # Check fallback condition (favor earlier linear probing to explore more configs)
        current_count = high_index - low_index + 1
        fallback_k = max(3, config.pruning_linear_fallback_k // 2)
        if should_fallback_to_linear(current_count, fallback_k):
            break
        
        mid_index = (low_index + high_index) // 2
        batch_size = mid_index - low_index + 1
        batch_positions = removable[low_index:mid_index + 1]
        
        # Snapshot before removal
        snapshot = snapshot_puzzle_state(puzzle)
        remove_clue_batch(puzzle, batch_positions)
        
        # Check uniqueness
        if check_puzzle_uniqueness(puzzle, solver_mode):
            # Success - but check if we went below minimum density
            new_clue_count = sum(
                1 for row in puzzle.grid.cells for cell in row 
                if not cell.blocked and cell.given
            )
            new_density = new_clue_count / len(path)
            
            if new_density < min_density:
                # Went too low - revert to last good state and stop
                restore_puzzle_state(puzzle, last_unique_snapshot)
                break
            
            # Success: save state and try more aggressive removal
            last_unique_snapshot = snapshot_puzzle_state(puzzle)
            state = contract_interval(low_index, high_index, "density_met")
            session.record_interval_contraction(state)
            low_index = state.low_index
        else:
            # Failure: revert and try repair (T05-T08)
            restore_puzzle_state(puzzle, snapshot)
            session.record_uniqueness_failure()
            
            # Check if we can repair
            if session.repairs_used < config.pruning_max_repairs:
                repair_succeeded = False

                # T037: If long head/tail detected, inject a mid-range anchor to stabilize
                density = _compute_clue_density(puzzle)
                if (puzzle.constraints.allow_diagonal
                        and puzzle.grid.rows >= 9
                        and density < SPARSE_DENSITY_THRESHOLD):
                    tail_len, _ = _detect_high_value_tail(puzzle)
                    head_len, _ = _detect_low_value_head(puzzle)
                    if tail_len >= TAIL_REJECT_LEN or head_len >= TAIL_REJECT_LEN:
                        # Pick a mid-range value near the center that's not currently a given
                        min_v = puzzle.constraints.min_value
                        max_v = puzzle.constraints.max_value
                        target_vals = []
                        mid = (min_v + max_v) // 2
                        # Prefer a small window around the midpoint
                        for delta in range(0, 8):
                            if mid - delta >= min_v:
                                target_vals.append(mid - delta)
                            if mid + delta <= max_v:
                                target_vals.append(mid + delta)
                        placed_givens = {cell.value for row in puzzle.grid.cells for cell in row if cell.given and not cell.blocked}
                        injected = False
                        for tv in target_vals:
                            if tv in placed_givens:
                                continue
                            # Find the cell with this value in the solution snapshot
                            chosen_pos = None
                            for row in puzzle.grid.cells:
                                for cell in row:
                                    if not cell.blocked and cell.value == tv:
                                        chosen_pos = cell.pos
                                        break
                                if chosen_pos:
                                    break
                            if chosen_pos is not None:
                                puzzle.grid.get_cell(chosen_pos).given = True
                                session.record_repair()
                                # Re-check uniqueness
                                if check_puzzle_uniqueness(puzzle, solver_mode):
                                    repair_succeeded = True
                                    last_unique_snapshot = snapshot_puzzle_state(puzzle)
                                else:
                                    # Revert if didn't help
                                    puzzle.grid.get_cell(chosen_pos).given = False
                                injected = True
                                break
                        if injected and repair_succeeded:
                            continue
                
                # T036: Try structural repair first if enabled (US2)
                if config.structural_repair_enabled:
                    # Sample alternate solutions for structural repair
                    current_givens_list = [
                        (cell.pos.row, cell.pos.col, cell.value)
                        for row in puzzle.grid.cells for cell in row
                        if not cell.blocked and cell.given
                    ]
                    
                    alternates = sample_alternate_solutions(
                        puzzle, path, solver_mode,
                        config.pruning_alternates_count,
                        time_cap_ms=2000
                    )
                    
                    if alternates and len(alternates) > 1:
                        # Attempt structural repair (blocking)
                        repair_result = apply_structural_repair(
                            grid=puzzle.grid,
                            givens=current_givens_list,
                            solutions=alternates,
                            max_repairs=config.structural_repair_max,
                            timeout_ms=config.structural_repair_timeout_ms,
                            allow_clue_fallback=False,
                            verify_solvability=False  # Skip for now, TODO: Puzzle integration
                        )
                        
                        if repair_result and repair_result.get('actions'):
                            # Structural repair applied blocks
                            session.record_repair()
                            
                            # Re-check uniqueness after structural repair
                            if check_puzzle_uniqueness(puzzle, solver_mode):
                                repair_succeeded = True
                                last_unique_snapshot = snapshot_puzzle_state(puzzle)
                            else:
                                # Structural repair didn't restore uniqueness, revert
                                restore_puzzle_state(puzzle, snapshot)
                
                # Fallback to clue-based repair if structural repair disabled or failed
                if not repair_succeeded:
                    current_givens = {
                        cell.pos for row in puzzle.grid.cells for cell in row
                        if not cell.blocked and cell.given
                    }
                    
                    alternates = sample_alternate_solutions(
                        puzzle, path, solver_mode,
                        config.pruning_alternates_count,
                        time_cap_ms=2000
                    )
                    
                    if alternates and len(alternates) > 1:
                        # Build ambiguity profile
                        profile = build_ambiguity_profile(
                            alternates, path, current_givens
                        )
                        
                        # Select repair candidate
                        candidates = select_repair_candidates(
                            profile, path, config.pruning_repair_topn
                        )
                        
                        if candidates:
                            # Apply first repair candidate
                            apply_repair_clue(puzzle, candidates[0])
                            session.record_repair()
                            
                            # Re-check uniqueness after repair
                            if check_puzzle_uniqueness(puzzle, solver_mode):
                                # Repair succeeded, continue with current interval
                                repair_succeeded = True
                                last_unique_snapshot = snapshot_puzzle_state(puzzle)
                            else:
                                # Repair didn't help, revert and contract
                                restore_puzzle_state(puzzle, snapshot)
                
                # Continue if any repair succeeded
                if repair_succeeded:
                    continue
            
            # Contract interval (either no repair or repair failed)
            state = contract_interval(low_index, high_index, "uniqueness_fail")
            session.record_interval_contraction(state)
            high_index = state.high_index
    
    # Check if we exhausted repairs or timed out
    final_status = PruningStatus.SUCCESS
    
    if session.timeout_occurred:
        final_status = PruningStatus.ABORTED_TIMEOUT
    elif session.repairs_used >= config.pruning_max_repairs:
        # Restore last known unique state
        restore_puzzle_state(puzzle, last_unique_snapshot)
        if not check_puzzle_uniqueness(puzzle, solver_mode):
            final_status = PruningStatus.ABORTED_MAX_REPAIRS
        else:
            final_status = PruningStatus.SUCCESS_WITH_REPAIRS
    elif session.repairs_used > 0:
        final_status = PruningStatus.SUCCESS_WITH_REPAIRS
    
    # Post-pruning optimization passes
    # 1) De-chunk: reduce large contiguous clusters
    # 2) Iterative thinning: smart removal targeting density while preserving gaps
    # Only for diagonal 9x9+ boards
    if puzzle.constraints.allow_diagonal and puzzle.grid.rows >= 5:
        # Removal budget on minimum density target minus whatever has been removed so far
        base_removal_budget = (1.0-min_density)*len(path)
        cells_already_removed_during_pruning = sum(
            1 for row in puzzle.grid.cells for cell in row 
            if not cell.blocked and not cell.given
        )
        removal_budget = base_removal_budget - cells_already_removed_during_pruning
        # De-chunk pass
        removed_dechunk = dechunk_given_clusters(
            puzzle, path, solver_mode, max_cluster_size=8, removal_budget=removal_budget, reverse=False
        )
        
        if removed_dechunk > 0:
            final_status = PruningStatus.SUCCESS_WITH_REPAIRS
        
        # Iterative thinning pass - target hard difficulty range
        current_clue_count = sum(
            1 for row in puzzle.grid.cells for cell in row 
            if not cell.blocked and cell.given
        )
        current_density = current_clue_count / len(path)
        
        # Only thin if still above target
        if current_density > max_density:
            removed_thinning = iterative_gap_safe_thinning(
                puzzle=puzzle,
                path=path,
                solver_mode=solver_mode,
                target_min_density=min_density,
                target_max_density=max_density,
                max_gap=MAX_VALUE_GAP,
                max_iterations=25,
                batch_size_init=2,  # even smaller batches to explore more configs
            )
            if removed_thinning > 0:
                final_status = PruningStatus.SUCCESS_WITH_REPAIRS

    # Calculate final metrics
    final_clue_count = sum(
        1 for row in puzzle.grid.cells for cell in row 
        if not cell.blocked and cell.given
    )
    
    return PruningResult(
        puzzle=puzzle,
        status=final_status,
        session=session,
        final_clue_count=final_clue_count,
        final_density=final_clue_count / len(path),
        time_ms=(time.time() - start_time) * 1000
    )


def compute_pruning_hash(puzzle: Puzzle, path: list[Position], difficulty: str) -> str:
    """Compute deterministic hash of pruning result.
    
    T13: Stable hash for determinism verification across runs.
    
    Args:
        puzzle: Final pruned puzzle
        path: Solution path
        difficulty: Target difficulty
    
    Returns:
        Hex digest string of SHA256 hash
    """
    import hashlib
    
    # Collect givens in deterministic order
    givens = []
    for pos in path:
        cell = puzzle.grid.get_cell(pos)
        if cell.given:
            givens.append((pos.row, pos.col, cell.value))
    givens.sort()
    
    # Build hashable string
    hash_parts = [
        f"difficulty={difficulty}",
        f"path_len={len(path)}",
        f"givens={givens}"
    ]
    hash_input = "|".join(hash_parts).encode('utf-8')
    
    return hashlib.sha256(hash_input).hexdigest()



