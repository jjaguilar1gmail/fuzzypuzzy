"""Test seed reproducibility across path modes.

Verify that same seed produces identical puzzles for all path building strategies.
"""

import pytest
from generate.generator import Generator


class TestSeedReproducibility:
    """Verify deterministic generation with same seed."""
    
    @pytest.mark.parametrize("path_mode", ["serpentine", "backbite_v1", "random_walk_v2"])
    def test_same_seed_identical_puzzles(self, path_mode):
        """Same seed should produce identical givens across runs.
        
        Note: random_walk (legacy) excluded due to potential hanging.
        """
        seed = 12345
        size = 6
        
        # Generate twice with same seed
        result1 = Generator.generate_puzzle(
            size=size,
            difficulty="medium",
            seed=seed,
            path_mode=path_mode,
            allow_partial_paths=False,
        )
        result2 = Generator.generate_puzzle(
            size=size,
            difficulty="medium",
            seed=seed,
            path_mode=path_mode,
            allow_partial_paths=False,
        )
        
        # Should have identical givens
        assert result1.givens == result2.givens, f"{path_mode}: Different givens with same seed"
        
        # Should have identical solutions
        assert result1.solution == result2.solution, f"{path_mode}: Different solutions with same seed"
        
        # Should have same difficulty
        assert result1.difficulty_label == result2.difficulty_label
        assert result1.difficulty_score == result2.difficulty_score
    
    def test_different_seeds_different_puzzles(self):
        """Different seeds should produce different puzzles."""
        size = 6
        path_mode = "backbite_v1"
        
        result1 = Generator.generate_puzzle(
            size=size,
            difficulty="medium",
            seed=100,
            path_mode=path_mode,
            allow_partial_paths=False,
        )
        
        result2 = Generator.generate_puzzle(
            size=size,
            difficulty="medium",
            seed=200,
            path_mode=path_mode,
            allow_partial_paths=False,
        )
        
        # Should have different givens (highly likely with different seeds)
        assert result1.givens != result2.givens, "Different seeds produced identical givens"
    
    def test_cross_mode_reproducibility_with_seed(self):
        """Verify each mode is independently deterministic."""
        seed = 99999
        size = 5
        
        modes = ["serpentine", "backbite_v1", "random_walk_v2"]
        results_by_mode = {}
        
        for mode in modes:
            result = Generator.generate_puzzle(
                size=size,
                difficulty="easy",
                seed=seed,
                path_mode=mode,
                allow_partial_paths=False,
            )
            results_by_mode[mode] = result.givens
        
        # Each mode should be deterministic (run again and check)
        for mode in modes:
            result = Generator.generate_puzzle(
                size=size,
                difficulty="easy",
                seed=seed,
                path_mode=mode,
                allow_partial_paths=False,
            )
            assert result.givens == results_by_mode[mode], f"{mode}: Not deterministic"
    
    def test_partial_paths_reproducible(self):
        """Partial path acceptance should also be deterministic."""
        seed = 77777
        size = 7
        
        result1 = Generator.generate_puzzle(
            size=size,
            difficulty="hard",
            seed=seed,
            path_mode="random_walk_v2",
            allow_partial_paths=True,
            min_cover_ratio=0.80,
            path_time_ms=1000,  # Short time to encourage partial paths
        )
        result2 = Generator.generate_puzzle(
            size=size,
            difficulty="hard",
            seed=seed,
            path_mode="random_walk_v2",
            allow_partial_paths=True,
            min_cover_ratio=0.80,
            path_time_ms=1000,
        )
        
        # Should have identical results
        assert result1.givens == result2.givens
        assert result1.blocked_cells == result2.blocked_cells
        
        # Coverage should also match
        coverage1 = result1.solver_metrics.get('path_coverage', 1.0)
        coverage2 = result2.solver_metrics.get('path_coverage', 1.0)
        assert coverage1 == coverage2
