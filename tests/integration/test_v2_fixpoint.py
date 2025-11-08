"""Integration test for logic_v2 fixpoint behavior on canonical 5x5."""
import json
from pathlib import Path
from core.position import Position
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver
from tests.util.perf_utils import measure_solve, assert_metrics_within_limits, SolverMetrics


def test_v2_fixpoint_canonical_5x5():
    """Test that logic_v2 reaches fixpoint with at least one elimination on canonical 5x5.
    
    Requirements from spec:
    - FR-002: v2 MUST perform at least one elimination via corridor or degree pruning
    - NFR-001: v2 fixpoint completes in ≤250 ms
    - Should reach fixpoint status ("no more logical moves") whether solved or not
    """
    # Load canonical 5x5 fixture
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    # Build puzzle from fixture
    grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
    constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
    puzzle = Puzzle(grid, constraints)
    
    # Set givens
    for given in data['givens']:
        pos = Position(given['row'], given['col'])
        grid.set_cell_value(pos, given['value'])
        grid.get_cell(pos).given = True
    
    # Run logic_v2 and measure performance
    result = Solver.solve(puzzle, mode='logic_v2')
    metrics = measure_solve(Solver.solve, puzzle, mode='logic_v2')
    
    # Assert performance requirements
    assert_metrics_within_limits(
        metrics,
        max_time_ms=250,
        must_solve=False,  # v2 may not solve, just reach fixpoint
    )
    
    # Assert at least one elimination occurred (FR-002)
    # Check for corridor or degree elimination in steps
    elimination_steps = [
        step for step in result.steps 
        if 'corridor' in step.reason.lower() or 'degree' in step.reason.lower()
    ]
    
    assert len(elimination_steps) > 0, \
        f"FR-002 violation: v2 must perform at least one corridor/degree elimination. " \
        f"Found {len(elimination_steps)} elimination step(s)"
    
    # Assert proper fixpoint status message
    if not metrics.solved:
        assert "no more logical moves" in metrics.message.lower(), \
            f"Expected 'no more logical moves' status, got: {metrics.message}"
    
    # Print summary for visibility
    print(f"\n✓ v2 fixpoint test passed:")
    print(f"  Solved: {metrics.solved}")
    print(f"  Time: {metrics.time_ms:.1f} ms")
    print(f"  Steps: {metrics.steps_count}")
    print(f"  Eliminations: {len(elimination_steps)}")
    print(f"  Message: {metrics.message}")


def test_v2_fixpoint_traces_eliminations():
    """Test that v2 properly traces corridor, degree, and region eliminations."""
    # Load canonical 5x5
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
    constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
    puzzle = Puzzle(grid, constraints)
    
    for given in data['givens']:
        pos = Position(given['row'], given['col'])
        grid.set_cell_value(pos, given['value'])
        grid.get_cell(pos).given = True
    
    # Run v2
    result = Solver.solve(puzzle, mode='logic_v2')
    
    # Count elimination types
    corridor_eliminations = sum(1 for step in result.steps if 'corridor' in step.reason.lower())
    degree_eliminations = sum(1 for step in result.steps if 'degree' in step.reason.lower())
    region_eliminations = sum(1 for step in result.steps if 'region' in step.reason.lower())
    
    total_eliminations = corridor_eliminations + degree_eliminations + region_eliminations
    
    # At least one elimination should occur
    assert total_eliminations > 0, \
        f"Expected at least one pruning elimination, found none. Steps: {len(result.steps)}"
    
    print(f"\n✓ v2 elimination tracing:")
    print(f"  Corridor: {corridor_eliminations}")
    print(f"  Degree: {degree_eliminations}")
    print(f"  Region: {region_eliminations}")
    print(f"  Total: {total_eliminations}")


def test_v2_deterministic_across_runs():
    """Test that v2 produces consistent results across multiple runs."""
    # Load canonical 5x5
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    results = []
    for run in range(3):
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
        
        result = Solver.solve(puzzle, mode='logic_v2')
        results.append({
            'solved': result.solved,
            'steps': len(result.steps),
            'message': result.message
        })
    
    # All runs should produce identical results
    first = results[0]
    for i, result in enumerate(results[1:], start=2):
        assert result['solved'] == first['solved'], \
            f"Run {i} solved={result['solved']}, but run 1 solved={first['solved']}"
        assert result['steps'] == first['steps'], \
            f"Run {i} had {result['steps']} steps, but run 1 had {first['steps']} steps"
        assert result['message'] == first['message'], \
            f"Run {i} message differs from run 1"
    
    print(f"\n✓ v2 determinism verified across 3 runs:")
    print(f"  Solved: {first['solved']}")
    print(f"  Steps: {first['steps']}")
    print(f"  Message: {first['message']}")
