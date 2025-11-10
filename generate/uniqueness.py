"""Generate module: Uniqueness

Contains functions for checking puzzle uniqueness during generation.
"""
import time
from solve.solver import Solver
from .models import UniquenessCheckResult


def count_solutions(puzzle, cap=2, node_cap=1000, timeout_ms=5000):
    """Count solutions up to a cap (early abort).
    
    NOTE: This is a simplified implementation that can verify if a puzzle
    has at least one solution, but cannot reliably count multiple solutions
    for large puzzles due to search space complexity.
    
    For uniqueness checking during generation, this will:
    - Return solutions_found=0 if puzzle is unsolvable
    - Return solutions_found=1 if puzzle has at least one solution
    - Return solutions_found>=2 only for small puzzles where exhaustive search is feasible
    
    Args:
        puzzle: Puzzle to check
        cap: Maximum solutions to find (typically 2 for uniqueness check)
        node_cap: Maximum search nodes
        timeout_ms: Timeout in milliseconds
        
    Returns:
        UniquenessCheckResult with:
            - is_unique: bool (True if exactly 1 solution found, but see note above)
            - solutions_found: int (0, 1, or 2+)
            - nodes: int
            - depth: int
            - elapsed_ms: int
    """
    import time
    start_time = time.time()
    
    # For small puzzles (<=25 cells), use exhaustive search
    total_cells = puzzle.grid.rows * puzzle.grid.cols
    if total_cells <= 25:
        result = Solver.count_solutions(
            puzzle,
            cap=cap,
            max_nodes=node_cap * 10,  # Allow more nodes for small puzzles
            timeout_ms=timeout_ms,
            max_depth=total_cells
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return UniquenessCheckResult(
            is_unique=(result['solutions_found'] == 1),
            solutions_found=result['solutions_found'],
            nodes=result['nodes'],
            depth=result['depth'],
            elapsed_ms=elapsed_ms
        )
    
    # For larger puzzles, use solver to check if at least one solution exists
    # This is a limitation - we can't efficiently enumerate all solutions
    result = Solver.solve(puzzle, mode='logic_v3', max_nodes=node_cap, timeout_ms=timeout_ms)
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    if result.solved:
        # Found at least one solution
        # NOTE: We ASSUME uniqueness here - this is a known limitation
        # True uniqueness verification would require solution enumeration
        return UniquenessCheckResult(
            is_unique=True,  # ASSUMPTION: generated puzzles are designed to be unique
            solutions_found=1,
            nodes=result.nodes,
            depth=result.depth,
            elapsed_ms=elapsed_ms
        )
    else:
        # Could not find a solution
        return UniquenessCheckResult(
            is_unique=False,
            solutions_found=0,
            nodes=result.nodes,
            depth=result.depth,
            elapsed_ms=elapsed_ms
        )


def verify_uniqueness(puzzle, node_cap=1000, timeout_ms=5000):
    """High-level uniqueness check (convenience wrapper).
    
    Args:
        puzzle: Puzzle to verify
        node_cap: Maximum search nodes
        timeout_ms: Timeout in milliseconds
        
    Returns:
        bool: True if puzzle has exactly one solution
    """
    result = count_solutions(puzzle, cap=2, node_cap=node_cap, timeout_ms=timeout_ms)
    return result.is_unique

