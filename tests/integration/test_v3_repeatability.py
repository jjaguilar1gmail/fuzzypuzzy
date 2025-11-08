"""Repeatability test for logic_v3 - ensures deterministic behavior across runs."""
import json
from pathlib import Path
from core.position import Position
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver


def test_v3_repeatability_5_runs():
    """Test that v3 produces identical results across 5 runs.
    
    Requirements from spec:
    - FR-004: v3 must be deterministic (same solution, metrics, trace across runs)
    - All tie-breaking must use deterministic ordering (row,col; value asc)
    """
    # Load canonical 5x5 fixture
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    results = []
    
    for run in range(5):
        # Build fresh puzzle for each run
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
        
        # Run v3
        result = Solver.solve(puzzle, mode='logic_v3')
        
        # Extract solution (if solved)
        solution = None
        if result.solved:
            solution = {}
            for cell in puzzle.grid.iter_cells():
                solution[(cell.pos.row, cell.pos.col)] = cell.value
        
        results.append({
            'run': run + 1,
            'solved': result.solved,
            'nodes': result.nodes if hasattr(result, 'nodes') else None,
            'depth': result.depth if hasattr(result, 'depth') else None,
            'steps': len(result.steps),
            'message': result.message,
            'solution': solution
        })
    
    # Compare all runs to first run
    first = results[0]
    
    for i, result in enumerate(results[1:], start=2):
        # Check solved status
        assert result['solved'] == first['solved'], \
            f"Run {i} solved={result['solved']}, but run 1 solved={first['solved']}"
        
        # Check node count (should be identical for deterministic search)
        assert result['nodes'] == first['nodes'], \
            f"Run {i} nodes={result['nodes']}, but run 1 nodes={first['nodes']}"
        
        # Check depth
        assert result['depth'] == first['depth'], \
            f"Run {i} depth={result['depth']}, but run 1 depth={first['depth']}"
        
        # Check step count
        assert result['steps'] == first['steps'], \
            f"Run {i} steps={result['steps']}, but run 1 steps={first['steps']}"
        
        # Check solution (if solved)
        if first['solved']:
            assert result['solution'] == first['solution'], \
                f"Run {i} produced different solution than run 1"
    
    print(f"\n✓ v3 repeatability verified across 5 runs:")
    print(f"  Solved: {first['solved']}")
    print(f"  Nodes: {first['nodes']}")
    print(f"  Depth: {first['depth']}")
    print(f"  Steps: {first['steps']}")
    print(f"  All runs identical: ✓")


def test_v3_solution_uniqueness():
    """Test that v3 always finds the same solution (deterministic ordering)."""
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    solutions = []
    
    for run in range(3):
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
        
        result = Solver.solve(puzzle, mode='logic_v3')
        
        if result.solved:
            # Build solution string (ordered by position for comparison)
            solution_str = []
            for row in range(data['rows']):
                for col in range(data['cols']):
                    pos = Position(row, col)
                    cell = puzzle.grid.get_cell(pos)
                    solution_str.append(str(cell.value))
            solutions.append(''.join(solution_str))
    
    # All solutions should be identical
    assert len(set(solutions)) == 1, \
        f"v3 produced {len(set(solutions))} different solutions across runs"
    
    print(f"\n✓ v3 solution uniqueness verified:")
    print(f"  All 3 runs produced identical solution")
    print(f"  Solution string: {solutions[0][:20]}...")


def test_v3_trace_determinism():
    """Test that v3 produces identical trace sequences across runs."""
    fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
    with open(fixture_path, 'r') as f:
        data = json.load(f)
    
    traces = []
    
    for run in range(3):
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
        
        result = Solver.solve(puzzle, mode='logic_v3')
        
        # Extract trace (reason strings for each step)
        trace = [step.reason for step in result.steps]
        traces.append(trace)
    
    # All traces should be identical
    first_trace = traces[0]
    for i, trace in enumerate(traces[1:], start=2):
        assert len(trace) == len(first_trace), \
            f"Run {i} has {len(trace)} steps, but run 1 has {len(first_trace)} steps"
        
        for j, (step1, step2) in enumerate(zip(first_trace, trace)):
            assert step1 == step2, \
                f"Run {i} step {j} differs: '{step2}' vs run 1: '{step1}'"
    
    print(f"\n✓ v3 trace determinism verified:")
    print(f"  All 3 runs produced identical {len(first_trace)}-step trace")
    if first_trace:
        print(f"  First step: {first_trace[0]}")
        print(f"  Last step: {first_trace[-1]}")
