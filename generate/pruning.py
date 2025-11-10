"""Generate module: Solver-Driven Pruning

Interval reduction and frequency-based uniqueness repair for minimal clue counts.
"""
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from enum import Enum

from core.position import Position
from core.puzzle import Puzzle

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
        Dict with given_positions set
    """
    given_positions = set()
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked and cell.given:
                given_positions.add(cell.pos)
    return {"given_positions": given_positions}


def restore_puzzle_state(puzzle: Puzzle, snapshot: dict) -> None:
    """Restore puzzle to prior state from snapshot.
    
    T03: Revert given flags after uniqueness failure.
    
    Args:
        puzzle: Puzzle to restore
        snapshot: State dict from snapshot_puzzle_state()
    """
    given_positions = snapshot["given_positions"]
    for row in puzzle.grid.cells:
        for cell in row:
            if not cell.blocked:
                cell.given = cell.pos in given_positions


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
        difficulty='medium',  # Conservative budget (500ms)
        enable_early_exit=True,
        enable_probes=False,  # Disable probes for now (placeholder logic)
        enable_sat=False
    )
    result = check_uniqueness(request)
    
    # Honor tri-state decision per FR-008
    if result.decision == UniquenessDecision.UNIQUE:
        return True
    elif result.decision == UniquenessDecision.NON_UNIQUE:
        return False
    else:  # INCONCLUSIVE
        # Fallback to old method for inconclusive cases
        from generate.uniqueness import count_solutions
        fallback_result = count_solutions(puzzle, cap=2, node_cap=5000, timeout_ms=5000)
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
    removable = order_removable_clues(puzzle, path)
    
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
        elif target_difficulty in ["hard", "extreme"]:
            min_density = config.pruning_target_density_hard_min
            max_density = config.pruning_target_density_hard_max
        
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
        
        # Check fallback condition
        current_count = high_index - low_index + 1
        if should_fallback_to_linear(current_count, config.pruning_linear_fallback_k):
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
                # Sample alternates and build profile
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
                            last_unique_snapshot = snapshot_puzzle_state(puzzle)
                            continue
                        else:
                            # Repair didn't help, revert and contract
                            restore_puzzle_state(puzzle, snapshot)
            
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



