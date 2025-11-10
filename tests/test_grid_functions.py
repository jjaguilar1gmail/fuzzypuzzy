## This is a set of tests for the functions of the Grid class.
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.adjacency import Adjacency
def test_grid_initialization():
    grid = Grid(3, 3, allow_diagonal=False)
    assert grid.rows == 3
    assert grid.cols == 3
    assert len(grid.cells) == 3
    assert len(grid.cells[0]) == 3
    for r in range(3):
        for c in range(3):
            cell = grid.get_cell(Position(r, c))
            assert isinstance(cell, Cell)
            assert cell.pos.row == r
            assert cell.pos.col == c
            assert cell.value is None
            assert not cell.blocked
            assert not cell.given
def test_set_and_get_cell_value():
    grid = Grid(2, 2)
    pos = Position(0, 0)
    grid.set_cell_value(pos, 5)
    cell = grid.get_cell(pos)
    assert cell.value == 5
    grid.clear_cell(pos)
    assert cell.value is None
def test_iter_cells():
    grid = Grid(2, 2)
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for cell, (r, c) in zip(grid.iter_cells(), positions):
        assert cell.pos.row == r
        assert cell.pos.col == c
def test_empty_and_filled_positions():
    grid = Grid(2, 2)
    grid.set_cell_value(Position(0, 0), 1)
    grid.set_cell_value(Position(1, 1), 2)
    empty_positions = list(grid.empty_positions())
    filled_positions = list(grid.filled_positions())
    assert len(empty_positions) == 2
    assert Position(0, 1) in empty_positions
    assert Position(1, 0) in empty_positions
    assert len(filled_positions) == 2
    assert Position(0, 0) in filled_positions
    assert Position(1, 1) in filled_positions


def test_print_grid(capsys):
    """Test grid printing via ascii_print (updated for deprecated print_grid)."""
    from hidato_io.exporters import ascii_print
    from core.puzzle import Puzzle
    from core.constraints import Constraints
    
    grid = Grid(2, 2)
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 1)).blocked = True
    grid.set_cell_value(Position(1, 1), 2)
    
    # Create puzzle for ascii_print
    constraints = Constraints(1, 4, allow_diagonal=True)
    puzzle = Puzzle(grid, constraints)
    
    ascii_print(puzzle)
    captured = capsys.readouterr()
    
    # Check that output contains expected elements
    assert "1" in captured.out
    assert "X" in captured.out or "■" in captured.out  # Blocked cell representation
    assert "2" in captured.out


def test_pretty_print_grid(capsys):
    """Test grid pretty printing via ascii_print (updated for deprecated print_grid)."""
    from hidato_io.exporters import ascii_print
    from core.puzzle import Puzzle
    from core.constraints import Constraints
    
    grid = Grid(3, 3)
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(1, 1)).blocked = True
    grid.set_cell_value(Position(2, 2), 2)
    
    # Create puzzle for ascii_print
    constraints = Constraints(1, 9, allow_diagonal=True)
    puzzle = Puzzle(grid, constraints)
    
    ascii_print(puzzle)
    captured = capsys.readouterr()
    
    # Check that output contains expected elements
    assert "1" in captured.out
    assert "X" in captured.out or "■" in captured.out  # Blocked cell representation
    assert "2" in captured.out

if __name__ == "__main__":
    test_grid_initialization()
    test_set_and_get_cell_value()
    test_iter_cells()
    test_empty_and_filled_positions()
    test_print_grid()
    test_pretty_print_grid()
    print("All tests passed.")