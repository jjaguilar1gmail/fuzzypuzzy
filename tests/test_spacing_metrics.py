"""
Tests for spacing metrics and cluster detection (US2).

Contract validation for Manhattan distance, quadrant variance,
cluster detection, and scoring functions.
"""
import pytest
from generate.spacing import (
    avg_manhattan_distance,
    quadrant_variance,
    detect_clusters,
    spacing_score,
)


class TestManhattanDistance:
    """Test average Manhattan distance calculation."""
    
    def test_empty_clues_returns_zero(self):
        """No clues should return 0.0."""
        assert avg_manhattan_distance([]) == 0.0
    
    def test_single_clue_returns_zero(self):
        """Single clue has no pairs, should return 0.0."""
        assert avg_manhattan_distance([(0, 0)]) == 0.0
    
    def test_two_adjacent_clues(self):
        """Two adjacent clues should have distance 1.0."""
        result = avg_manhattan_distance([(0, 0), (0, 1)])
        assert result == 1.0
    
    def test_diagonal_clues(self):
        """Diagonal clues distance = |dr| + |dc|."""
        result = avg_manhattan_distance([(0, 0), (2, 2)])
        assert result == 4.0  # |2-0| + |2-0|
    
    def test_multiple_clues_average(self):
        """Average of all pairs should be computed correctly."""
        # (0,0) -> (1,0) = 1
        # (0,0) -> (0,2) = 2
        # (1,0) -> (0,2) = 1+2 = 3
        # Average = (1+2+3)/3 = 2.0
        result = avg_manhattan_distance([(0, 0), (1, 0), (0, 2)])
        assert result == pytest.approx(2.0)


class TestQuadrantVariance:
    """Test quadrant distribution variance."""
    
    def test_empty_clues_returns_zero(self):
        """No clues should return 0.0."""
        assert quadrant_variance([], 8) == 0.0
    
    def test_uniform_distribution_low_variance(self):
        """Clues evenly distributed should have low variance."""
        # 4 clues, one per quadrant in 8x8 board
        clues = [(1, 1), (1, 6), (6, 1), (6, 6)]
        result = quadrant_variance(clues, 8)
        assert result == 0.0  # Perfect balance
    
    def test_clustered_distribution_high_variance(self):
        """All clues in one quadrant should have high variance."""
        # All 4 clues in top-left quadrant
        clues = [(0, 0), (1, 1), (2, 2), (3, 3)]
        result = quadrant_variance(clues, 8)
        assert result > 0.8  # High variance (normalized 0-1)
    
    def test_partial_clustering(self):
        """3 in one quadrant, 1 in another should have moderate variance."""
        clues = [(1, 1), (2, 2), (3, 3), (6, 6)]
        result = quadrant_variance(clues, 8)
        assert 0.3 < result < 0.8


class TestClusterDetection:
    """Test 8-neighbor cluster detection."""
    
    def test_empty_clues_returns_empty(self):
        """No clues should return empty list."""
        assert detect_clusters([]) == []
    
    def test_single_clue_single_cluster(self):
        """Single clue forms one cluster."""
        result = detect_clusters([(5, 5)])
        assert len(result) == 1
        assert result[0] == [(5, 5)]
    
    def test_adjacent_clues_same_cluster(self):
        """8-connected clues should be in same cluster."""
        clues = [(0, 0), (0, 1), (1, 0)]  # L-shape
        result = detect_clusters(clues)
        assert len(result) == 1
        assert set(result[0]) == set(clues)
    
    def test_diagonal_adjacency_counts(self):
        """Diagonal neighbors should be in same cluster."""
        clues = [(0, 0), (1, 1), (2, 2)]
        result = detect_clusters(clues)
        assert len(result) == 1
    
    def test_separated_clues_different_clusters(self):
        """Non-adjacent clues should form separate clusters."""
        clues = [(0, 0), (5, 5), (10, 10)]
        result = detect_clusters(clues)
        assert len(result) == 3
    
    def test_two_separate_groups(self):
        """Two distinct groups should form 2 clusters."""
        clues = [(0, 0), (0, 1), (10, 10), (10, 11)]
        result = detect_clusters(clues)
        assert len(result) == 2
        cluster_sizes = sorted(len(c) for c in result)
        assert cluster_sizes == [2, 2]


class TestSpacingScore:
    """Test combined spacing score function."""
    
    def test_higher_distance_increases_score(self):
        """More spread clues should have higher score."""
        spread_clues = [(0, 0), (7, 7)]
        clustered_clues = [(0, 0), (0, 1)]
        spread_score = spacing_score(spread_clues, 8)
        clustered_score = spacing_score(clustered_clues, 8)
        assert spread_score > clustered_score
    
    def test_uniform_distribution_better_than_clustered(self):
        """Uniform distribution should score higher than clustered."""
        uniform = [(1, 1), (1, 6), (6, 1), (6, 6)]
        clustered = [(1, 1), (1, 2), (2, 1), (2, 2)]
        uniform_score = spacing_score(uniform, 8)
        clustered_score = spacing_score(clustered, 8)
        assert uniform_score > clustered_score
    
    def test_custom_weights(self):
        """Custom weights should affect score computation."""
        clues = [(0, 0), (3, 3), (6, 6)]
        score_default = spacing_score(clues, 8, w1=1.0, w2=0.5)
        score_emphasize_distance = spacing_score(clues, 8, w1=2.0, w2=0.5)
        score_emphasize_variance = spacing_score(clues, 8, w1=1.0, w2=1.0)
        
        # Higher w1 should increase score (more weight on distance)
        assert score_emphasize_distance > score_default
        # Higher w2 should decrease score (more penalty for variance)
        assert score_emphasize_variance < score_default


# Placeholder for future property tests
class TestSpacingProperties:
    """Property-based tests for spacing metrics."""
    
    @pytest.mark.skip(reason="Requires hypothesis library")
    def test_manhattan_distance_symmetric(self):
        """Distance should be symmetric: dist(A,B) = dist(B,A)."""
        pass
    
    @pytest.mark.skip(reason="Requires hypothesis library")
    def test_variance_bounded_0_to_1(self):
        """Quadrant variance should always be in [0, 1] range."""
        pass
    
    @pytest.mark.skip(reason="Requires hypothesis library")
    def test_cluster_count_never_exceeds_clue_count(self):
        """Number of clusters ≤ number of clues."""
        pass
