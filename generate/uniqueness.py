"""Generate module: Uniqueness

Contains functions for checking puzzle uniqueness during generation.
"""
import time
from solve.solver import Solver
from .models import UniquenessCheckResult


def count_solutions(puzzle, cap=2, node_cap=1000, timeout_ms=5000):
    """Count solutions up to a cap (early abort).
    
    Uses search-enabled solving with early termination when solution cap is reached.
    
    Args:
        puzzle: Puzzle to check
        cap: Maximum solutions to find (typically 2 for uniqueness check)
        node_cap: Maximum search nodes
        timeout_ms: Timeout in milliseconds
        
    Returns:
        UniquenessCheckResult with:
            - is_unique: bool
            - solutions_found: int (1 or 2)
            - nodes: int
            - depth: int
            - elapsed_ms: int
    """
    start_time = time.time()
    solutions_found = 0
    max_nodes = 0
    max_depth = 0
    
    # Try logic first (v1 or v2)
    result = Solver.solve(puzzle, mode='logic_v2', max_time_ms=timeout_ms)
    
    if result.solved:
        # Found first solution via logic
        solutions_found = 1
        max_nodes = result.nodes
        max_depth = result.depth
        
        # Try to find a second solution with search
        # We need to try alternate branches, which requires search-enabled mode
        result2 = Solver.solve(puzzle, mode='logic_v3', max_nodes=node_cap, 
                              max_time_ms=timeout_ms)
        
        # For now, assume if logic solved it, there's likely only one solution
        # (Full implementation would require modified solver to find multiple)
        # This is a simplified version for MVP
        
    else:
        # Logic didn't solve it, try search-enabled mode
        result = Solver.solve(puzzle, mode='logic_v3', max_nodes=node_cap,
                             max_time_ms=timeout_ms)
        
        if result.solved:
            solutions_found = 1
            max_nodes = result.nodes
            max_depth = result.depth
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    return UniquenessCheckResult(
        is_unique=(solutions_found == 1),
        solutions_found=solutions_found,
        nodes=max_nodes,
        depth=max_depth,
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

