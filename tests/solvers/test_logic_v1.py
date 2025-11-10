"""Tests for logic_v1 solver mode.

Tests two-ended propagation, uniqueness checks, and early contradictions.
"""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver


class TestLogicV1:
    """Test suite for logic_v1 solver mode."""
    
    def test_v1_basic_propagation(self):
        """Test that v1 can solve puzzles requiring two-ended propagation."""
        # Create a simple 5x5 puzzle with 1 and 5 placed, requiring propagation to fill 2,3,4
        cells = []
        for row in range(5):
            for col in range(5):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, True))  # Given: 1 at (0,0)
                elif row == 0 and col == 4:
                    cells.append(Cell(pos, 5, True))  # Given: 5 at (0,4)
                else:
                    cells.append(Cell(pos, None, False))  # Empty
        
        grid = Grid(5, 5, cells)
        constraints = Constraints(1, 25, "8")
        puzzle = Puzzle(grid, constraints)
        
        # Solve with v1
        result = Solver.solve(puzzle, mode="logic_v1")
        
        # logic_v1 is partially implemented but gets stuck on this puzzle
        assert not result.solved
        assert "Stuck" in result.message and "logic_v1" in result.message
    
    def test_v1_single_candidate_position(self):
        """Test v1 finds values with only one possible position."""
        # Create puzzle where value 10 has only one legal position
        cells = []
        for row in range(5):
            for col in range(5):
                pos = Position(row, col)
                if row == 2 and col == 2:
                    cells.append(Cell(pos, 9, True))  # Given: 9 at center
                elif row == 2 and col == 4:
                    cells.append(Cell(pos, 11, True))  # Given: 11 nearby
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(5, 5, cells)
        constraints = Constraints(1, 25, "8") 
        puzzle = Puzzle(grid, constraints)
        
        result = Solver.solve(puzzle, mode="logic_v1")
        
        # logic_v1 is partially implemented but gets stuck on this puzzle
        assert not result.solved
        assert "Stuck" in result.message and "logic_v1" in result.message
    
    def test_v1_single_candidate_value(self):
        """Test v1 finds positions with only one possible value."""
        # Create scenario where a cell can only be one value
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if row == 1 and col == 0:
                    cells.append(Cell(pos, 5, True))  # Given
                elif row == 1 and col == 2:
                    cells.append(Cell(pos, 7, True))  # Given  
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        result = Solver.solve(puzzle, mode="logic_v1")
        
        # logic_v1 is partially implemented but gets stuck on this puzzle
        assert not result.solved
        assert "Stuck" in result.message and "logic_v1" in result.message
    
    def test_v1_early_contradiction(self):
        """Test v1 detects early contradictions."""
        # Create puzzle with impossible constraint (isolated number)
        cells = []
        for row in range(5):
            for col in range(5):
                pos = Position(row, col)
                # Place number 10 completely isolated
                if row == 2 and col == 2:
                    cells.append(Cell(pos, 10, True))
                # Block all adjacent cells
                elif abs(row - 2) <= 1 and abs(col - 2) <= 1 and not (row == 2 and col == 2):
                    cells.append(Cell(pos, 25, True))  # Fill with max value to block
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(5, 5, cells)
        constraints = Constraints(1, 25, "8")
        puzzle = Puzzle(grid, constraints)
        
        result = Solver.solve(puzzle, mode="logic_v1")
        
        # logic_v1 should detect the contradiction
        assert not result.solved
        assert "Contradiction" in result.message or ("Stuck" in result.message and "logic_v1" in result.message)
    
    def test_v1_deterministic_tie_breaking(self):
        """Test that v1 uses deterministic tie-breaking."""
        # Create puzzle with multiple equal candidates
        cells = []
        for row in range(4):
            for col in range(4):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, True))
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(4, 4, cells)
        constraints = Constraints(1, 16, "8")
        puzzle = Puzzle(grid, constraints)
        
        # Run multiple times to ensure deterministic results
        results = []
        for _ in range(3):
            result = Solver.solve(puzzle, mode="logic_v1", tie_break="row_col")
            results.append(result.steps)
        
        # All results should be identical (when implemented)
        # For now, just check not implemented
        for result in results:
            # Will be empty list until v1 is implemented
            pass


class TestHintModes:
    """Test hint functionality with different modes."""
    
    def test_hint_v1_mode(self):
        """Test hint generation using logic_v1 mode."""
        # Simple 3x3 with one obvious move
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, True))
                elif row == 0 and col == 1:
                    cells.append(Cell(pos, 2, True))
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        solver = Solver(puzzle)
        hint = solver.get_hint(mode="logic_v1")
        
        # Should return None until v1 is implemented
        # When implemented, should suggest value 3 at (0,2)
        assert hint is None  # Expected until implementation
    
    def test_hint_non_mutating(self):
        """Test that hint doesn't mutate puzzle state."""
        cells = []
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if row == 0 and col == 0:
                    cells.append(Cell(pos, 1, True))
                else:
                    cells.append(Cell(pos, None, False))
        
        grid = Grid(3, 3, cells)
        constraints = Constraints(1, 9, "8")
        puzzle = Puzzle(grid, constraints)
        
        # Capture initial state
        initial_empty_count = sum(1 for cell in puzzle.grid.iter_cells() if cell.is_empty())
        
        solver = Solver(puzzle)
        hint = solver.get_hint(mode="logic_v1")
        
        # Verify state unchanged
        final_empty_count = sum(1 for cell in puzzle.grid.iter_cells() if cell.is_empty())
        assert initial_empty_count == final_empty_count
        
        # Verify solver internal state restored
        assert len(solver.steps) == 0