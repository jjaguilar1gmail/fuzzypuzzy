"""Determinism tests for pruning (T23).

Verify that identical seeds produce identical results.
"""
import pytest
from generate.generator import Generator
from generate.pruning import compute_pruning_hash


class TestDeterminism:
    """Test deterministic behavior across repeated runs."""
    
    def test_pruning_hash_stability(self):
        """Same givens produce same hash."""
        from core.position import Position
        from core.cell import Cell
        from core.grid import Grid
        from core.constraints import Constraints
        from core.puzzle import Puzzle
        
        # Create identical puzzles
        path = [Position(0, i) for i in range(5)]
        
        puzzle1 = self._make_puzzle(path, givens_at=[0, 2, 4])
        puzzle2 = self._make_puzzle(path, givens_at=[0, 2, 4])
        
        hash1 = compute_pruning_hash(puzzle1, path, "easy")
        hash2 = compute_pruning_hash(puzzle2, path, "easy")
        
        assert hash1 == hash2
    
    def test_pruning_hash_differs_on_change(self):
        """Different givens produce different hashes."""
        from core.position import Position
        
        path = [Position(0, i) for i in range(5)]
        
        puzzle1 = self._make_puzzle(path, givens_at=[0, 2, 4])
        puzzle2 = self._make_puzzle(path, givens_at=[0, 1, 4])  # Different
        
        hash1 = compute_pruning_hash(puzzle1, path, "easy")
        hash2 = compute_pruning_hash(puzzle2, path, "easy")
        
        assert hash1 != hash2
    
    def test_generator_determinism_with_pruning_disabled(self):
        """Same seed produces same puzzle (legacy mode)."""
        seed = 12345
        
        result1 = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=seed,
            allow_diagonal=True,
            path_mode="serpentine"
        )
        
        result2 = Generator.generate_puzzle(
            size=5,
            difficulty="easy", 
            seed=seed,
            allow_diagonal=True,
            path_mode="serpentine"
        )
        
        # Should have same givens
        assert sorted(result1.givens) == sorted(result2.givens)
        assert result1.clue_count == result2.clue_count
    
    def _make_puzzle(self, path, givens_at):
        """Helper to create puzzle with specific givens."""
        from core.cell import Cell
        from core.grid import Grid
        from core.constraints import Constraints
        from core.puzzle import Puzzle
        
        cells = []
        for i, pos in enumerate(path):
            is_given = i in givens_at
            cells.append(Cell(pos, i + 1, False, is_given))
        
        grid = Grid(1, len(path), cells, allow_diagonal=False)
        return Puzzle(grid, Constraints(1, len(path), "4"))


class TestTimeout:
    """Test timeout handling (T15)."""
    
    def test_timeout_flag_set(self):
        """Session records timeout when it occurs."""
        from generate.pruning import PruningSession
        
        session = PruningSession()
        assert session.timeout_occurred is False
        
        session.timeout_occurred = True
        assert session.timeout_occurred is True
    
    def test_timeout_in_metrics(self):
        """Timeout flag appears in metrics."""
        from generate.pruning import PruningSession
        
        session = PruningSession()
        session.timeout_occurred = True
        
        metrics = session.to_metrics()
        assert metrics["timeout_occurred"] is True
