"""Test backbite_v1 speed requirements (T018)."""
import pytest
import time
from core.grid import Grid
from core.position import Position
from generate.path_builder import PathBuilder
from util.rng import RNG


class TestBackbiteSpeed:
    """Test backbite_v1 meets speed requirements."""
    
    def test_backbite_9x9_under_6000ms(self):
        """Backbite completes 9x9 within 6000ms budget (p90 target)."""
        seeds = [11, 13, 17, 19, 23]  # Five test seeds
        
        for seed in seeds:
            rng = RNG(seed)
            grid = Grid(9, 9, allow_diagonal=True)
            
            start = time.time()
            path = PathBuilder._build_backbite_v1(grid, rng, blocked=None, max_time_ms=6000)
            elapsed_ms = (time.time() - start) * 1000
            
            # Verify completion
            assert len(path) == 81, f"Seed {seed}: Expected 81 positions, got {len(path)}"
            
            # Verify speed
            assert elapsed_ms < 6000, f"Seed {seed}: Took {elapsed_ms:.0f}ms, expected <6000ms"
            
            print(f"Seed {seed}: {elapsed_ms:.0f}ms, path length {len(path)}")
    
    def test_backbite_6x6_under_2000ms(self):
        """Backbite completes 6x6 within 2000ms budget."""
        seeds = [7, 11, 13]
        
        for seed in seeds:
            rng = RNG(seed)
            grid = Grid(6, 6, allow_diagonal=True)
            
            start = time.time()
            path = PathBuilder._build_backbite_v1(grid, rng, blocked=None, max_time_ms=2000)
            elapsed_ms = (time.time() - start) * 1000
            
            assert len(path) == 36
            assert elapsed_ms < 2000, f"Seed {seed}: Took {elapsed_ms:.0f}ms"
    
    def test_backbite_with_blocked_cells(self):
        """Backbite handles blocked cells correctly."""
        rng = RNG(42)
        grid = Grid(5, 5, allow_diagonal=True)
        
        # Block corner cells
        blocked = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for r, c in blocked:
            pos = Position(r, c)
            grid.get_cell(pos).blocked = True
        
        path = PathBuilder._build_backbite_v1(grid, rng, blocked=blocked, max_time_ms=2000)
        
        # Should have 25 - 4 = 21 positions
        assert len(path) == 21
        
        # Verify no blocked positions in path
        path_coords = {(p.row, p.col) for p in path}
        assert path_coords.isdisjoint(set(blocked))
    
    def test_backbite_convergence_early_exit(self):
        """Backbite exits early when no changes occur."""
        rng = RNG(99)
        grid = Grid(4, 4, allow_diagonal=True)
        
        # Small grid should converge quickly
        start = time.time()
        path = PathBuilder._build_backbite_v1(grid, rng, blocked=None, max_time_ms=5000)
        elapsed_ms = (time.time() - start) * 1000
        
        assert len(path) == 16
        # Should exit early, not use full budget
        assert elapsed_ms < 1000, f"Expected early exit, took {elapsed_ms:.0f}ms"
