"""Contract tests for immutable givens behavior."""
# import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle

def raises_exception(func, exception_type):
    """Simple replacement for pytest.raises."""
    try:
        func()
        return False
    except exception_type:
        return True
    except Exception:
        return False

def test_givens_cannot_be_overwritten_via_grid():
    """Test that setting a cell value fails if cell is marked as given."""
    grid = Grid(2, 2)
    pos = Position(0, 0)
    
    # Mark cell as given
    cell = grid.get_cell(pos)
    cell.value = 5
    cell.given = True
    
    # Attempt to overwrite should fail
    assert raises_exception(lambda: grid.set_cell_value(pos, 10), ValueError)

def test_givens_cannot_be_cleared_via_grid():
    """Test that clearing a given cell fails."""
    grid = Grid(2, 2)
    pos = Position(0, 0)
    
    # Mark cell as given
    cell = grid.get_cell(pos)
    cell.value = 5
    cell.given = True
    
    # Attempt to clear should fail
    assert raises_exception(lambda: grid.clear_cell(pos), ValueError)

def test_blocked_cells_cannot_be_modified():
    """Test that blocked cells cannot be modified."""
    grid = Grid(2, 2)
    pos = Position(0, 0)
    
    # Mark cell as blocked
    cell = grid.get_cell(pos)
    cell.blocked = True
    
    # Attempt to set value should fail
    assert raises_exception(lambda: grid.set_cell_value(pos, 5), ValueError)
    
    # Attempt to clear should also fail
    assert raises_exception(lambda: grid.clear_cell(pos), ValueError)

def test_puzzle_clone_preserves_givens():
    """Test that puzzle cloning preserves given status."""
    grid = Grid(2, 2)
    constraints = Constraints(min_value=1, max_value=4)
    puzzle = Puzzle(grid, constraints)
    
    # Set up a given
    pos = Position(0, 0)
    cell = grid.get_cell(pos)
    cell.value = 1
    cell.given = True
    
    # Clone puzzle
    cloned = puzzle.clone()
    
    # Given should be preserved
    cloned_cell = cloned.grid.get_cell(pos)
    assert cloned_cell.value == 1
    assert cloned_cell.given == True

def test_puzzle_clone_with_replacements_respects_givens():
    """Test that puzzle cloning with replacements doesn't modify givens."""
    grid = Grid(2, 2)
    constraints = Constraints(min_value=1, max_value=4)
    puzzle = Puzzle(grid, constraints)
    
    # Set up a given
    given_pos = Position(0, 0)
    given_cell = grid.get_cell(given_pos)
    given_cell.value = 1
    given_cell.given = True
    
    # Clone with attempt to modify given
    replacements = {given_pos: 99}
    cloned = puzzle.clone(replacements)
    
    # Given should be unchanged
    cloned_cell = cloned.grid.get_cell(given_pos)
    assert cloned_cell.value == 1  # Original value preserved
    assert cloned_cell.given == True

def test_clear_non_givens_preserves_givens():
    """Test that clearing non-givens preserves all given values."""
    grid = Grid(2, 2)
    constraints = Constraints(min_value=1, max_value=4)
    puzzle = Puzzle(grid, constraints)
    
    # Set up a given and a non-given
    given_pos = Position(0, 0)
    given_cell = grid.get_cell(given_pos)
    given_cell.value = 1
    given_cell.given = True
    
    non_given_pos = Position(0, 1)
    non_given_cell = grid.get_cell(non_given_pos)
    non_given_cell.value = 2
    non_given_cell.given = False
    
    # Clear non-givens
    puzzle.clear_non_givens()
    
    # Given should be preserved, non-given should be cleared
    assert given_cell.value == 1
    assert given_cell.given == True
    assert non_given_cell.value is None
    assert non_given_cell.given == False

if __name__ == "__main__":
    test_givens_cannot_be_overwritten_via_grid()
    test_givens_cannot_be_cleared_via_grid() 
    test_blocked_cells_cannot_be_modified()
    test_puzzle_clone_preserves_givens()
    test_puzzle_clone_with_replacements_respects_givens()
    test_clear_non_givens_preserves_givens()
    print("All givens immutability contract tests passed.")