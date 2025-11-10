"""Test adaptive anchor counts per difficulty (T057)."""
import pytest
from generate.generator import Generator


class TestAnchorCounts:
    """Test anchor count bounds for each difficulty."""
    
    def test_easy_anchor_count(self):
        """Easy difficulty should have 2-3 hard anchors plus endpoints."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        # Easy: 2-3 hard anchors + 2 endpoints
        anchor_count = result.solver_metrics['anchor_count']
        hard_count = result.solver_metrics['anchor_hard_count']
        endpoint_count = result.solver_metrics['anchor_endpoint_count']
        
        assert endpoint_count == 2, "Should have 2 endpoints"
        assert 2 <= hard_count <= 3, f"Easy should have 2-3 hard anchors, got {hard_count}"
        assert anchor_count == hard_count + endpoint_count
    
    def test_medium_anchor_count(self):
        """Medium difficulty should have 0-1 soft anchor plus endpoints."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="medium",
            seed=42,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        soft_count = result.solver_metrics['anchor_soft_count']
        endpoint_count = result.solver_metrics['anchor_endpoint_count']
        
        assert endpoint_count == 2, "Should have 2 endpoints"
        assert 0 <= soft_count <= 1, f"Medium should have 0-1 soft anchor, got {soft_count}"
    
    def test_hard_anchor_count(self):
        """Hard difficulty should have only endpoints (unless repair needed)."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="hard",
            seed=42,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        hard_count = result.solver_metrics['anchor_hard_count']
        soft_count = result.solver_metrics['anchor_soft_count']
        repair_count = result.solver_metrics['anchor_repair_count']
        endpoint_count = result.solver_metrics['anchor_endpoint_count']
        anchor_reason = result.solver_metrics['anchor_selection_reason']
        
        assert endpoint_count == 2, "Should have 2 endpoints"
        
        # Hard should have no hard/soft anchors unless repair
        if anchor_reason != "repair":
            assert hard_count == 0, f"Hard should have no hard anchors (non-repair), got {hard_count}"
            assert soft_count == 0, f"Hard should have no soft anchors (non-repair), got {soft_count}"
    
    def test_extreme_anchor_count(self):
        """Extreme difficulty should have only endpoints (unless repair needed)."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="extreme",
            seed=99,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        hard_count = result.solver_metrics['anchor_hard_count']
        soft_count = result.solver_metrics['anchor_soft_count']
        endpoint_count = result.solver_metrics['anchor_endpoint_count']
        anchor_reason = result.solver_metrics['anchor_selection_reason']
        
        assert endpoint_count == 2, "Should have 2 endpoints"
        
        # Extreme should have no hard/soft anchors unless repair
        if anchor_reason != "repair":
            assert hard_count == 0, f"Extreme should have no hard anchors (non-repair), got {hard_count}"
            assert soft_count == 0, f"Extreme should have no soft anchors (non-repair), got {soft_count}"
    
    def test_policy_metadata_present(self):
        """All anchor metrics should be present."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="medium",
            seed=42,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        metrics = result.solver_metrics
        
        # Check all required fields exist
        assert 'anchor_count' in metrics
        assert 'anchor_hard_count' in metrics
        assert 'anchor_soft_count' in metrics
        assert 'anchor_repair_count' in metrics
        assert 'anchor_endpoint_count' in metrics
        assert 'anchor_positions' in metrics
        assert 'anchor_policy_name' in metrics
        assert 'anchor_selection_reason' in metrics
        
        # Check policy name
        assert metrics['anchor_policy_name'] == "adaptive_v1"
        assert metrics['anchor_selection_reason'] in ["policy", "repair", "legacy"]
    
    def test_legacy_policy_behavior(self):
        """Legacy policy should use old turn anchor logic."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            adaptive_turn_anchors=False
        )
        
        policy_name = result.solver_metrics['anchor_policy_name']
        anchor_reason = result.solver_metrics['anchor_selection_reason']
        
        assert policy_name == "legacy", f"Should use legacy policy, got {policy_name}"
        assert anchor_reason == "legacy", f"Should have legacy reason, got {anchor_reason}"
    
    def test_determinism_anchor_selection(self):
        """Same seed should produce identical anchor selections."""
        result1 = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=123,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        result2 = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=123,
            adaptive_turn_anchors=True,
            anchor_policy_name="adaptive_v1"
        )
        
        # Check anchor positions are identical
        positions1 = sorted(result1.solver_metrics['anchor_positions'])
        positions2 = sorted(result2.solver_metrics['anchor_positions'])
        
        assert positions1 == positions2, "Anchor positions should be deterministic"
        assert result1.solver_metrics['anchor_count'] == result2.solver_metrics['anchor_count']
