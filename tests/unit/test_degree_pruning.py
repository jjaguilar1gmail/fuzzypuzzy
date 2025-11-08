"""Unit tests for degree pruning logic."""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.degree import DegreeIndex


def test_degree_empty_neighbors_only():
    """Degree should count only empty neighbors, not all neighbors."""
    # Create 3x3 grid with some filled cells
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Fill center and corner
    puzzle.grid.set_cell_value(Position(0, 0), 5)
    puzzle.grid.set_cell_value(Position(1, 1), 5)
    
    degrees = DegreeIndex()
    degrees.build_degree_index(puzzle)
    
    # Position (0, 1) has 5 neighbors in 8-adjacency: (0,0), (0,2), (1,0), (1,1), (1,2)
    # But (0, 0) is filled and (1, 1) is filled, so only 3 empty neighbors
    pos = Position(0, 1)
    degree = degrees.get_degree(pos)
    
    # Should count only empty neighbors
    assert degree == 3, f"Expected 3 empty neighbors, got {degree}"


def test_degree_endpoint_threshold():
    """Endpoint values (1 or N) need at least 1 empty neighbor."""
    # 3x3 with corner isolated (all neighbors filled)
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Fill all cells except corner
    for row in range(3):
        for col in range(3):
            pos = Position(row, col)
            if row == 0 and col == 0:
                # Leave corner empty
                pass
            else:
                # Fill all other cells
                puzzle.grid.set_cell_value(pos, row * 3 + col + 2)
    
    degrees = DegreeIndex()
    degrees.build_degree_index(puzzle)
    
    corner = Position(0, 0)
    degree = degrees.get_degree(corner)
    
    # Corner has 3 neighbors in 8-adjacency, but all are filled
    assert degree == 0, "Isolated cell should have degree 0"


def test_degree_middle_threshold():
    """Middle values need at least 2 empty neighbors to form a path."""
    # 3x3 with center having only 1 empty neighbor
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Fill all except center and one neighbor
    for row in range(3):
        for col in range(3):
            pos = Position(row, col)
            if row == 1 and col == 1:
                # Center empty
                pass
            elif row == 0 and col == 1:
                # One empty neighbor
                pass
            else:
                # Others filled
                puzzle.grid.set_cell_value(pos, 99)

    degrees = DegreeIndex()
    degrees.build_degree_index(puzzle)
    
    center = Position(1, 1)
    degree = degrees.get_degree(center)
    
    # Center has 8 neighbors, but only 1 is empty
    assert degree == 1, "Center should have degree 1 (only one empty neighbor)"
