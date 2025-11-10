"""Early-exit bounded backtracking for uniqueness checking.

Stage 1 of the staged uniqueness pipeline. Uses diverse heuristics
to quickly detect non-unique puzzles by finding a second solution.
"""

import time
from copy import deepcopy
from typing import Optional, Tuple, Dict, TYPE_CHECKING

from generate.uniqueness_staged.result import UniquenessDecision, UniquenessCheckResult, StrategyProfile
from generate.uniqueness_staged.registry import list_strategies

if TYPE_CHECKING:
    from core.puzzle import Puzzle
    from solve.candidates import CandidateModel


def run_early_exit_stage(
    puzzle: 'Puzzle',
    budget_ms: int,
    seed: int
) -> Optional[UniquenessCheckResult]:
    """Run early-exit stage with diverse heuristics.
    
    Tries multiple heuristic profiles with solution cap=2.
    Returns immediately if second solution found (Non-Unique).
    
    Args:
        puzzle: Puzzle object to check (NOT MODIFIED - read-only per FR-010)
        budget_ms: Total time budget across all heuristics
        seed: Random seed for reproducibility
        
    Returns:
        UniquenessCheckResult if Non-Unique detected, None if inconclusive
        
    Notes:
        - IMMUTABILITY: Does not modify puzzle parameter
        - Bounded search creates internal solver state copies
        - Early returns on finding 2+ solutions (FR-006)
    """
    start_time = time.time()
    total_nodes = 0
    
    # Get registered heuristic profiles
    profiles = [p for p in list_strategies() if 'detect_non_unique' in p.capabilities]
    
    # Allocate time evenly across profiles
    if not profiles:
        return None
    
    per_profile_budget_ms = budget_ms // len(profiles)
    
    # Try each heuristic profile
    for profile in profiles:
        # Check if we've exceeded total budget
        elapsed_ms = int((time.time() - start_time) * 1000)
        if elapsed_ms >= budget_ms:
            break
        
        remaining_ms = budget_ms - elapsed_ms
        profile_budget = min(per_profile_budget_ms, remaining_ms)
        
        # Run bounded search with this profile
        result = _bounded_search(
            puzzle=puzzle,
            solution_cap=2,
            timeout_ms=profile_budget,
            profile=profile,
            seed=seed
        )
        
        total_nodes += result['nodes']
        
        # If we found 2+ solutions, immediately return Non-Unique
        if result['solutions_found'] >= 2:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return UniquenessCheckResult(
                decision=UniquenessDecision.NON_UNIQUE,
                stage_decided='early_exit',
                elapsed_ms=elapsed_ms,
                per_stage_ms={'early_exit': elapsed_ms},
                nodes_explored={'early_exit': total_nodes},
                probes_run=0,
                notes=f'Found multiple solutions using profile {profile.id}'
            )
    
    # Didn't find non-unique evidence
    return None


def _bounded_search(
    puzzle: 'Puzzle',
    solution_cap: int,
    timeout_ms: int,
    profile: 'StrategyProfile',
    seed: int
) -> Dict:
    """Bounded backtracking search with heuristic ordering.
    
    Args:
        puzzle: Puzzle to solve
        solution_cap: Stop after finding this many solutions
        timeout_ms: Time budget
        profile: Heuristic profile for ordering
        seed: Random seed
        
    Returns:
        Dict with solutions_found, nodes, timed_out
    """
    import time
    from solve.solver import Solver
    from solve.candidates import CandidateModel
    
    start_time = time.time()
    solutions_found = 0
    nodes_explored = 0
    timed_out = False
    
    def is_timeout() -> bool:
        return (time.time() - start_time) * 1000 > timeout_ms
    
    def search_recursive(puzzle_state, depth: int) -> bool:
        """Recursive search with solution counting."""
        nonlocal solutions_found, nodes_explored, timed_out
        
        nodes_explored += 1
        
        # Check timeout
        if is_timeout():
            timed_out = True
            return False
        
        # Check if we've found enough solutions
        if solutions_found >= solution_cap:
            return False  # Stop searching
        
        # Apply logic passes (v2: corridors, degree, islands)
        solver = Solver(puzzle_state)
        progress_made, solved, logic_steps = Solver.apply_logic_fixpoint(
            puzzle_state,
            max_passes=10,  # Limited passes for speed
            tie_break='row_col',
            enable_island_elim=True,
            enable_segment_bridging=True,
            enable_degree_prune=True
        )
        
        # Check if solved
        if solved or solver._is_solved():
            solutions_found += 1
            return solutions_found < solution_cap  # Continue if need more solutions
        
        # Build candidate model for search
        candidates = CandidateModel()
        candidates.init_from(puzzle_state)
        
        # Check for contradictions
        if candidates.has_empty_candidates():
            return True  # Continue searching other branches
        
        # Choose next value using profile's position/value ordering
        ordering = profile.params.get('position_order', 'row_major')
        choice = _choose_variable_with_profile(candidates, ordering, puzzle_state)
        
        if choice is None:
            return True  # Continue searching
        
        value, positions = choice
        
        # Try each position for the chosen value
        for pos in positions:
            if is_timeout():
                timed_out = True
                return False
            
            # Check solution cap again
            if solutions_found >= solution_cap:
                return False
            
            # Create new puzzle state with this assignment
            new_puzzle = solver._copy_puzzle(puzzle_state)
            new_cell = new_puzzle.grid.get_cell(pos)
            new_cell.value = value
            
            # Recursive search
            if not search_recursive(new_puzzle, depth + 1):
                return False  # Timeout or solution cap reached
        
        return True  # Continue searching
    
    # Start search from a copy of the puzzle
    puzzle_copy = deepcopy(puzzle)
    search_recursive(puzzle_copy, 0)
    
    return {
        'solutions_found': solutions_found,
        'nodes': nodes_explored,
        'timed_out': timed_out
    }


def _choose_variable_with_profile(candidates: 'CandidateModel', ordering: str, puzzle) -> Optional[Tuple[int, list]]:
    """Choose next value and positions using profile ordering.
    
    Args:
        candidates: Candidate model
        ordering: Position ordering strategy
        puzzle: Current puzzle state
        
    Returns:
        (value, ordered_positions) or None
    """
    from core.position import Position
    
    # Find value with minimum remaining positions (MRV)
    min_count = float('inf')
    best_value = None
    
    for value, positions in candidates.value_to_positions.items():
        if len(positions) < min_count and len(positions) > 0:
            min_count = len(positions)
            best_value = value
    
    if best_value is None:
        return None
    
    positions = list(candidates.value_to_positions[best_value])
    
    # Order positions based on profile
    if ordering == 'row_major':
        positions.sort(key=lambda p: (p.row, p.col))
    elif ordering == 'center_out':
        # Sort by distance from center
        center_row = puzzle.grid.rows // 2
        center_col = puzzle.grid.cols // 2
        positions.sort(key=lambda p: abs(p.row - center_row) + abs(p.col - center_col))
    elif ordering == 'mrv':
        # Already using MRV for value selection, use row_major for positions
        positions.sort(key=lambda p: (p.row, p.col))
    elif ordering == 'degree':
        # Order by neighbor count (degree-based)
        def degree_key(p):
            neighbors = puzzle.grid.neighbors_of(p)
            return -len(neighbors)  # Higher degree first
        positions.sort(key=degree_key)
    else:
        # Default: row_major
        positions.sort(key=lambda p: (p.row, p.col))
    
    return (best_value, positions)
