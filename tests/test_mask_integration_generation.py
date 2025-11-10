"""Integration test for mask generation impact (US1).

Compares 7x7 and 9x9 generation with/without masks to verify:
- Branching reduction (qualitative via successful generation)
- Clue count impact
- Uniqueness preservation
"""
import pytest
from generate.generator import Generator


def test_mask_integration_7x7():
    """T019: Verify mask integration works on 7x7 board."""
    seed = 1234
    
    # Generate with mask
    puzzle = Generator.generate_puzzle(
        size=7,
        difficulty="hard",
        seed=seed,
        mask_enabled=True,
        mask_mode="auto"
    )
    
    assert puzzle is not None
    assert puzzle.size == 7
    assert puzzle.uniqueness_verified is True
    
    # Check mask was applied
    metrics = puzzle.solver_metrics
    if metrics["mask_pattern_id"] is not None:
        assert metrics["mask_cells_count"] > 0
        assert 0 < metrics["mask_density"] <= 0.12  # Allow small board tolerance
        assert metrics["mask_attempts"] >= 1


def test_mask_integration_9x9():
    """T019: Verify mask integration works on 9x9 board."""
    seed = 5678
    
    # Generate with mask
    puzzle = Generator.generate_puzzle(
        size=9,
        difficulty="hard",
        seed=seed,
        mask_enabled=True,
        mask_mode="auto"
    )
    
    assert puzzle is not None
    assert puzzle.size == 9
    assert puzzle.uniqueness_verified is True
    
    # Check mask was applied
    metrics = puzzle.solver_metrics
    if metrics["mask_pattern_id"] is not None:
        assert metrics["mask_cells_count"] > 0
        assert 0 < metrics["mask_density"] <= 0.12


def test_mask_disabled_baseline():
    """T019: Verify generation works with mask disabled (baseline)."""
    puzzle = Generator.generate_puzzle(
        size=7,
        difficulty="medium",
        seed=9999,
        mask_enabled=False
    )
    
    assert puzzle is not None
    assert puzzle.uniqueness_verified is True
    
    # Mask metrics should reflect disabled state
    metrics = puzzle.solver_metrics
    assert metrics["mask_enabled"] is False
    assert metrics["mask_pattern_id"] is None
    assert metrics["mask_cells_count"] == 0


def test_mask_deterministic():
    """T019: Verify same seed produces consistent mask."""
    seed = 4242
    
    puzzle1 = Generator.generate_puzzle(
        size=7,
        difficulty="hard",
        seed=seed,
        mask_enabled=True,
        mask_mode="template",
        mask_template="corridor"
    )
    
    puzzle2 = Generator.generate_puzzle(
        size=7,
        difficulty="hard",
        seed=seed,
        mask_enabled=True,
        mask_mode="template",
        mask_template="corridor"
    )
    
    # Same seed should produce same mask
    assert puzzle1.solver_metrics["mask_pattern_id"] == puzzle2.solver_metrics["mask_pattern_id"]
    assert puzzle1.solver_metrics["mask_cells_count"] == puzzle2.solver_metrics["mask_cells_count"]


def test_mask_auto_disable_small_size():
    """T019: Verify mask auto-disables for small sizes."""
    puzzle = Generator.generate_puzzle(
        size=5,
        difficulty="hard",
        seed=1111,
        mask_enabled=True  # Request enabled
    )
    
    # Should auto-disable for size < 6
    metrics = puzzle.solver_metrics
    assert metrics["mask_pattern_id"] is None or metrics["mask_cells_count"] == 0


def test_mask_auto_disable_easy_difficulty():
    """T019: Verify mask auto-disables for easy difficulty."""
    puzzle = Generator.generate_puzzle(
        size=7,
        difficulty="easy",
        seed=2222,
        mask_enabled=True  # Request enabled
    )
    
    # Should auto-disable for easy
    metrics = puzzle.solver_metrics
    assert metrics["mask_pattern_id"] is None or metrics["mask_cells_count"] == 0


@pytest.mark.slow
def test_mask_impact_qualitative():
    """T019: Qualitative check that masks don't break generation.
    
    This is a smoke test - full performance benchmarking would be separate.
    """
    seeds = [100, 200, 300]
    
    for seed in seeds:
        # With mask
        puzzle_masked = Generator.generate_puzzle(
            size=8,
            difficulty="hard",
            seed=seed,
            mask_enabled=True
        )
        
        assert puzzle_masked is not None
        assert puzzle_masked.uniqueness_verified is True
        
        # Baseline
        puzzle_baseline = Generator.generate_puzzle(
            size=8,
            difficulty="hard",
            seed=seed,
            mask_enabled=False
        )
        
        assert puzzle_baseline is not None
        assert puzzle_baseline.uniqueness_verified is True
        
        # Both should succeed (actual clue count comparison would require more samples)
