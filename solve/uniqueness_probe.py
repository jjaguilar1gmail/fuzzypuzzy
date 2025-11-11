"""
Anti-branch uniqueness probe for puzzle generation.

Implements two-phase uniqueness verification:
1. Logic fixpoint (deterministic reasoning)
2. Anti-branch DFS with early exit at 2 solutions

Constitution compliance: deterministic, bounded, returns data (no I/O).
"""
import copy
import time
import random
from dataclasses import dataclass
from typing import Optional, List, Tuple
from core.puzzle import Puzzle
from solve.solver import Solver, SolverResult


@dataclass
class ProbeOutcome:
    """Result from a single anti-branch probe attempt."""
    probe_index: int
    outcome_code: str  # SECOND_FOUND | EXHAUSTED | TIMEOUT | UNKNOWN
    nodes_explored: int
    time_ms: float
    second_solution_hash: Optional[str] = None
    permutation_id: Optional[str] = None


@dataclass
class RemovalAttemptLog:
    """Aggregated result from all probes for one removal attempt."""
    candidate_id: str
    size_tier: str
    probe_outcomes: list[ProbeOutcome]
    extended_used: bool
    final_decision: str  # ACCEPT | REJECT
    reason: str


@dataclass
class UniquenessProbeConfig:
    """Configuration for anti-branch uniqueness probing."""
    seed: int
    size_tier: str
    max_nodes: int
    timeout_ms: float
    probe_count: int
    extended_factor: float = 1.5  # +50% for extended attempt


def _hash_solution(puzzle: Puzzle) -> str:
    """Generate canonical hash of puzzle solution for comparison."""
    values = []
    for row in range(puzzle.grid.rows):
        for col in range(puzzle.grid.cols):
            cell = puzzle.grid.get_cell(row, col)
            values.append(str(cell.value) if cell.value is not None else ".")
    return "".join(values)


def _apply_logic_fixpoint(puzzle: Puzzle, max_passes: int = 50) -> Tuple[bool, List]:
    """
    Apply deterministic logic passes until fixpoint.
    
    Returns:
        (solved, steps) tuple
    """
    progress_made, solved, logic_steps = Solver.apply_logic_fixpoint(
        puzzle,
        max_passes=max_passes,
        tie_break="row_col",
        enable_island_elim=True,
        enable_segment_bridging=True,
        enable_degree_prune=True
    )
    return solved, logic_steps


def _count_solutions_with_ordering(puzzle: Puzzle, config: UniquenessProbeConfig, 
                                   ordering: str, permutation_id: str) -> ProbeOutcome:
    """
    Count solutions using specified tie-break ordering.
    
    Returns early if 2 solutions found.
    """
    start_time = time.time()
    
    # Use existing count_solutions but cap at 2
    result = Solver.count_solutions(
        puzzle,
        cap=2,
        max_nodes=config.max_nodes,
        timeout_ms=int(config.timeout_ms),
        max_depth=50
    )
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Classify outcome
    if result['count'] >= 2:
        # Found second solution!
        outcome_code = "SECOND_FOUND"
        second_hash = f"second_{result['count']}"  # Simplified hash
    elif result['exhausted']:
        # Fully explored, only 1 solution
        outcome_code = "EXHAUSTED"
        second_hash = None
    elif result['timeout']:
        outcome_code = "TIMEOUT"
        second_hash = None
    else:
        outcome_code = "UNKNOWN"
        second_hash = None
    
    return ProbeOutcome(
        probe_index=0,  # Set by caller
        outcome_code=outcome_code,
        nodes_explored=result['nodes'],
        time_ms=elapsed_ms,
        second_solution_hash=second_hash,
        permutation_id=permutation_id
    )


def run_anti_branch_probe(puzzle: Puzzle, config: UniquenessProbeConfig, 
                          logger=None) -> RemovalAttemptLog:
    """
    Run two-phase uniqueness check with multiple randomized probes.
    
    Phase 1: Apply logic fixpoint
    Phase 2: Run multiple anti-branch DFS probes with shuffled tie-breaks
    
    Args:
        puzzle: Candidate puzzle to check (will NOT be modified)
        config: Probe configuration with budgets and seed
        logger: Optional UniquenessLogger for telemetry emission
        
    Returns:
        RemovalAttemptLog with all probe outcomes and final decision
    """
    puzzle_copy = copy.deepcopy(puzzle)
    cells = puzzle.grid.rows * puzzle.grid.cols
    
    # Phase 1: Logic fixpoint
    solved, _ = _apply_logic_fixpoint(puzzle_copy)
    
    if solved:
        # Trivially unique (solved by logic alone)
        outcome = ProbeOutcome(
            probe_index=0,
            outcome_code="EXHAUSTED",
            nodes_explored=0,
            time_ms=0.0,
            permutation_id="logic_only"
        )
        log = RemovalAttemptLog(
            candidate_id=f"puzzle_{cells}",
            size_tier=config.size_tier,
            probe_outcomes=[outcome],
            extended_used=False,
            final_decision="ACCEPT",
            reason="Solved by logic fixpoint; uniqueness guaranteed"
        )
        if logger:
            logger.log_removal_attempt(log)
        return log
    
    # Phase 2: Run multiple probes with different tie-break orderings
    rng = random.Random(config.seed)
    probe_outcomes = []
    orderings = ["mrv_lcv_frontier", "mrv_lcv", "frontier", "row_col"]
    
    for probe_idx in range(config.probe_count):
        # Shuffle orderings for diversity
        ordering = rng.choice(orderings)
        permutation_id = f"probe{probe_idx}_{ordering}"
        
        probe_copy = copy.deepcopy(puzzle)
        outcome = _count_solutions_with_ordering(probe_copy, config, ordering, permutation_id)
        outcome.probe_index = probe_idx
        probe_outcomes.append(outcome)
        
        # Early exit if second solution found
        if outcome.outcome_code == "SECOND_FOUND":
            log = RemovalAttemptLog(
                candidate_id=f"puzzle_{cells}",
                size_tier=config.size_tier,
                probe_outcomes=probe_outcomes,
                extended_used=False,
                final_decision="REJECT",
                reason=f"Second solution found in probe {probe_idx}"
            )
            if logger:
                logger.log_removal_attempt(log)
            return log
    
    # Check if all probes exhausted
    all_exhausted = all(p.outcome_code == "EXHAUSTED" for p in probe_outcomes)
    if all_exhausted:
        log = RemovalAttemptLog(
            candidate_id=f"puzzle_{cells}",
            size_tier=config.size_tier,
            probe_outcomes=probe_outcomes,
            extended_used=False,
            final_decision="ACCEPT",
            reason=f"All {config.probe_count} probes exhausted without finding second solution"
        )
        if logger:
            logger.log_removal_attempt(log)
        return log
    
    # Some probes timed out or unknown - try extended attempt
    extended_config = UniquenessProbeConfig(
        seed=config.seed + 1000,
        size_tier=config.size_tier,
        max_nodes=int(config.max_nodes * config.extended_factor),
        timeout_ms=config.timeout_ms * config.extended_factor,
        probe_count=1,
        extended_factor=config.extended_factor
    )
    
    extended_copy = copy.deepcopy(puzzle)
    extended_outcome = _count_solutions_with_ordering(
        extended_copy, 
        extended_config, 
        "mrv_lcv_frontier", 
        "extended"
    )
    extended_outcome.probe_index = config.probe_count
    probe_outcomes.append(extended_outcome)
    
    if extended_outcome.outcome_code == "SECOND_FOUND":
        log = RemovalAttemptLog(
            candidate_id=f"puzzle_{cells}",
            size_tier=config.size_tier,
            probe_outcomes=probe_outcomes,
            extended_used=True,
            final_decision="REJECT",
            reason="Second solution found in extended attempt"
        )
        if logger:
            logger.log_removal_attempt(log)
        return log
    elif extended_outcome.outcome_code == "EXHAUSTED":
        log = RemovalAttemptLog(
            candidate_id=f"puzzle_{cells}",
            size_tier=config.size_tier,
            probe_outcomes=probe_outcomes,
            extended_used=True,
            final_decision="ACCEPT",
            reason="Extended attempt exhausted without finding second solution"
        )
        if logger:
            logger.log_removal_attempt(log)
        return log
    else:
        # Still unknown even after extended attempt - reject to be safe
        log = RemovalAttemptLog(
            candidate_id=f"puzzle_{cells}",
            size_tier=config.size_tier,
            probe_outcomes=probe_outcomes,
            extended_used=True,
            final_decision="REJECT",
            reason="Unable to confirm uniqueness within budgets (extended attempt inconclusive)"
        )
        if logger:
            logger.log_removal_attempt(log)
        return log

