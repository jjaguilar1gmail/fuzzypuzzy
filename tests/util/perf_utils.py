"""Performance testing utilities for solver benchmarking."""
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class SolverMetrics:
    """Metrics captured during a solver run."""
    solved: bool
    time_ms: float
    nodes: Optional[int] = None
    depth: Optional[int] = None
    steps: int = 0
    message: str = ""


def measure_solve(solver_fn, *args, **kwargs) -> SolverMetrics:
    """
    Execute a solver function and capture timing and result metrics.
    
    Args:
        solver_fn: Callable that returns a result with solved, steps, message attributes
        *args, **kwargs: Arguments to pass to solver_fn
        
    Returns:
        SolverMetrics with timing and result data
    """
    start = time.perf_counter()
    result = solver_fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    
    return SolverMetrics(
        solved=result.solved,
        time_ms=elapsed * 1000,
        nodes=getattr(result, 'nodes', None),
        depth=getattr(result, 'depth', None),
        steps=len(result.steps) if hasattr(result, 'steps') else 0,
        message=result.message if hasattr(result, 'message') else ""
    )


def assert_metrics_within_limits(
    metrics: SolverMetrics,
    max_time_ms: Optional[float] = None,
    max_nodes: Optional[int] = None,
    max_depth: Optional[int] = None,
    must_solve: bool = True
) -> None:
    """
    Assert that solver metrics are within acceptable limits.
    
    Args:
        metrics: SolverMetrics to validate
        max_time_ms: Maximum allowed time in milliseconds
        max_nodes: Maximum allowed node count (for search-based solvers)
        max_depth: Maximum allowed search depth
        must_solve: Whether the solver must find a solution
        
    Raises:
        AssertionError: If any limit is exceeded
    """
    if must_solve:
        assert metrics.solved, f"Expected solved=True, got {metrics.solved}. Message: {metrics.message}"
    
    if max_time_ms is not None:
        assert metrics.time_ms <= max_time_ms, \
            f"Time {metrics.time_ms:.2f}ms exceeds limit {max_time_ms}ms"
    
    if max_nodes is not None and metrics.nodes is not None:
        assert metrics.nodes <= max_nodes, \
            f"Nodes {metrics.nodes} exceeds limit {max_nodes}"
    
    if max_depth is not None and metrics.depth is not None:
        assert metrics.depth <= max_depth, \
            f"Depth {metrics.depth} exceeds limit {max_depth}"
