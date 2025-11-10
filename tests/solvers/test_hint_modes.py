"""Tests for hint mode routing and functionality."""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver


class TestHintModes:
    """Test hint functionality across different solver modes."""
    
    def test_hint_mode_routing_v0(self):
        """Test hint routing to logic_v0."""
        # Create a 1x3 line puzzle with 1 and 3 at ends - forces 2 in middle
        cells = []
        for row in range(1):
            for col in range(3):
                pos = Position(row, col)
                if col == 0:
                    cells.append(Cell(pos, 1, False, True))  # value=1 at (0,0)
                elif col == 2:
                    cells.append(Cell(pos, 3, False, True))  # value=3 at (0,2)
                else:
                    cells.append(Cell(pos, None, False, False))
        
        grid = Grid(1, 3, cells, allow_diagonal=False)  # 4-neighbor only for line
        constraints = Constraints(1, 3, "4")  # 4-neighbor constraint
        puzzle = Puzzle(grid, constraints)
        
        solver = Solver(puzzle)
        hint = solver.get_hint(mode="logic_v0")
        
        # Should find hint for value 2 at position (0,1) - only cell between 1 and 3
        assert hint is not None
        assert hint.value == 2
        assert hint.position == Position(0, 1)
    
    def test_hint_mode_routing_v1(self):
        """Test hint routing to logic_v1 (placeholder)."""
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, False, True))
                else:
                    cells.append(Cell(pos, None, False, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        solver = Solver(puzzle)
        hint = solver.get_hint(mode="logic_v1")
        
        # Returns None until v1 is implemented
        assert hint is None
    
    def test_hint_invalid_mode(self):
        """Test hint with invalid mode raises error."""
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                cells.append(Cell(pos, None, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        solver = Solver(puzzle)
        
        with pytest.raises(ValueError, match="Unsupported hint mode"):
            solver.get_hint(mode="invalid_mode")
    
    def test_hint_state_restoration(self):
        """Test hint preserves solver state."""
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, False, True))
                else:
                    cells.append(Cell(pos, None, False, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        solver = Solver(puzzle)
        
        # Capture initial state
        initial_steps = len(solver.steps)
        initial_empty = sum(1 for cell in solver.puzzle.grid.iter_cells() if cell.is_empty())
        
        # Get hint
        hint = solver.get_hint(mode="logic_v0")
        
        # Verify state restored  
        assert len(solver.steps) == initial_steps
        final_empty = sum(1 for cell in solver.puzzle.grid.iter_cells() if cell.is_empty())
        assert final_empty == initial_empty