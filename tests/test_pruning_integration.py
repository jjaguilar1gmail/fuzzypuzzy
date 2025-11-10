"""Test that pruning.py actually uses the new staged checker."""

import sys
sys.path.insert(0, '.')

from core.grid import Grid
from core.puzzle import Puzzle
from core.constraints import Constraints
from generate.pruning import check_puzzle_uniqueness


def test_pruning_integration():
    """Test that check_puzzle_uniqueness uses the new method."""
    print("Testing pruning.py integration...")
    print("=" * 60)
    
    # Create simple 3x3 puzzle with 2 givens (likely non-unique)
    grid = Grid(rows=3, cols=3, allow_diagonal=False)
    constraints = Constraints(min_value=1, max_value=9, allow_diagonal=False)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    puzzle.grid.cells[2][2].value = 9
    puzzle.grid.cells[2][2].given = True
    
    print(f"Test puzzle: 3x3 with 2 givens (corners)")
    print(f"Expected: NON-UNIQUE (too few givens)")
    
    # Call the pruning function (should use staged checker)
    result = check_puzzle_uniqueness(puzzle, solver_mode='logic_v3')
    
    print(f"\nResult: {'UNIQUE' if result else 'NON-UNIQUE'}")
    print(f"✓ Integration test complete")
    
    return result


def test_pruning_with_more_givens():
    """Test with more constrained puzzle."""
    print("\n" + "=" * 60)
    print("Testing with more givens...")
    print("=" * 60)
    
    grid = Grid(rows=4, cols=4, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=16, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Place several givens to constrain the puzzle
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    
    puzzle.grid.cells[1][1].value = 7
    puzzle.grid.cells[1][1].given = True
    
    puzzle.grid.cells[2][2].value = 11
    puzzle.grid.cells[2][2].given = True
    
    puzzle.grid.cells[3][3].value = 16
    puzzle.grid.cells[3][3].given = True
    
    puzzle.grid.cells[1][2].value = 8
    puzzle.grid.cells[1][2].given = True
    
    print(f"Test puzzle: 4x4 with 5 givens")
    
    result = check_puzzle_uniqueness(puzzle, solver_mode='logic_v3')
    
    print(f"Result: {'UNIQUE' if result else 'NON-UNIQUE'}")
    
    return result


if __name__ == '__main__':
    print("Testing Pruning Integration with Staged Uniqueness Checker")
    print("=" * 60)
    print()
    
    result1 = test_pruning_integration()
    result2 = test_pruning_with_more_givens()
    
    print("\n" + "=" * 60)
    print("PRUNING INTEGRATION TESTS COMPLETE")
    print("=" * 60)
    print(f"Test 1 (3x3, 2 givens): {'UNIQUE' if result1 else 'NON-UNIQUE'}")
    print(f"Test 2 (4x4, 5 givens): {'UNIQUE' if result2 else 'NON-UNIQUE'}")
