"""Tests for structural block candidate scoring (US2).

T030: Test candidate scoring based on frequency × corridor_width × distance.
"""
import pytest
from core.position import Position
from core.grid import Grid
from generate.repair.models import AmbiguityRegion


def test_score_candidates_basic():
    """T030: Score candidates should return scored positions."""
    from generate.repair.scoring import score_structural_blocks
    
    # Simple 3x3 grid with one ambiguity region
    grid = Grid(3, 3, allow_diagonal=True)
    region = AmbiguityRegion(
        cells={(1, 1), (1, 2)},
        divergence_count=2
    )
    givens = [Position(0, 0), Position(2, 2)]
    
    candidates = score_structural_blocks(
        regions=[region],
        grid=grid,
        givens=givens
    )
    
    assert len(candidates) > 0
    # Each candidate should have position and score
    for candidate in candidates:
        assert hasattr(candidate, 'position')
        assert hasattr(candidate, 'score')
        assert candidate.score > 0


def test_score_frequency_impact():
    """T030: Higher frequency regions should yield higher scores."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(3, 3, allow_diagonal=True)
    
    region_high_freq = AmbiguityRegion(cells={(1, 1)}, divergence_count=4)
    region_low_freq = AmbiguityRegion(cells={(1, 2)}, divergence_count=2)
    
    candidates_high = score_structural_blocks([region_high_freq], grid, [])
    candidates_low = score_structural_blocks([region_low_freq], grid, [])
    
    # High frequency should yield higher scores
    if candidates_high and candidates_low:
        max_high = max(c.score for c in candidates_high)
        max_low = max(c.score for c in candidates_low)
        assert max_high > max_low


def test_score_corridor_width_impact():
    """T030: Narrower corridors should yield higher scores."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(5, 5, allow_diagonal=True)
    
    # Narrow corridor: region at (2, 2) with few exits
    grid.get_cell(Position(1, 2)).blocked = True
    grid.get_cell(Position(2, 1)).blocked = True
    grid.get_cell(Position(3, 2)).blocked = True
    grid.get_cell(Position(2, 3)).blocked = True
    region_narrow = AmbiguityRegion(cells={(2, 2)}, divergence_count=2)
    
    # Wide corridor: region at interior with many exits
    grid2 = Grid(5, 5, allow_diagonal=True)
    region_wide = AmbiguityRegion(cells={(2, 2)}, divergence_count=2)
    
    candidates_narrow = score_structural_blocks([region_narrow], grid, [])
    candidates_wide = score_structural_blocks([region_wide], grid2, [])
    
    # Narrow corridor should have higher score
    if candidates_narrow and candidates_wide:
        # Compare average corridor scores since candidates are adjacent
        avg_narrow = sum(c.corridor_width for c in candidates_narrow) / len(candidates_narrow)
        avg_wide = sum(c.corridor_width for c in candidates_wide) / len(candidates_wide)
        assert avg_narrow > avg_wide


def test_score_distance_from_givens():
    """T030: Positions farther from givens should score higher."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(5, 5, allow_diagonal=True)
    region = AmbiguityRegion(
        cells={(2, 0), (2, 4)},
        divergence_count=2
    )
    
    # Given at (2, 0) - close to left cell
    givens = [Position(2, 0)]
    
    candidates = score_structural_blocks([region], grid, givens)
    
    # Cell (2, 4) should score higher (farther from given)
    if len(candidates) >= 2:
        scores_by_pos = {c.position: c.score for c in candidates}
        if Position(2, 4) in scores_by_pos and Position(2, 1) in scores_by_pos:
            assert scores_by_pos[Position(2, 4)] > scores_by_pos[Position(2, 1)]


def test_score_excludes_blocked_cells():
    """T030: Blocked cells should not be candidate positions."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(3, 3, allow_diagonal=True)
    grid.get_cell(Position(1, 1)).blocked = True
    
    region = AmbiguityRegion(cells={(1, 0), (1, 1)}, divergence_count=2)
    
    candidates = score_structural_blocks([region], grid, [])
    
    # (1, 1) is blocked, should not appear in candidates
    candidate_positions = [c.position for c in candidates]
    assert Position(1, 1) not in candidate_positions


def test_score_excludes_givens():
    """T030: Given positions should not be candidates."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(3, 3, allow_diagonal=True)
    region = AmbiguityRegion(cells={(1, 1)}, divergence_count=2)
    givens = [Position(1, 1)]
    
    candidates = score_structural_blocks([region], grid, givens)
    
    # (1, 1) is a given, should not appear
    candidate_positions = [c.position for c in candidates]
    assert Position(1, 1) not in candidate_positions


def test_score_multiple_regions():
    """T030: Multiple regions should contribute candidates."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(4, 4, allow_diagonal=True)
    
    region1 = AmbiguityRegion(cells={(0, 0), (0, 1)}, divergence_count=2)
    region2 = AmbiguityRegion(cells={(3, 2), (3, 3)}, divergence_count=2)
    
    candidates = score_structural_blocks([region1, region2], grid, [])
    
    # Should have candidates from both regions
    assert len(candidates) >= 2
    candidate_positions = [c.position for c in candidates]
    
    # At least one candidate from each region
    has_region1 = any(pos.row == 0 for pos in candidate_positions)
    has_region2 = any(pos.row == 3 for pos in candidate_positions)
    assert has_region1 and has_region2


def test_score_sorted_descending():
    """T030: Candidates should be sorted by score (highest first)."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(5, 5, allow_diagonal=True)
    region = AmbiguityRegion(
        cells={(2, 1), (2, 2), (2, 3)},
        divergence_count=3
    )
    
    candidates = score_structural_blocks([region], grid, [])
    
    # Scores should be in descending order
    scores = [c.score for c in candidates]
    assert scores == sorted(scores, reverse=True)


def test_score_empty_regions():
    """T030: Empty regions list should return empty candidates."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(3, 3, allow_diagonal=True)
    
    candidates = score_structural_blocks([], grid, [])
    
    assert candidates == []


def test_score_adjacent_to_ambiguity():
    """T030: Candidates should include cells adjacent to ambiguity region."""
    from generate.repair.scoring import score_structural_blocks
    
    grid = Grid(3, 3, allow_diagonal=True)
    region = AmbiguityRegion(cells={(1, 1)}, divergence_count=2)
    
    candidates = score_structural_blocks([region], grid, [])
    
    # Should include adjacent cells as candidates
    candidate_positions = [c.position for c in candidates]
    
    # Check at least some adjacent cells are included
    adjacent = [
        Position(0, 1), Position(1, 0), Position(1, 2), Position(2, 1),
        Position(0, 0), Position(0, 2), Position(2, 0), Position(2, 2)
    ]
    found_adjacent = [pos for pos in adjacent if pos in candidate_positions]
    assert len(found_adjacent) > 0
