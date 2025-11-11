"""Tests for ambiguity detection and solution diffing (US2).

T029: Test solution diff algorithm, divergence clustering, and ambiguity region identification.
"""
import pytest
from core.position import Position
from generate.repair.models import AmbiguityRegion


def test_diff_identical_solutions():
    """T029: Diff identical solutions should return empty ambiguity regions."""
    from generate.repair.diff import diff_solutions
    
    solution1 = [(0, 0, 1), (0, 1, 2), (1, 0, 3), (1, 1, 4)]
    solution2 = [(0, 0, 1), (0, 1, 2), (1, 0, 3), (1, 1, 4)]
    
    regions = diff_solutions(solution1, solution2, size=2)
    
    assert regions == []


def test_diff_single_divergence():
    """T029: Single divergence cell should be identified."""
    from generate.repair.diff import diff_solutions
    
    # Solutions differ only at (1, 1)
    solution1 = [(0, 0, 1), (0, 1, 2), (1, 0, 3), (1, 1, 4)]
    solution2 = [(0, 0, 1), (0, 1, 2), (1, 0, 4), (1, 1, 3)]
    
    regions = diff_solutions(solution1, solution2, size=2)
    
    assert len(regions) == 1
    region = regions[0]
    assert len(region.cells) == 2  # Both divergent cells
    assert (1, 0) in region.cells or (1, 1) in region.cells


def test_diff_clustered_divergences():
    """T029: Adjacent divergences should cluster into single region."""
    from generate.repair.diff import diff_solutions
    
    # Multiple adjacent cells differ
    solution1 = [
        (0, 0, 1), (0, 1, 2), (0, 2, 3),
        (1, 0, 4), (1, 1, 5), (1, 2, 6),
        (2, 0, 7), (2, 1, 8), (2, 2, 9)
    ]
    solution2 = [
        (0, 0, 1), (0, 1, 2), (0, 2, 3),
        (1, 0, 4), (1, 1, 6), (1, 2, 5),  # (1,1) and (1,2) swapped
        (2, 0, 7), (2, 1, 8), (2, 2, 9)
    ]
    
    regions = diff_solutions(solution1, solution2, size=3)
    
    assert len(regions) == 1  # Adjacent divergences cluster
    region = regions[0]
    assert (1, 1) in region.cells
    assert (1, 2) in region.cells


def test_diff_separate_regions():
    """T029: Non-adjacent divergences should form separate regions."""
    from generate.repair.diff import diff_solutions
    
    # Divergences at opposite corners
    solution1 = [
        (0, 0, 1), (0, 1, 2), (0, 2, 3),
        (1, 0, 4), (1, 1, 5), (1, 2, 6),
        (2, 0, 7), (2, 1, 8), (2, 2, 9)
    ]
    solution2 = [
        (0, 0, 2), (0, 1, 1), (0, 2, 3),  # Top-left swap
        (1, 0, 4), (1, 1, 5), (1, 2, 6),
        (2, 0, 7), (2, 1, 9), (2, 2, 8)   # Bottom-right swap
    ]
    
    regions = diff_solutions(solution1, solution2, size=3)
    
    assert len(regions) == 2  # Two separate regions
    # Check that regions are spatially separate
    cells_0 = [pos for pos in regions[0].cells]
    cells_1 = [pos for pos in regions[1].cells]
    
    # One region should be top-left, other bottom-right
    top_left = any(pos[0] == 0 and pos[1] <= 1 for pos in cells_0)
    bottom_right = any(pos[0] == 2 and pos[1] >= 1 for pos in cells_1)
    
    assert top_left or bottom_right


def test_ambiguity_region_frequency():
    """T029: Ambiguity region should track divergence frequency."""
    from generate.repair.diff import diff_solutions
    
    solution1 = [(0, 0, 1), (0, 1, 2)]
    solution2 = [(0, 0, 2), (0, 1, 1)]
    
    regions = diff_solutions(solution1, solution2, size=1)
    
    assert len(regions) == 1
    region = regions[0]
    # Frequency should be 2 (both solutions diverge here)
    assert region.divergence_count == 2


def test_diff_diagonal_adjacency():
    """T029: Diagonal adjacency should be considered for clustering."""
    from generate.repair.diff import diff_solutions
    
    # Divergences at (0,0) and (1,1) - diagonally adjacent
    solution1 = [
        (0, 0, 1), (0, 1, 2),
        (1, 0, 3), (1, 1, 4)
    ]
    solution2 = [
        (0, 0, 2), (0, 1, 2),
        (1, 0, 3), (1, 1, 1)
    ]
    
    regions = diff_solutions(solution1, solution2, size=2, allow_diagonal=True)
    
    # With diagonal adjacency, should cluster into one region
    assert len(regions) == 1
    assert len(regions[0].cells) == 2


def test_diff_no_diagonal_adjacency():
    """T029: Without diagonal, diagonal divergences should be separate regions."""
    from generate.repair.diff import diff_solutions
    
    # Same as above but without diagonal adjacency
    solution1 = [
        (0, 0, 1), (0, 1, 2),
        (1, 0, 3), (1, 1, 4)
    ]
    solution2 = [
        (0, 0, 2), (0, 1, 2),
        (1, 0, 3), (1, 1, 1)
    ]
    
    regions = diff_solutions(solution1, solution2, size=2, allow_diagonal=False)
    
    # Without diagonal adjacency, should be separate
    assert len(regions) == 2


def test_ambiguity_region_properties():
    """T029: AmbiguityRegion should have correct properties."""
    cells = {(1, 1), (1, 2), (2, 1)}
    region = AmbiguityRegion(cells=cells, divergence_count=2)
    
    assert len(region.cells) == 3
    assert region.divergence_count == 2
    assert (1, 1) in region.cells
    assert (1, 2) in region.cells
    assert (2, 1) in region.cells


def test_diff_multiple_solutions():
    """T029: Diff multiple solutions should aggregate frequencies."""
    from generate.repair.diff import diff_multiple_solutions
    
    solutions = [
        [(0, 0, 1), (0, 1, 2)],
        [(0, 0, 2), (0, 1, 1)],  # Diverges at both
        [(0, 0, 1), (0, 1, 1)],  # Diverges at (0,1)
    ]
    
    regions = diff_multiple_solutions(solutions, size=1)
    
    assert len(regions) >= 1
    # Cell (0,1) should have higher frequency (appears in 2/3 divergences)
    region = regions[0]
    assert region.divergence_count >= 2
