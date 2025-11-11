"""Edge case tests for ambiguity repair (T051 Polish).

Tests boundary conditions and error handling for repair operations.
"""
import pytest
from core.grid import Grid
from core.position import Position
from generate.repair import apply_structural_repair
from generate.repair.diff import diff_solutions, diff_multiple_solutions
from generate.repair.scoring import score_structural_blocks


def test_repair_with_no_solutions():
    """T051: Repair with empty solution list should return None."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1), (0, 1, 2)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[],
        max_repairs=2
    )
    
    assert result is None


def test_repair_with_single_solution():
    """T051: Repair with single solution (already unique) should return None."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1), (0, 1, 2)]
    solution = givens + [(0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution],
        max_repairs=2
    )
    
    assert result is None


def test_repair_with_identical_solutions():
    """T051: Repair with identical solutions should find no divergences."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1), (0, 1, 2)]
    solution = givens + [(0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution, solution],  # Identical
        max_repairs=2
    )
    
    # No divergences = no repair needed
    assert result is None


def test_repair_max_repairs_zero():
    """T051: Max repairs of 0 should not attempt any repairs."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1)]
    solution1 = givens + [(0, 1, 2), (0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    solution2 = givens + [(0, 1, 3), (0, 2, 2), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=0
    )
    
    # Should return immediately with no actions
    assert result is not None
    assert len(result['actions']) == 0


def test_repair_timeout_immediate():
    """T051: Very short timeout should handle gracefully."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1)]
    solution1 = givens + [(0, 1, 2), (0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    solution2 = givens + [(0, 1, 3), (0, 2, 2), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=2,
        timeout_ms=1  # 1ms timeout
    )
    
    # Should complete without error, even if timeout exceeded
    assert result is not None


def test_diff_empty_solutions():
    """T051: Diffing empty solutions should return no regions."""
    regions = diff_multiple_solutions([], size=5, allow_diagonal=True)
    
    assert len(regions) == 0


def test_diff_single_solution():
    """T051: Diffing single solution should return no regions."""
    solution = [(0, 0, 1), (0, 1, 2), (0, 2, 3)]
    regions = diff_multiple_solutions([solution], size=3, allow_diagonal=True)
    
    assert len(regions) == 0


def test_score_empty_regions():
    """T051: Scoring empty regions should return empty list."""
    grid = Grid(3, 3)
    regions = []
    givens = [Position(0, 0)]
    
    candidates = score_structural_blocks(regions, grid, givens)
    
    assert len(candidates) == 0


def test_score_region_all_blocked():
    """T051: Region where all adjacent cells are blocked should have no candidates."""
    from generate.repair.models import AmbiguityRegion
    
    grid = Grid(5, 5)
    # Block cells around (2, 2)
    for r in range(1, 4):
        for c in range(1, 4):
            if r != 2 or c != 2:
                grid.get_cell(Position(r, c)).blocked = True
    
    region = AmbiguityRegion(
        cells={(2, 2)},
        divergence_count=2
    )
    
    givens = [Position(0, 0)]
    candidates = score_structural_blocks([region], grid, givens)
    
    # Should have no valid candidates since all adjacent cells are blocked
    assert len(candidates) == 0


def test_repair_all_candidates_blocked():
    """T051: Repair where all candidate positions are blocked should handle gracefully."""
    grid = Grid(3, 3)
    # Block most of the grid
    for r in range(3):
        for c in range(3):
            if (r, c) not in [(0, 0), (0, 1), (1, 1)]:
                grid.get_cell(Position(r, c)).blocked = True
    
    givens = [(0, 0, 1), (0, 1, 2)]
    solution1 = [(0, 0, 1), (0, 1, 2), (1, 1, 3)]
    solution2 = [(0, 0, 1), (0, 1, 2), (1, 1, 4)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=2
    )
    
    # Should complete without error
    assert result is not None


def test_repair_with_very_large_ambiguity():
    """T051: Repair with entire grid ambiguous should handle gracefully."""
    grid = Grid(5, 5)
    givens = [(0, 0, 1)]
    
    # Create two completely different solutions
    solution1 = [(i, j, i*5+j+1) for i in range(5) for j in range(5)]
    solution2 = [(i, j, (i*5+j+2) % 25 + 1) for i in range(5) for j in range(5)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=2
    )
    
    # Should complete and attempt some repairs
    assert result is not None
    assert 'actions' in result


def test_repair_no_givens():
    """T051: Repair with empty givens list should handle gracefully."""
    grid = Grid(3, 3)
    givens = []
    solution1 = [(0, 0, 1), (0, 1, 2), (0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    solution2 = [(0, 0, 2), (0, 1, 1), (0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=2
    )
    
    # Should handle empty givens without error
    assert result is not None


def test_repair_clue_fallback_disabled():
    """T051: Repair with clue fallback disabled should only try blocks."""
    grid = Grid(3, 3)
    givens = [(0, 0, 1)]
    solution1 = [(0, 0, 1), (0, 1, 2), (0, 2, 3), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    solution2 = [(0, 0, 1), (0, 1, 3), (0, 2, 2), (1, 0, 4), (1, 1, 5), (1, 2, 6), (2, 0, 7), (2, 1, 8), (2, 2, 9)]
    
    result = apply_structural_repair(
        grid=grid,
        givens=givens,
        solutions=[solution1, solution2],
        max_repairs=2,
        allow_clue_fallback=False
    )
    
    # Should only have 'block' actions, no 'clue' actions
    if result and result.get('actions'):
        for action in result['actions']:
            assert action.action_type == 'block'
