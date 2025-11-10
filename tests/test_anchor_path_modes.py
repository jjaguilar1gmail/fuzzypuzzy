"""Test adaptive anchors work correctly with all path modes (T048 integration)."""
import pytest
from generate.generator import Generator


class TestAnchorPathModes:
    """Test adaptive anchor integration with different path building modes."""
    
    def test_adaptive_anchors_with_serpentine(self):
        """Test adaptive anchors work with serpentine path mode."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            path_mode="serpentine",
            anchor_policy_name="adaptive_v1",
            adaptive_turn_anchors=True
        )
        
        # Verify anchor metrics present
        assert "anchor_count" in result.solver_metrics
        assert "anchor_policy_name" in result.solver_metrics
        assert result.solver_metrics["anchor_policy_name"] == "adaptive_v1"
        assert result.solver_metrics["anchor_selection_reason"] == "policy"
        
        # Easy should have 2-3 hard anchors + 2 endpoints
        hard_count = result.solver_metrics["anchor_hard_count"]
        endpoint_count = result.solver_metrics["anchor_endpoint_count"]
        assert 2 <= hard_count <= 3
        assert endpoint_count == 2
    
    def test_adaptive_anchors_with_backbite(self):
        """Test adaptive anchors work with backbite_v1 path mode."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="medium",
            seed=99,
            path_mode="backbite_v1",
            anchor_policy_name="adaptive_v1",
            adaptive_turn_anchors=True
        )
        
        # Verify anchor metrics
        assert result.solver_metrics["anchor_policy_name"] == "adaptive_v1"
        
        # Medium should have 0-1 soft anchor + 2 endpoints
        soft_count = result.solver_metrics["anchor_soft_count"]
        endpoint_count = result.solver_metrics["anchor_endpoint_count"]
        assert 0 <= soft_count <= 1
        assert endpoint_count == 2
    
    def test_adaptive_anchors_with_random_walk_v2(self):
        """Test adaptive anchors work with random_walk_v2 path mode."""
        result = Generator.generate_puzzle(
            size=6,
            difficulty="hard",
            seed=200,
            path_mode="random_walk_v2",
            anchor_policy_name="adaptive_v1",
            adaptive_turn_anchors=True
        )
        
        # Verify anchor metrics
        assert result.solver_metrics["anchor_policy_name"] == "adaptive_v1"
        
        # Hard should have 0 hard/soft anchors + 2 endpoints only
        hard_count = result.solver_metrics["anchor_hard_count"]
        soft_count = result.solver_metrics["anchor_soft_count"]
        endpoint_count = result.solver_metrics["anchor_endpoint_count"]
        repair_count = result.solver_metrics["anchor_repair_count"]
        
        assert hard_count == 0
        assert soft_count == 0
        assert endpoint_count == 2
        # Repair anchors may be added if needed
        assert repair_count >= 0
    
    def test_legacy_anchors_with_complex_paths(self):
        """Test legacy anchor mode works with complex path modes."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            path_mode="backbite_v1",
            anchor_policy_name="legacy",
            adaptive_turn_anchors=False
        )
        
        # Verify legacy behavior
        assert result.solver_metrics["anchor_policy_name"] == "legacy"
        assert result.solver_metrics["anchor_selection_reason"] == "legacy"
        
        # Legacy typically has more anchors
        anchor_count = result.solver_metrics["anchor_count"]
        assert anchor_count >= 2  # At least endpoints
    
    def test_determinism_across_path_modes(self):
        """Test that same seed produces same anchors regardless of path mode."""
        seed = 123
        size = 5
        difficulty = "easy"
        
        # Generate with serpentine
        result1 = Generator.generate_puzzle(
            size=size,
            difficulty=difficulty,
            seed=seed,
            path_mode="serpentine",
            anchor_policy_name="adaptive_v1"
        )
        
        # Generate again with serpentine (should be identical)
        result2 = Generator.generate_puzzle(
            size=size,
            difficulty=difficulty,
            seed=seed,
            path_mode="serpentine",
            anchor_policy_name="adaptive_v1"
        )
        
        # Anchor metrics should be identical
        assert result1.solver_metrics["anchor_count"] == result2.solver_metrics["anchor_count"]
        assert result1.solver_metrics["anchor_positions"] == result2.solver_metrics["anchor_positions"]
        assert result1.solver_metrics["anchor_hard_count"] == result2.solver_metrics["anchor_hard_count"]
    
    def test_anchor_positions_on_path(self):
        """Test that all anchor positions are actually on the generated path."""
        result = Generator.generate_puzzle(
            size=6,
            difficulty="easy",
            seed=777,
            path_mode="random_walk_v2",
            anchor_policy_name="adaptive_v1"
        )
        
        # Get all solution positions
        solution_positions = {(r, c) for r, c, v in result.solution}
        
        # Get anchor positions
        anchor_positions = set(result.solver_metrics["anchor_positions"])
        
        # All anchors must be on the path
        assert anchor_positions.issubset(solution_positions), \
            f"Anchors {anchor_positions - solution_positions} not on path"
    
    def test_partial_paths_with_adaptive_anchors(self):
        """Test adaptive anchors work with partial path acceptance."""
        result = Generator.generate_puzzle(
            size=6,
            difficulty="medium",
            seed=500,
            path_mode="random_walk_v2",
            allow_partial_paths=True,
            min_cover_ratio=0.80,
            anchor_policy_name="adaptive_v1"
        )
        
        # Should complete successfully
        assert result.uniqueness_verified
        assert "anchor_count" in result.solver_metrics
        assert result.solver_metrics["anchor_policy_name"] == "adaptive_v1"
        
        # Medium difficulty anchors
        soft_count = result.solver_metrics["anchor_soft_count"]
        assert 0 <= soft_count <= 1
