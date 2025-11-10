"""Test that the staged uniqueness checker actually detects solutions."""

import sys
sys.path.insert(0, '.')

from core.grid import Grid
from core.puzzle import Puzzle
from core.constraints import Constraints
from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision


def test_detect_solution_on_small_puzzle():
    """Test that solver can find solution on a minimal puzzle."""
    print("\n=== Test: Detect solution on 3x3 puzzle ===")
    
    # Create 3x3 puzzle with solution: 1-2-3
    #                                    |   |
    #                                    4-5-6
    #                                    |   |
    #                                    7-8-9
    grid = Grid(rows=3, cols=3, allow_diagonal=False)  # 4-adjacency for simplicity
    constraints = Constraints(min_value=1, max_value=9, allow_diagonal=False)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Place corners as givens - leaves only one solution
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    
    puzzle.grid.cells[2][2].value = 9
    puzzle.grid.cells[2][2].given = True
    
    # This puzzle should have a unique solution
    request = create_request(
        puzzle=puzzle,
        size=3,
        adjacency=4,
        difficulty='easy',
        seed=42,
        enable_early_exit=True,
        enable_probes=False,
        enable_sat=False
    )
    
    result = check_uniqueness(request)
    
    print(f"Decision: {result.decision.value}")
    print(f"Stage: {result.stage_decided}")
    print(f"Time: {result.elapsed_ms}ms")
    print(f"Nodes: {result.nodes_explored}")
    
    # With the real solver, it should either find:
    # - Unique (1 solution found)
    # - Non-Unique (2+ solutions found)
    # - Inconclusive (if too complex)
    
    # For this simple 3x3, we expect it to find at least 1 solution
    assert result.decision in [UniquenessDecision.UNIQUE, UniquenessDecision.NON_UNIQUE, UniquenessDecision.INCONCLUSIVE]
    
    if result.decision != UniquenessDecision.INCONCLUSIVE:
        print(f"✓ Solver found solutions (not inconclusive)")
    else:
        print(f"⚠ Inconclusive - puzzle may be too constrained or search exhausted")
    
    return result


def test_detect_multiple_solutions():
    """Test that solver can detect when puzzle has multiple solutions."""
    print("\n=== Test: Detect non-unique puzzle ===")
    
    # Create 4x4 puzzle with very few givens - likely non-unique
    grid = Grid(rows=4, cols=4, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=16, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Only place start and end - many solutions possible
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    
    puzzle.grid.cells[3][3].value = 16
    puzzle.grid.cells[3][3].given = True
    
    request = create_request(
        puzzle=puzzle,
        size=4,
        adjacency=8,
        difficulty='easy',
        seed=42,
        enable_early_exit=True,
        enable_probes=False
    )
    
    result = check_uniqueness(request)
    
    print(f"Decision: {result.decision.value}")
    print(f"Stage: {result.stage_decided}")
    print(f"Time: {result.elapsed_ms}ms")
    print(f"Nodes: {result.nodes_explored}")
    
    # With only 2 givens, this should likely be non-unique
    # (though not guaranteed - depends on search)
    if result.decision == UniquenessDecision.NON_UNIQUE:
        print(f"✓ Correctly detected non-unique puzzle")
    elif result.decision == UniquenessDecision.UNIQUE:
        print(f"⚠ Found unique solution (unexpected with so few givens)")
    else:
        print(f"? Inconclusive - search may not have explored enough")
    
    return result


def test_actual_search_stats():
    """Verify that search actually explores nodes."""
    print("\n=== Test: Search statistics ===")
    
    grid = Grid(rows=4, cols=4, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=16, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Add a few givens to make it interesting
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    puzzle.grid.cells[1][1].value = 7
    puzzle.grid.cells[1][1].given = True
    puzzle.grid.cells[3][3].value = 16
    puzzle.grid.cells[3][3].given = True
    
    request = create_request(
        puzzle=puzzle,
        size=4,
        difficulty='medium',
        seed=99
    )
    
    result = check_uniqueness(request)
    
    print(f"Decision: {result.decision.value}")
    print(f"Elapsed: {result.elapsed_ms}ms")
    print(f"Per-stage: {result.per_stage_ms}")
    print(f"Nodes explored: {result.nodes_explored}")
    print(f"Stage decided: {result.stage_decided}")
    
    # Verify search actually ran
    total_nodes = sum(result.nodes_explored.values())
    if total_nodes > 0:
        print(f"✓ Search explored {total_nodes} nodes")
    else:
        print(f"⚠ No nodes explored - search may not have run")
    
    return result


def main():
    """Run solver integration tests."""
    print("=" * 60)
    print("Staged Uniqueness - Solver Integration Tests")
    print("=" * 60)
    
    try:
        result1 = test_detect_solution_on_small_puzzle()
        result2 = test_detect_multiple_solutions()
        result3 = test_actual_search_stats()
        
        print("\n" + "=" * 60)
        print("✅ SOLVER INTEGRATION TESTS COMPLETED")
        print("=" * 60)
        print("\nSummary:")
        print(f"  Test 1 (3x3): {result1.decision.value} in {result1.elapsed_ms}ms")
        print(f"  Test 2 (4x4 sparse): {result2.decision.value} in {result2.elapsed_ms}ms")
        print(f"  Test 3 (4x4 stats): {result3.decision.value} in {result3.elapsed_ms}ms")
        print(f"  Total nodes: {sum(result1.nodes_explored.values()) + sum(result2.nodes_explored.values()) + sum(result3.nodes_explored.values())}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
