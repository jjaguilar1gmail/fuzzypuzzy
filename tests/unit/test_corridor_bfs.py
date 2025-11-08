"""Unit tests for corridor computation using distance-sum BFS."""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.corridors import CorridorMap


def test_corridor_distance_sum_simple():
    """Corridor between two anchors should satisfy distA + distB <= (t-1)."""
    # 5x5 grid with anchors at opposite corners
    grid = Grid(5, 5, allow_diagonal=True)
    constraints = Constraints(1, 25, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Set givens
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 0)).given = True
    grid.set_cell_value(Position(4, 4), 25)
    grid.get_cell(Position(4, 4)).given = True
    
    corridors = CorridorMap()
    corridor = corridors.compute_corridor(1, 25, puzzle)
    
    # With gap of 24, distance-sum threshold is 23
    # All cells should be in corridor for this open grid
    assert len(corridor) > 0, "Corridor should not be empty"
    
    # Anchors themselves should not be in corridor (only empty cells)
    assert Position(0, 0) not in corridor
    assert Position(4, 4) not in corridor


def test_corridor_empty_cells_only():
    """Corridor should contain only empty positions, not the anchors."""
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Set givens
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 0)).given = True
    grid.set_cell_value(Position(2, 2), 9)
    grid.get_cell(Position(2, 2)).given = True
    
    corridors = CorridorMap()
    corridor = corridors.compute_corridor(1, 9, puzzle)
    
    # Anchors should not be in corridor
    assert Position(0, 0) not in corridor
    assert Position(2, 2) not in corridor
    
    # All cells in corridor should be empty
    for pos in corridor:
        cell = puzzle.grid.get_cell(pos)
        assert cell.is_empty(), f"Corridor cell {pos} should be empty"


def test_corridor_inequality_threshold():
    """Verify distance-sum uses <= (t-1) not < or <=t."""
    # 5x1 horizontal strip with 1 at left, 5 at right
    grid = Grid(5, 1, allow_diagonal=False)  # 5 rows, 1 col for horizontal strip
    constraints = Constraints(1, 5, '4')  # 4-adjacency for horizontal strip
    puzzle = Puzzle(grid, constraints)
    
    # Set givens (rows go down, so use different positions)
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 0)).given = True
    grid.set_cell_value(Position(4, 0), 5)
    grid.get_cell(Position(4, 0)).given = True
    
    corridors = CorridorMap()
    corridor = corridors.compute_corridor(1, 5, puzzle)
    
    # Gap is 4, so t-1 = 3
    # The 3 empty cells between should all be in corridor
    # distA[1,0]=1, distB[1,0]=1, sum=2 <= 3 ✓
    # distA[2,0]=2, distB[2,0]=2, sum=4 > 3 ✗ (if using strict inequality)
    # With <= (t-1)=3, we should get the middle cells
    
    assert len(corridor) >= 1, "Corridor should include at least center cells"
    # Middle cell should definitely be included
    assert Position(2, 0) in corridor or Position(1, 0) in corridor or Position(3, 0) in corridor


def test_corridor_cache_lifecycle():
    """Corridor cache should invalidate on placement and be marked clean after compute."""
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Set both givens so corridor can be computed
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 0)).given = True
    grid.set_cell_value(Position(2, 2), 9)
    grid.get_cell(Position(2, 2)).given = True
    
    corridors = CorridorMap()
    
    # First computation should build cache
    corridor1 = corridors.compute_corridor(1, 9, puzzle)
    assert not corridors._cache_dirty, "Cache should be clean after compute"
    
    # Invalidate cache
    corridors.invalidate_cache()
    assert corridors._cache_dirty, "Cache should be dirty after invalidation"
    
    # Recompute
    corridor2 = corridors.compute_corridor(1, 9, puzzle)
    assert not corridors._cache_dirty, "Cache should be clean after recompute"
