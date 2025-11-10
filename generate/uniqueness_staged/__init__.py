"""Staged uniqueness validation for Hidato puzzles.

Provides a multi-stage pipeline for uniqueness checking:
- Stage 1: Early-exit bounded backtracking with diverse heuristics
- Stage 2: Randomized solver probes with seeded RNG
- Stage 3: Optional SAT/CP verification via external hook

All stages respect strict time budgets and return tri-state decisions:
Unique, Non-Unique, or Inconclusive.
"""

from generate.uniqueness_staged.result import (
    UniquenessCheckRequest,
    UniquenessCheckResult,
    UniquenessDecision,
)
from generate.uniqueness_staged.config import UniquenessConfig

__all__ = [
    'UniquenessCheckRequest',
    'UniquenessCheckResult',
    'UniquenessDecision',
    'UniquenessConfig',
    'check_uniqueness',
    'create_request',
    'enable_stage',
    'disable_stage',
]


def create_request(
    puzzle,
    size: int,
    adjacency: int = 8,
    difficulty: str = "medium",
    seed: int = 0,
    enable_early_exit: bool = True,
    enable_probes: bool = True,
    enable_sat: bool = False
) -> UniquenessCheckRequest:
    """Create a UniquenessCheckRequest with sensible defaults.
    
    Args:
        puzzle: Puzzle object to check
        size: Grid size
        adjacency: Adjacency mode (4 or 8)
        difficulty: Difficulty level (easy/medium/hard)
        seed: Random seed for reproducibility
        enable_early_exit: Enable early-exit stage
        enable_probes: Enable randomized probes stage
        enable_sat: Enable optional SAT/CP stage
        
    Returns:
        Configured request ready for check_uniqueness()
    """
    # Get default budget for difficulty per FR-014
    if size <= 5:
        total_budget_ms = 100
    else:
        budget_map = {'easy': 600, 'medium': 500, 'hard': 400}
        total_budget_ms = budget_map.get(difficulty, 500)
    
    return UniquenessCheckRequest(
        puzzle=puzzle,
        size=size,
        adjacency=adjacency,
        difficulty=difficulty,
        total_budget_ms=total_budget_ms,
        seed=seed,
        strategy_flags={
            'early_exit': enable_early_exit,
            'probes': enable_probes,
            'sat': enable_sat
        }
    )


def enable_stage(request: UniquenessCheckRequest, stage: str) -> None:
    """Enable a specific stage in the request.
    
    Args:
        request: Request to modify
        stage: Stage name ('early_exit', 'probes', or 'sat')
    """
    if stage not in {'early_exit', 'probes', 'sat'}:
        raise ValueError(f"Unknown stage: {stage}. Must be one of: early_exit, probes, sat")
    request.strategy_flags[stage] = True


def disable_stage(request: UniquenessCheckRequest, stage: str) -> None:
    """Disable a specific stage in the request.
    
    Args:
        request: Request to modify
        stage: Stage name ('early_exit', 'probes', or 'sat')
    """
    if stage not in {'early_exit', 'probes', 'sat'}:
        raise ValueError(f"Unknown stage: {stage}. Must be one of: early_exit, probes, sat")
    request.strategy_flags[stage] = False


def check_uniqueness(request: UniquenessCheckRequest) -> UniquenessCheckResult:
    """Check puzzle uniqueness using staged multi-strategy pipeline.
    
    Args:
        request: Configuration including size, difficulty, budgets, seed
        
    Returns:
        Result with decision (Unique/Non-Unique/Inconclusive) and metrics
        
    Raises:
        ValueError: If request validation fails
        
    Notes:
        - IMMUTABILITY: Does not modify request.puzzle (FR-010)
        - Each stage operates on puzzle snapshots or read-only access
        - Deterministic: same seed + config → identical outcomes (FR-013)
        - Early returns: exits immediately when Non-Unique detected (FR-006)
    """
    import time
    import logging
    from generate.uniqueness_staged.result import UniquenessDecision
    
    logger = logging.getLogger(__name__)
    start_time = time.time()
    per_stage_ms = {}
    nodes_explored = {}
    probes_run = 0
    
    # Log configuration
    logger.debug(f"Starting uniqueness check: size={request.size}, difficulty={request.difficulty}, "
                 f"budget={request.total_budget_ms}ms, seed={request.seed}")
    
    # Note: FR-003 specifies small boards (≤25 cells) could use exhaustive enumeration
    # For now, we use the same early-exit/probes stages for all sizes
    # This works fine and is consistent across board sizes
    
    # Stage 1: Early-exit search (T011-T017 implemented)
    if request.strategy_flags.get('early_exit', True):
        from generate.uniqueness_staged.early_exit import run_early_exit_stage
        
        stage_start = time.time()
        
        # Calculate budget for this stage
        early_exit_budget = int(request.total_budget_ms * request.stage_budget_split.get('early_exit', 0.4))
        
        # Check remaining budget
        elapsed_ms = int((time.time() - start_time) * 1000)
        remaining_budget = request.total_budget_ms - elapsed_ms
        if remaining_budget > 0:
            stage_budget = min(early_exit_budget, remaining_budget)
            
            logger.debug(f"Running early_exit stage: budget={stage_budget}ms")
            
            result = run_early_exit_stage(
                puzzle=request.puzzle,
                budget_ms=stage_budget,
                seed=request.seed
            )
            
            stage_elapsed = int((time.time() - stage_start) * 1000)
            per_stage_ms['early_exit'] = stage_elapsed
            
            # If we found non-unique, return immediately
            if result is not None:
                logger.info(f"Early-exit stage decided: {result.decision.value} in {stage_elapsed}ms")
                return result
            else:
                logger.debug(f"Early-exit inconclusive after {stage_elapsed}ms")
    
    # Stage 2: Randomized probes (T022-T024 will implement)
    if request.strategy_flags.get('probes', True):
        from generate.uniqueness_staged.probes import run_probes_stage
        
        stage_start = time.time()
        
        # Calculate budget for this stage
        probes_budget = int(request.total_budget_ms * request.stage_budget_split.get('probes', 0.4))
        
        # Check remaining budget
        elapsed_ms = int((time.time() - start_time) * 1000)
        remaining_budget = request.total_budget_ms - elapsed_ms
        if remaining_budget > 0:
            stage_budget = min(probes_budget, remaining_budget)
            
            logger.debug(f"Running probes stage: budget={stage_budget}ms")
            
            result = run_probes_stage(
                puzzle=request.puzzle,
                budget_ms=stage_budget,
                seed=request.seed,
                num_probes=5  # Default to 5 probes per FR-013
            )
            
            stage_elapsed = int((time.time() - stage_start) * 1000)
            per_stage_ms['probes'] = stage_elapsed
            
            # If we found non-unique, return immediately
            if result is not None:
                probes_run = result.probes_run
                logger.info(f"Probes stage decided: {result.decision.value} in {stage_elapsed}ms ({probes_run} probes)")
                return result
            else:
                logger.debug(f"Probes stage inconclusive after {stage_elapsed}ms")
    
    # Stage 3: Optional SAT/CP (T025-T027 will implement)
    if request.strategy_flags.get('sat', False):
        from generate.uniqueness_staged.sat_stage import run_sat_stage
        
        stage_start = time.time()
        
        # Calculate budget for this stage
        sat_budget = int(request.total_budget_ms * request.stage_budget_split.get('sat', 0.2))
        
        # Check remaining budget
        elapsed_ms = int((time.time() - start_time) * 1000)
        remaining_budget = request.total_budget_ms - elapsed_ms
        if remaining_budget > 0:
            stage_budget = min(sat_budget, remaining_budget)
            
            logger.debug(f"Running SAT stage: budget={stage_budget}ms")
            
            result = run_sat_stage(
                puzzle=request.puzzle,
                budget_ms=stage_budget,
                seed=request.seed
            )
            
            stage_elapsed = int((time.time() - stage_start) * 1000)
            per_stage_ms['sat'] = stage_elapsed
            
            # SAT stage can return any decision (Unique/Non-Unique/Inconclusive)
            # If it reached a decision (not None), return it
            if result is not None and result.decision != UniquenessDecision.INCONCLUSIVE:
                logger.info(f"SAT stage decided: {result.decision.value} in {stage_elapsed}ms")
                return result
            else:
                logger.debug(f"SAT stage inconclusive after {stage_elapsed}ms")
    
    # If no stage found non-unique, return inconclusive for now
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"All stages completed: inconclusive after {elapsed_ms}ms "
                f"(stages run: {list(per_stage_ms.keys())})")
    
    return UniquenessCheckResult(
        decision=UniquenessDecision.INCONCLUSIVE,
        stage_decided='all_stages_exhausted',
        elapsed_ms=elapsed_ms,
        per_stage_ms=per_stage_ms,
        nodes_explored=nodes_explored,
        probes_run=probes_run,
        notes=f'All enabled stages ran without finding second solution (stages: {list(per_stage_ms.keys())})'
    )
