"""Unit tests for minimal region capacity checks."""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.regions import RegionCache


def test_region_capacity_basic():
    """Region capacity should count empty cells in connected components."""
    # 3x3 with middle row filled (splits top and bottom regions)
    grid = Grid(3, 3, allow_diagonal=True)
    constraints = Constraints(1, 9, '8')
    puzzle = Puzzle(grid, constraints)
    
    # Fill middle row to split into regions
    for col in range(3):
        grid.set_cell_value(Position(1, col), 99)
    
    regions = RegionCache()
    regions.build_regions(puzzle)
    
    # Should have 2 separate regions (top and bottom)
    assert len(regions.regions) >= 2, "Should have at least 2 disconnected regions"
    
    # Each region should have 3 cells
    region_sizes = [len(r.cells) for r in regions.regions]
    assert 3 in region_sizes, "Should have region with 3 empty cells"


def test_region_intersecting_corridor():
    """Region capacity for a gap should check regions intersecting the corridor."""
    # Simple 5x5 grid all empty
    grid = Grid(5, 5, allow_diagonal=True)
    constraints = Constraints(1, 25, '8')
    puzzle = Puzzle(grid, constraints)
    
    regions = RegionCache()
    regions.build_regions(puzzle)
    
    # All empty, so should be 1 large region
    assert len(regions.regions) == 1, "All-empty grid should be one region"
    assert len(regions.regions[0].cells) == 25, "Region should have all 25 cells"


def test_region_insufficient_capacity():
    """If a region has fewer empties than (t-1), gap cannot fit."""
    # 5x1 strip with middle 3 empty, but we need gap of 5
    grid = Grid(5, 1, allow_diagonal=False)  # 5 rows, 1 col
    constraints = Constraints(1, 25, '4')
    puzzle = Puzzle(grid, constraints)
    
    # Fill first and last cells
    grid.set_cell_value(Position(0, 0), 1)
    grid.get_cell(Position(0, 0)).given = True
    grid.set_cell_value(Position(4, 0), 21)
    grid.get_cell(Position(4, 0)).given = True
    
    regions = RegionCache()
    regions.build_regions(puzzle)
    
    # Should have 1 region with 3 empty cells
    assert len(regions.regions) == 1
    assert len(regions.regions[0].cells) == 3
    
    # If we need gap of 20 (from 1 to 21, t-1=19), this region is insufficient (only 3 empties)
    # This is the kind of check that should eliminate candidates
