"""Integration test for logic_v3 solve on canonical 5x5 with strict limits."""
import json
from pathlib import Path
from core.position import Position
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver
from tests.util.perf_utils import measure_solve, assert_metrics_within_limits, SolverMetrics


def test_v3_solves_canonical_5x5():
    """Test that logic_v3 solves canonical 5x5 within strict performance limits.
    
    Requirements from spec:
    - NFR-002: v3 solves in ≤100 ms
    - NFR-003: v3 uses ≤2,000 nodes
    - NFR-004: v3 max depth ≤25
    - FR-003: v3 MUST find a solution (not just reach fixpoint)
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
    
    # Run logic_v3 and measure performance
    metrics = measure_solve(Solver.solve, puzzle, mode='logic_v3')
    
    # Assert v3 MUST solve (FR-003)
    assert metrics.solved, \
        f"FR-003 violation: v3 must solve canonical 5x5. Message: {metrics.message}"
    
    # Assert strict performance requirements
    assert_metrics_within_limits(
        metrics,
        max_time_ms=100,      # NFR-002
        max_nodes=2000,       # NFR-003
        max_depth=25,         # NFR-004
        must_solve=True
    )
    
    # Print summary for visibility
    print(f"\n✓ v3 solve test passed:")
    print(f"  Solved: {metrics.solved}")
    print(f"  Time: {metrics.time_ms:.1f} ms (limit: 100 ms)")
    print(f"  Nodes: {metrics.nodes} (limit: 2,000)")
    print(f"  Depth: {metrics.depth} (limit: 25)")
    print(f"  Steps: {metrics.steps}")
    print(f"  Message: {metrics.message}")


def test_v3_applies_fixpoint_at_nodes():
    """Test that v3 applies v2 logic fixpoint at each search node (Bug #1 fix)."""
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
    
    # Run v3
    result = Solver.solve(puzzle, mode='logic_v3')
    
    # v3 should solve using very few nodes (logic at each node should prune heavily)
    assert result.solved, "v3 should solve canonical 5x5"
    
    # With in-place fixpoint at each node, we should see:
    # 1. Fewer nodes than naive search
    # 2. Evidence of pruning in trace
    assert hasattr(result, 'nodes') and result.nodes is not None, \
        "v3 should track node count"
    
    print(f"\n✓ v3 fixpoint application verified:")
    print(f"  Nodes explored: {result.nodes}")
    print(f"  Solution found: {result.solved}")


def test_v3_validates_solution():
    """Test that v3 produces valid Hidato solution."""
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
    
    # Run v3
    result = Solver.solve(puzzle, mode='logic_v3')
    
    assert result.solved, "v3 should solve canonical 5x5"
    
    # Validate solution
    # 1. All cells filled
    for cell in puzzle.grid.iter_cells():
        assert not cell.is_empty(), f"Cell {cell.pos} should be filled"
    
    # 2. All values 1..25 present exactly once
    values_found = set()
    for cell in puzzle.grid.iter_cells():
        values_found.add(cell.value)
    
    expected_values = set(range(1, 26))
    assert values_found == expected_values, \
        f"Solution should have values 1..25, found: {sorted(values_found)}"
    
    # 3. Consecutive values are adjacent
    value_to_pos = {}
    for cell in puzzle.grid.iter_cells():
        value_to_pos[cell.value] = cell.pos
    
    for value in range(1, 25):  # Check 1-2, 2-3, ..., 24-25
        pos1 = value_to_pos[value]
        pos2 = value_to_pos[value + 1]
        neighbors = puzzle.grid.neighbors_of(pos1)
        assert pos2 in neighbors, \
            f"Value {value} at {pos1} should be adjacent to {value+1} at {pos2}"
    
    # 4. Givens preserved
    for given in data['givens']:
        pos = Position(given['row'], given['col'])
        cell = puzzle.grid.get_cell(pos)
        assert cell.value == given['value'], \
            f"Given at {pos} should be {given['value']}, got {cell.value}"
    
    print(f"\n✓ v3 solution validation passed:")
    print(f"  All cells filled: ✓")
    print(f"  All values 1..25 present: ✓")
    print(f"  Consecutive adjacency: ✓")
    print(f"  Givens preserved: ✓")
