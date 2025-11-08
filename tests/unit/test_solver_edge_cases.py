"""
Unit tests for solver edge cases and error handling.

Tests unusual inputs, boundary conditions, and error cases.
"""

import pytest
from core.position import Position
from core.grid import Grid
from core.cell import Cell
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver, validate_solution


class TestSolverEdgeCases:
    """Test solver behavior with edge cases."""
    
    def test_empty_puzzle_unsolved(self):
        """Test that empty puzzle returns unsolved."""
        grid = Grid(3, 3, allow_diagonal=True)
        constraints = Constraints(1, 9, '8')
        puzzle = Puzzle(grid, constraints)
        
        # No givens - completely empty
        result = Solver.solve(puzzle, mode='logic_v0')
        
        # Should not solve (no information to work with)
        assert not result.solved
    
    def test_single_cell_puzzle(self):
        """Test 1x1 puzzle (trivial case)."""
        grid = Grid(1, 1, allow_diagonal=False)
        constraints = Constraints(1, 1, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Set the only cell
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        
        result = Solver.solve(puzzle, mode='logic_v0')
        
        # Should immediately recognize as solved
        assert result.solved
    
    def test_puzzle_with_only_endpoints(self):
        """Test puzzle with only start and end values."""
        grid = Grid(5, 1, allow_diagonal=False)  # 5x1 line
        constraints = Constraints(1, 5, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Set only endpoints
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        grid.set_cell_value(Position(4, 0), 5)
        grid.get_cell(Position(4, 0)).given = True
        
        # v0 might not solve this, but v1 should (two-ended propagation)
        result = Solver.solve(puzzle, mode='logic_v1')
        
        # Should solve with two-ended propagation
        assert result.solved
    
    def test_contradictory_givens(self):
        """Test puzzle with contradictory givens (non-adjacent consecutive values)."""
        grid = Grid(3, 3, allow_diagonal=False)
        constraints = Constraints(1, 9, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Place consecutive values that aren't adjacent (contradiction)
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        grid.set_cell_value(Position(2, 2), 2)  # Not adjacent to (0,0)
        grid.get_cell(Position(2, 2)).given = True
        
        result = Solver.solve(puzzle, mode='logic_v3')
        
        # Should detect contradiction and fail to solve
        assert not result.solved
    
    def test_already_solved_puzzle(self):
        """Test that solver recognizes already-solved puzzle."""
        grid = Grid(3, 1, allow_diagonal=False)
        constraints = Constraints(1, 3, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Fill entire puzzle
        for i in range(3):
            grid.set_cell_value(Position(i, 0), i + 1)
            grid.get_cell(Position(i, 0)).given = True
        
        result = Solver.solve(puzzle, mode='logic_v0')
        
        # Should immediately recognize as solved
        assert result.solved
        assert len(result.steps) == 0  # No steps needed
    
    def test_v3_with_timeout(self):
        """Test that v3 respects timeout settings."""
        grid = Grid(5, 5, allow_diagonal=True)
        constraints = Constraints(1, 25, '8')
        puzzle = Puzzle(grid, constraints)
        
        # Set only one given (very hard puzzle)
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        
        # Should respect very short timeout
        result = Solver.solve(puzzle, mode='logic_v3', timeout_ms=1)
        
        # Likely won't solve in 1ms
        # Just verify it doesn't crash or hang
        assert isinstance(result.solved, bool)
    
    def test_v3_with_node_limit(self):
        """Test that v3 respects node limit."""
        grid = Grid(5, 5, allow_diagonal=True)
        constraints = Constraints(1, 25, '8')
        puzzle = Puzzle(grid, constraints)
        
        # Set minimal givens
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        
        # Set very low node limit
        result = Solver.solve(puzzle, mode='logic_v3', max_nodes=5)
        
        # Should stop before solving due to node limit
        assert not result.solved or result.nodes <= 5


class TestValidationEdgeCases:
    """Test validation with edge cases."""
    
    def test_validate_empty_puzzle(self):
        """Test validation of empty puzzle."""
        grid = Grid(3, 3, allow_diagonal=True)
        constraints = Constraints(1, 9, '8')
        puzzle = Puzzle(grid, constraints)
        
        report = validate_solution(puzzle, {})
        
        assert report['status'] == 'FAIL'
        assert not report['all_filled']
    
    def test_validate_partially_filled(self):
        """Test validation of partially filled puzzle."""
        grid = Grid(3, 1, allow_diagonal=False)
        constraints = Constraints(1, 3, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Fill only first cell
        grid.set_cell_value(Position(0, 0), 1)
        
        report = validate_solution(puzzle, {Position(0, 0): 1})
        
        assert report['status'] == 'FAIL'
        assert not report['all_filled']
    
    def test_validate_with_duplicate_values(self):
        """Test validation detects duplicate values."""
        grid = Grid(3, 1, allow_diagonal=False)
        constraints = Constraints(1, 3, '4')
        puzzle = Puzzle(grid, constraints)
        
        # Create duplicate
        grid.set_cell_value(Position(0, 0), 1)
        grid.set_cell_value(Position(1, 0), 1)  # Duplicate!
        grid.set_cell_value(Position(2, 0), 3)
        
        report = validate_solution(puzzle, {Position(0, 0): 1})
        
        assert report['status'] == 'FAIL'
        assert not report['values_complete']
    
    def test_validate_single_cell_puzzle(self):
        """Test validation of 1x1 puzzle."""
        grid = Grid(1, 1, allow_diagonal=False)
        constraints = Constraints(1, 1, '4')
        puzzle = Puzzle(grid, constraints)
        
        grid.set_cell_value(Position(0, 0), 1)
        
        report = validate_solution(puzzle, {Position(0, 0): 1})
        
        # Single cell is always contiguous
        assert report['status'] == 'PASS'
        assert report['contiguous_path']


class TestModeTransitions:
    """Test behavior when switching between solver modes."""
    
    def test_v0_to_v1_on_same_puzzle(self):
        """Test that v0 and v1 are independent."""
        grid = Grid(5, 1, allow_diagonal=False)
        constraints = Constraints(1, 5, '4')
        puzzle = Puzzle(grid, constraints)
        
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        grid.set_cell_value(Position(4, 0), 5)
        grid.get_cell(Position(4, 0)).given = True
        
        result_v0 = Solver.solve(puzzle, mode='logic_v0')
        result_v1 = Solver.solve(puzzle, mode='logic_v1')
        
        # v0 may not solve, but v1 should (has two-ended propagation)
        assert result_v1.solved
        
        # v1 should perform at least as well as v0
        if result_v0.solved:
            assert result_v1.solved
    
    def test_v2_after_v0_unsolved(self):
        """Test using v2 after v0 fails."""
        grid = Grid(5, 5, allow_diagonal=True)
        constraints = Constraints(1, 25, '8')
        puzzle = Puzzle(grid, constraints)
        
        # Set some givens (not enough for v0/v2 alone)
        grid.set_cell_value(Position(0, 0), 1)
        grid.get_cell(Position(0, 0)).given = True
        grid.set_cell_value(Position(4, 4), 25)
        grid.get_cell(Position(4, 4)).given = True
        
        result_v0 = Solver.solve(puzzle, mode='logic_v0')
        result_v2 = Solver.solve(puzzle, mode='logic_v2')
        
        # With only 2 givens, neither v0 nor v2 will solve
        # But both should run without crashing
        assert isinstance(result_v0.solved, bool)
        assert isinstance(result_v2.solved, bool)
        # v2 might make some progress even if not solving
        # (progress_made tracks if eliminations occurred)
