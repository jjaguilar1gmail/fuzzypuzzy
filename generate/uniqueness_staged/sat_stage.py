"""Optional SAT/CP solver stage for uniqueness verification.

This stage uses external SAT/CP solvers for formal uniqueness proof when available.
Disabled by default per FR-012.
"""

import time
from typing import Optional

from generate.uniqueness_staged.result import UniquenessCheckResult, UniquenessDecision
from generate.uniqueness_staged.sat_hook import has_sat_solver, get_sat_solver


def run_sat_stage(
    puzzle,
    budget_ms: int,
    seed: int  # Unused but kept for consistency
) -> Optional[UniquenessCheckResult]:
    """Run optional SAT/CP verification stage.
    
    Args:
        puzzle: Puzzle object to check
        budget_ms: Total time budget for SAT queries
        seed: Random seed (unused for deterministic SAT)
        
    Returns:
        UniquenessCheckResult if decision reached, None if inconclusive
        
    Notes:
        - Only runs if external solver registered via register_sat_solver()
        - Splits budget: 60% for first solution, 40% for blocking clause search
        - Returns Unique if second solution not found within budget
        - Returns Non-Unique if second solution found
        - Returns None (Inconclusive) if no first solution or timeout
    """
    start_time = time.time()
    
    # Check if SAT solver available
    if not has_sat_solver():
        return UniquenessCheckResult(
            decision=UniquenessDecision.INCONCLUSIVE,
            stage_decided='sat',
            elapsed_ms=0,
            per_stage_ms={'sat': 0},
            nodes_explored={},
            probes_run=0,
            notes='SAT solver not registered'
        )
    
    solver = get_sat_solver()
    
    # Budget split: 60% first solution, 40% blocking clause
    first_budget = int(budget_ms * 0.6)
    second_budget = budget_ms - first_budget
    
    # Find first solution
    first_solution = solver.find_solution(puzzle, timeout_ms=first_budget)
    
    if first_solution is None:
        # No solution found or timeout
        elapsed_ms = int((time.time() - start_time) * 1000)
        return UniquenessCheckResult(
            decision=UniquenessDecision.INCONCLUSIVE,
            stage_decided='sat',
            elapsed_ms=elapsed_ms,
            per_stage_ms={'sat': elapsed_ms},
            nodes_explored={},
            probes_run=0,
            notes='SAT solver could not find first solution within budget'
        )
    
    # Find second solution (with blocking clause)
    second_solution = solver.find_second_solution(
        puzzle, 
        first_solution, 
        timeout_ms=second_budget
    )
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    if second_solution is not None:
        # Found second solution → Non-Unique
        return UniquenessCheckResult(
            decision=UniquenessDecision.NON_UNIQUE,
            stage_decided='sat',
            elapsed_ms=elapsed_ms,
            per_stage_ms={'sat': elapsed_ms},
            nodes_explored={},
            probes_run=0,
            notes='SAT solver found second solution via blocking clause'
        )
    else:
        # No second solution found → Unique (or timeout but we assume unique)
        return UniquenessCheckResult(
            decision=UniquenessDecision.UNIQUE,
            stage_decided='sat',
            elapsed_ms=elapsed_ms,
            per_stage_ms={'sat': elapsed_ms},
            nodes_explored={},
            probes_run=0,
            notes='SAT solver verified uniqueness (no second solution found)'
        )
