"""
Tests for size/difficulty anchor policies (US2).

Contract validation for anchor selection, turn detection,
and spacing constraints.
"""
import pytest
from generate.anchors_policy import (
    get_anchor_policy,
    select_anchor_positions,
    _find_turns,
    _select_spaced_turns,
    AnchorPolicy,
)


class TestAnchorPolicyRetrieval:
    """Test policy selection by size and difficulty."""
    
    def test_easy_small_includes_turns(self):
        """Easy small puzzle should include turn anchors."""
        policy = get_anchor_policy("easy", 5)  # 5x5 = 25 cells
        assert policy.difficulty == "easy"
        assert policy.size_tier == "small"
        assert policy.retain_endpoints == True
        assert policy.max_turn_anchors >= 2
    
    def test_medium_allows_soft_turn(self):
        """Medium difficulty should allow one soft turn."""
        policy = get_anchor_policy("medium", 8)  # 8x8 = 64 cells
        assert policy.difficulty == "medium"
        assert policy.size_tier == "medium"
        assert policy.max_turn_anchors == 1
        assert policy.soft_turn_allowed == True
    
    def test_hard_endpoints_only(self):
        """Hard difficulty should retain endpoints only."""
        policy = get_anchor_policy("hard", 10)  # 10x10 = 100 cells
        assert policy.difficulty == "hard"
        assert policy.size_tier == "large"
        assert policy.max_turn_anchors == 0
        assert policy.soft_turn_allowed == False
    
    def test_size_tier_boundaries(self):
        """Size tiers should map correctly."""
        assert get_anchor_policy("easy", 5).size_tier == "small"   # 25 cells
        assert get_anchor_policy("easy", 6).size_tier == "medium"  # 36 cells
        assert get_anchor_policy("easy", 9).size_tier == "large"   # 81 cells
        assert get_anchor_policy("easy", 11).size_tier == "very_large"  # 121 cells


class TestTurnDetection:
    """Test turn position detection in paths."""
    
    def test_straight_path_no_turns(self):
        """Straight horizontal path should have no turns."""
        path = [(0, 0), (0, 1), (0, 2), (0, 3)]
        turns = _find_turns(path)
        assert len(turns) == 0
    
    def test_single_turn_detected(self):
        """L-shaped path should detect one turn."""
        path = [(0, 0), (0, 1), (0, 2), (1, 2)]
        turns = _find_turns(path)
        assert len(turns) == 1
        assert turns[0] == 2  # Turn at index 2: (0,2)
    
    def test_multiple_turns(self):
        """Zigzag path should detect all turns."""
        path = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0)]
        turns = _find_turns(path)
        assert len(turns) == 3  # Turns at indices 1, 2, 3
    
    def test_diagonal_counts_as_turn(self):
        """Diagonal after horizontal is a direction change."""
        path = [(0, 0), (0, 1), (1, 2)]
        turns = _find_turns(path)
        assert len(turns) == 1
    
    def test_path_too_short_no_turns(self):
        """Path with <3 positions has no turns."""
        assert _find_turns([]) == []
        assert _find_turns([(0, 0)]) == []
        assert _find_turns([(0, 0), (0, 1)]) == []


class TestSpacedTurnSelection:
    """Test evenly spaced turn selection."""
    
    def test_selects_requested_count(self):
        """Should select up to max_count turns."""
        turn_indices = [5, 10, 15, 20, 25, 30]
        selected = _select_spaced_turns(turn_indices, 3, "easy", 50)
        assert len(selected) <= 3
    
    def test_respects_minimum_gap(self):
        """Selected turns should have minimum spacing."""
        turn_indices = [5, 6, 7, 20, 21, 35]
        selected = _select_spaced_turns(turn_indices, 3, "medium", 50)
        
        # Check gaps between selected turns
        for i in range(len(selected) - 1):
            gap = selected[i + 1] - selected[i]
            assert gap >= 5  # Minimum gap enforced
    
    def test_empty_input_returns_empty(self):
        """No turns available should return empty."""
        assert _select_spaced_turns([], 3, "easy", 50) == []
    
    def test_zero_count_returns_empty(self):
        """Max count of 0 should return empty."""
        turn_indices = [5, 10, 15]
        assert _select_spaced_turns(turn_indices, 0, "easy", 50) == []


class TestAnchorSelection:
    """Test complete anchor selection."""
    
    def test_always_includes_endpoints(self):
        """Endpoints should always be in anchor list."""
        path = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0)]
        policy = AnchorPolicy("hard", "small", True, 0, False)
        anchors = select_anchor_positions(path, policy)
        assert 0 in anchors  # First position
        assert len(path) - 1 in anchors  # Last position
    
    def test_easy_includes_turn_anchors(self):
        """Easy difficulty should add turn anchors."""
        # Create path with multiple turns
        path = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (2, 1)]
        policy = get_anchor_policy("easy", 5)
        anchors = select_anchor_positions(path, policy)
        assert len(anchors) > 2  # More than just endpoints
    
    def test_hard_only_endpoints(self):
        """Hard difficulty should only keep endpoints."""
        path = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0)]
        policy = get_anchor_policy("hard", 5)
        anchors = select_anchor_positions(path, policy)
        assert len(anchors) == 2  # Only endpoints
        assert anchors == [0, len(path) - 1]
    
    def test_no_duplicate_anchors(self):
        """Anchor list should have no duplicates."""
        path = [(0, 0), (0, 1), (1, 1)]
        policy = get_anchor_policy("medium", 5)
        anchors = select_anchor_positions(path, policy)
        assert len(anchors) == len(set(anchors))
    
    def test_anchors_sorted(self):
        """Anchor indices should be sorted."""
        path = [(i, 0) for i in range(20)]  # Long straight path
        policy = get_anchor_policy("easy", 5)
        anchors = select_anchor_positions(path, policy)
        assert anchors == sorted(anchors)


# Placeholder for future contract tests
class TestAnchorContracts:
    """Contract validation for anchor policies."""
    
    @pytest.mark.skip(reason="Requires generator integration")
    def test_anchors_never_removed_during_generation(self):
        """Anchors should remain as givens throughout removal loop."""
        pass
    
    @pytest.mark.skip(reason="Requires generator integration")
    def test_soft_anchors_removable_if_spacing_improves(self):
        """Soft anchors can be removed if spacing score increases."""
        pass
