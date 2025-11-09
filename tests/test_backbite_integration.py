"""Integration test for backbite_v1 mode in full generation pipeline."""
import pytest
from generate.generator import Generator


class TestBackbiteIntegration:
    """Test backbite_v1 mode in full puzzle generation."""
    
    def test_backbite_generates_valid_puzzle(self):
        """Backbite mode produces valid, solvable puzzle."""
        result = Generator.generate_puzzle(
            size=6,
            difficulty="medium",
            seed=42,
            allow_diagonal=True,
            path_mode="backbite_v1"
        )
        
        # Basic validation
        assert result.size == 6
        assert result.clue_count > 0
        assert result.clue_count < 36  # Not all cells
        assert result.uniqueness_verified
        assert result.seed == 42
        assert result.path_mode == "backbite_v1"
        
        # Check givens are valid
        assert len(result.givens) == result.clue_count
        for r, c, v in result.givens:
            assert 0 <= r < 6
            assert 0 <= c < 6
            assert 1 <= v <= 36
        
        # Check solution is complete
        assert len(result.solution) == 36
    
    def test_backbite_respects_seed(self):
        """Same seed produces identical puzzle with backbite."""
        result1 = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=123,
            path_mode="backbite_v1"
        )
        
        result2 = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=123,
            path_mode="backbite_v1"
        )
        
        # Should be identical
        assert result1.givens == result2.givens
        assert result1.solution == result2.solution
        assert result1.clue_count == result2.clue_count
    
    def test_backbite_different_from_serpentine(self):
        """Backbite produces different solution path than serpentine."""
        serpentine_result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=99,
            path_mode="serpentine"
        )
        
        backbite_result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=99,
            path_mode="backbite_v1"
        )
        
        # Solutions should differ (different paths)
        assert serpentine_result.solution != backbite_result.solution
    
    def test_backbite_handles_blocked_cells(self):
        """Backbite works with blocked cells."""
        blocked = [(0, 0), (4, 4)]
        
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=55,
            blocked=blocked,
            path_mode="backbite_v1"
        )
        
        # Should have 25 - 2 = 23 cells in solution
        assert len(result.solution) == 23
        assert result.blocked_cells == blocked
        
        # No givens or solution values in blocked cells
        blocked_coords = {(r, c) for r, c in blocked}
        for r, c, _ in result.givens:
            assert (r, c) not in blocked_coords
        for r, c, _ in result.solution:
            assert (r, c) not in blocked_coords
    
    def test_backbite_performance_9x9(self):
        """Backbite completes 9x9 in reasonable time."""
        import time
        
        start = time.time()
        result = Generator.generate_puzzle(
            size=9,
            difficulty="medium",
            seed=17,
            path_mode="backbite_v1"
        )
        elapsed_ms = (time.time() - start) * 1000
        
        assert result.size == 9
        assert result.uniqueness_verified
        
        # Should complete in under 10 seconds (including uniqueness checks)
        assert elapsed_ms < 10000, f"Generation took {elapsed_ms:.0f}ms"
