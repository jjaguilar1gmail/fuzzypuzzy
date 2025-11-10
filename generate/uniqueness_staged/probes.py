"""Randomized probe-based uniqueness checking with deterministic seeding.

This stage performs multiple solver runs with randomized decision ordering,
aiming to discover second solutions through diverse search paths.
"""

import random
import time
from typing import Optional

from generate.uniqueness_staged.result import UniquenessCheckResult, UniquenessDecision


def run_probes_stage(
    puzzle,
    budget_ms: int,
    seed: int,
    num_probes: int = 5
) -> Optional[UniquenessCheckResult]:
    """Run randomized solver probes to search for second solution.
    
    Args:
        puzzle: Puzzle object to check
        budget_ms: Total time budget for all probes
        seed: Random seed for deterministic probe generation
        num_probes: Number of independent probe runs
        
    Returns:
        UniquenessCheckResult if Non-Unique detected, None if all probes found ≤1 solution
        
    Notes:
        - Each probe uses different randomized decision ordering
        - Seeded RNG ensures identical outcomes for same seed+puzzle
        - Early returns on second solution found
        - Probes share budget equally (budget_ms / num_probes per probe)
    """
    start_time = time.time()
    per_probe_budget = budget_ms // num_probes if num_probes > 0 else budget_ms
    
    # Seed the RNG for deterministic probe generation
    rng = random.Random(seed)
    
    solutions_found = 0
    nodes_explored = 0
    probes_completed = 0
    
    for probe_idx in range(num_probes):
        # Check if we've exceeded total budget
        elapsed_ms = int((time.time() - start_time) * 1000)
        if elapsed_ms >= budget_ms:
            break
        
        # Generate probe-specific seed deterministically
        probe_seed = rng.randint(0, 2**31 - 1)
        
        # Run probe with randomized ordering
        probe_result = _run_single_probe(
            puzzle=puzzle,
            budget_ms=per_probe_budget,
            seed=probe_seed
        )
        
        probes_completed += 1
        nodes_explored += probe_result.get('nodes_explored', 0)
        
        # If probe found a solution
        if probe_result.get('solution_found', False):
            solutions_found += 1
            
            # Early return if we found 2+ solutions
            if solutions_found >= 2:
                elapsed_ms = int((time.time() - start_time) * 1000)
                return UniquenessCheckResult(
                    decision=UniquenessDecision.NON_UNIQUE,
                    stage_decided='probes',
                    elapsed_ms=elapsed_ms,
                    per_stage_ms={'probes': elapsed_ms},
                    nodes_explored={'probes': nodes_explored},
                    probes_run=probes_completed,
                    notes=f'Found {solutions_found} solutions via probes (probe {probe_idx+1}/{num_probes})'
                )
    
    # All probes completed without finding 2+ solutions
    # Return None to continue to next stage
    return None


def _run_single_probe(puzzle, budget_ms: int, seed: int) -> dict:
    """Execute a single randomized solver probe.
    
    Args:
        puzzle: Puzzle to solve
        budget_ms: Time budget for this probe
        seed: Random seed for this probe's decision ordering
        
    Returns:
        Dict with keys:
            - solution_found (bool): Whether probe found a solution
            - nodes_explored (int): Number of search nodes visited
            - elapsed_ms (int): Time spent in this probe
    """
    # TODO: Implement actual randomized solver with:
    # 1. Apply solver passes (corridors, degree, islands) as usual
    # 2. Use seed to randomize value/cell ordering during backtracking
    # 3. Track nodes and respect budget_ms timeout
    # 4. Return as soon as first solution found (probe success)
    
    # Placeholder: return no solution found
    return {
        'solution_found': False,
        'nodes_explored': 0,
        'elapsed_ms': 0
    }


def generate_probe_seeds(base_seed: int, num_probes: int) -> list[int]:
    """Generate deterministic sequence of probe seeds.
    
    Args:
        base_seed: Base random seed
        num_probes: Number of probe seeds to generate
        
    Returns:
        List of probe-specific seeds in stable order
        
    Notes:
        Same base_seed always produces identical sequence (FR-013).
    """
    rng = random.Random(base_seed)
    return [rng.randint(0, 2**31 - 1) for _ in range(num_probes)]
