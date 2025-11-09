"""Test random_walk_v2 limits and behavior (T028-T030)."""
import pytest
import time
from core.grid import Grid
from generate.path_builder import PathBuilder
from util.rng import RNG


class TestRandomWalkV2Limits:
    """Test random_walk_v2 respects configured limits."""
    
    def test_random_walk_v2_respects_max_restarts(self):
        """Random walk v2 gives up after max_restarts."""
        # Use a difficult seed/size that's unlikely to succeed quickly
        rng = RNG(999)
        grid = Grid(7, 7, allow_diagonal=True)
        
        # Very tight timeout and low restarts
        start = time.time()
        path = PathBuilder._build_random_walk_v2(
            grid, rng, blocked=None, max_time_ms=1000, max_restarts=2
        )
        elapsed_ms = (time.time() - start) * 1000
        
        # Should fallback to serpentine if can't complete
        assert len(path) == 49
        assert elapsed_ms < 1500, f"Should respect timeout, took {elapsed_ms:.0f}ms"
    
    def test_random_walk_v2_completes_small_grids(self):
        """Random walk v2 successfully builds paths on small grids."""
        seeds = [42, 100, 200]
        
        for seed in seeds:
            rng = RNG(seed)
            grid = Grid(5, 5, allow_diagonal=True)
            
            path = PathBuilder._build_random_walk_v2(
                grid, rng, blocked=None, max_time_ms=3000, max_restarts=5
            )
            
            assert len(path) == 25, f"Seed {seed}: Expected 25 positions"
            
            # Check adjacency (Hamiltonian path property)
            for i in range(len(path) - 1):
                curr = path[i]
                next_pos = path[i + 1]
                dr = abs(curr.row - next_pos.row)
                dc = abs(curr.col - next_pos.col)
                is_adjacent = (dr <= 1 and dc <= 1 and (dr + dc) > 0)
                assert is_adjacent, f"Positions {i},{i+1} not adjacent"
    
    def test_random_walk_v2_deterministic(self):
        """Same seed produces same path with random_walk_v2."""
        seed = 123
        
        # Run 1
        rng1 = RNG(seed)
        grid1 = Grid(6, 6, allow_diagonal=True)
        path1 = PathBuilder._build_random_walk_v2(grid1, rng1, blocked=None)
        
        # Run 2
        rng2 = RNG(seed)
        grid2 = Grid(6, 6, allow_diagonal=True)
        path2 = PathBuilder._build_random_walk_v2(grid2, rng2, blocked=None)
        
        # Should be identical
        assert len(path1) == len(path2) == 36
        for i, (p1, p2) in enumerate(zip(path1, path2)):
            assert p1.row == p2.row and p1.col == p2.col, f"Position {i} differs"
    
    def test_random_walk_v2_handles_blocked_cells(self):
        """Random walk v2 works with blocked cells."""
        rng = RNG(55)
        grid = Grid(5, 5, allow_diagonal=True)
        
        from core.position import Position
        blocked = [(0, 0), (4, 4), (2, 2)]
        for r, c in blocked:
            pos = Position(r, c)
            grid.get_cell(pos).blocked = True
        
        path = PathBuilder._build_random_walk_v2(grid, rng, blocked=blocked)
        
        # Should have 25 - 3 = 22 positions
        assert len(path) == 22
        
        # No blocked positions in path
        path_coords = {(p.row, p.col) for p in path}
        assert path_coords.isdisjoint(set(blocked))


class TestRandomWalkV2Variety:
    """Test random_walk_v2 produces varied paths (T029)."""
    
    def test_different_seeds_produce_variety(self):
        """Different seeds produce different path structures."""
        seeds = [10, 20, 30, 40, 50]
        paths = []
        
        for seed in seeds:
            rng = RNG(seed)
            grid = Grid(6, 6, allow_diagonal=True)
            path = PathBuilder._build_random_walk_v2(grid, rng, blocked=None)
            paths.append(path)
        
        # All should be valid
        for path in paths:
            assert len(path) == 36
        
        # Count turn points for each path (measure of variety)
        def count_turns(path):
            """Count direction changes in path."""
            if len(path) < 3:
                return 0
            turns = 0
            for i in range(1, len(path) - 1):
                prev_dir = (path[i].row - path[i-1].row, path[i].col - path[i-1].col)
                next_dir = (path[i+1].row - path[i].row, path[i+1].col - path[i].col)
                if prev_dir != next_dir:
                    turns += 1
            return turns
        
        turn_counts = [count_turns(p) for p in paths]
        
        # Should have at least 3 distinct turn-count profiles
        unique_turn_counts = len(set(turn_counts))
        assert unique_turn_counts >= 3, f"Only {unique_turn_counts} distinct patterns, expected ≥3. Turns: {turn_counts}"
    
    def test_random_walk_v2_differs_from_serpentine(self):
        """Random walk v2 produces non-serpentine paths."""
        rng = RNG(123)
        grid1 = Grid(5, 5, allow_diagonal=True)
        random_path = PathBuilder._build_random_walk_v2(grid1, rng, blocked=None)
        
        grid2 = Grid(5, 5, allow_diagonal=True)
        serpentine_path = PathBuilder._build_serpentine(grid2, blocked=None)
        
        # Paths should differ significantly
        differences = sum(
            1 for p1, p2 in zip(random_path, serpentine_path)
            if p1.row != p2.row or p1.col != p2.col
        )
        
        # Expect at least 50% different positions
        assert differences > 12, f"Only {differences}/25 positions differ from serpentine"
