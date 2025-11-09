"""Test backbite_v1 determinism (T019)."""
import pytest
from core.grid import Grid
from generate.path_builder import PathBuilder
from util.rng import RNG


class TestBackbiteDeterminism:
    """Test backbite_v1 produces deterministic results."""
    
    def test_same_seed_same_path(self):
        """Same seed produces identical path."""
        seed = 42
        
        # Run 1
        rng1 = RNG(seed)
        grid1 = Grid(7, 7, allow_diagonal=True)
        path1 = PathBuilder._build_backbite_v1(grid1, rng1, blocked=None, max_time_ms=3000)
        
        # Run 2
        rng2 = RNG(seed)
        grid2 = Grid(7, 7, allow_diagonal=True)
        path2 = PathBuilder._build_backbite_v1(grid2, rng2, blocked=None, max_time_ms=3000)
        
        # Paths should be identical
        assert len(path1) == len(path2)
        for i, (p1, p2) in enumerate(zip(path1, path2)):
            assert p1.row == p2.row, f"Position {i}: row mismatch"
            assert p1.col == p2.col, f"Position {i}: col mismatch"
    
    def test_different_seeds_different_paths(self):
        """Different seeds produce different paths."""
        # Run with seed 10
        rng1 = RNG(10)
        grid1 = Grid(6, 6, allow_diagonal=True)
        path1 = PathBuilder._build_backbite_v1(grid1, rng1, blocked=None, max_time_ms=2000)
        
        # Run with seed 20
        rng2 = RNG(20)
        grid2 = Grid(6, 6, allow_diagonal=True)
        path2 = PathBuilder._build_backbite_v1(grid2, rng2, blocked=None, max_time_ms=2000)
        
        # Paths should differ (very high probability)
        assert len(path1) == len(path2) == 36
        
        differences = sum(
            1 for p1, p2 in zip(path1, path2)
            if p1.row != p2.row or p1.col != p2.col
        )
        
        # At least 50% of positions should differ
        assert differences > 18, f"Only {differences} positions differ, expected >18"
    
    def test_backbite_produces_valid_hamiltonian_path(self):
        """Backbite produces valid connected path."""
        rng = RNG(123)
        grid = Grid(5, 5, allow_diagonal=True)
        
        path = PathBuilder._build_backbite_v1(grid, rng, blocked=None, max_time_ms=2000)
        
        # Check all positions unique
        path_coords = [(p.row, p.col) for p in path]
        assert len(path_coords) == len(set(path_coords)), "Path has duplicate positions"
        
        # Check consecutive positions are adjacent
        for i in range(len(path) - 1):
            curr = path[i]
            next_pos = path[i + 1]
            
            dr = abs(curr.row - next_pos.row)
            dc = abs(curr.col - next_pos.col)
            
            # 8-neighbor adjacency
            is_adjacent = (dr <= 1 and dc <= 1 and (dr + dc) > 0)
            assert is_adjacent, f"Positions {i},{i+1} not adjacent: {curr} -> {next_pos}"
        
        # Check values assigned correctly
        for i, pos in enumerate(path, 1):
            cell = grid.get_cell(pos)
            assert cell.value == i, f"Position {pos}: expected value {i}, got {cell.value}"
