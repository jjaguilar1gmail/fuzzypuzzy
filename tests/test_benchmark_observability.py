"""Batch benchmark harness for metrics observability (T042 US3).

Generate multiple puzzles and validate metrics aggregation.
"""
import pytest
from generate.mask.summary import aggregate_mask_metrics, format_mask_summary, MaskSummary
from generate.repair.summary import aggregate_repair_metrics, format_repair_summary, RepairSummary


def test_mask_summary_empty():
    """T042: Mask summary handles empty list."""
    summary = aggregate_mask_metrics([])
    
    assert summary.total_puzzles == 0
    assert summary.masks_applied_count == 0


def test_mask_summary_none_values():
    """T042: Mask summary handles None values (disabled masks)."""
    metrics_list = [None, None, None]
    summary = aggregate_mask_metrics(metrics_list)
    
    assert summary.total_puzzles == 3
    assert summary.masks_enabled_count == 0


def test_mask_summary_aggregation():
    """T042: Mask summary aggregates correctly."""
    metrics_list = [
        {'selected': True, 'density': 0.05, 'cells_count': 5, 'attempts': 1, 'pattern_id': 'corridor'},
        {'selected': True, 'density': 0.08, 'cells_count': 8, 'attempts': 2, 'pattern_id': 'ring'},
        {'selected': False, 'density': 0.0, 'cells_count': 0, 'attempts': 3},  # Not applied
    ]
    summary = aggregate_mask_metrics(metrics_list)
    
    assert summary.total_puzzles == 3
    assert summary.masks_enabled_count == 3
    assert summary.masks_applied_count == 2
    assert summary.avg_density == pytest.approx(0.065, abs=0.001)
    assert summary.avg_cells_blocked == 6.5
    assert summary.avg_attempts == 1.5
    assert summary.patterns_used == {'corridor': 1, 'ring': 1}


def test_mask_summary_format():
    """T042: Mask summary formats to string."""
    summary = MaskSummary(
        total_puzzles=10,
        masks_enabled_count=8,
        masks_applied_count=5,
        avg_density=0.06,
        avg_cells_blocked=6.0,
        avg_attempts=1.5,
        patterns_used={'corridor': 3, 'ring': 2}
    )
    
    formatted = format_mask_summary(summary)
    assert "10 puzzles" in formatted
    assert "Masks enabled: 8" in formatted
    assert "Masks applied: 5" in formatted


def test_repair_summary_empty():
    """T042: Repair summary handles empty list."""
    summary = aggregate_repair_metrics([])
    
    assert summary.total_puzzles == 0
    assert summary.repair_attempted_count == 0


def test_repair_summary_none_values():
    """T042: Repair summary handles None values (disabled repair)."""
    metrics_list = [None, None, None]
    summary = aggregate_repair_metrics(metrics_list)
    
    assert summary.total_puzzles == 3
    assert summary.repair_enabled_count == 0


def test_repair_summary_aggregation():
    """T042: Repair summary aggregates correctly."""
    metrics_list = [
        {
            'attempts': 2,
            'structural_blocks_applied': 1,
            'clue_fallbacks_used': 1,
            'ambiguity_regions_detected': 2,
            'uniqueness_restored': True,
            'repair_time_ms': 100.0
        },
        {
            'attempts': 1,
            'structural_blocks_applied': 1,
            'clue_fallbacks_used': 0,
            'ambiguity_regions_detected': 1,
            'uniqueness_restored': True,
            'repair_time_ms': 50.0
        },
        {
            'attempts': 0,  # No repair attempted
            'structural_blocks_applied': 0,
            'clue_fallbacks_used': 0,
            'ambiguity_regions_detected': 0,
            'uniqueness_restored': False,
            'repair_time_ms': 0.0
        }
    ]
    summary = aggregate_repair_metrics(metrics_list)
    
    assert summary.total_puzzles == 3
    assert summary.repair_enabled_count == 3
    assert summary.repair_attempted_count == 2  # Only first 2 had attempts > 0
    assert summary.repair_succeeded_count == 2
    assert summary.total_structural_blocks == 2
    assert summary.total_clue_fallbacks == 1
    assert summary.avg_ambiguity_regions == 1.5
    assert summary.avg_repair_time_ms == 75.0
    assert summary.success_rate == 100.0


def test_repair_summary_partial_success():
    """T042: Repair summary calculates success rate correctly."""
    metrics_list = [
        {'attempts': 1, 'uniqueness_restored': True},
        {'attempts': 1, 'uniqueness_restored': False},
        {'attempts': 1, 'uniqueness_restored': True},
    ]
    summary = aggregate_repair_metrics(metrics_list)
    
    assert summary.repair_attempted_count == 3
    assert summary.repair_succeeded_count == 2
    assert summary.success_rate == pytest.approx(66.67, abs=0.01)


def test_repair_summary_format():
    """T042: Repair summary formats to string."""
    summary = RepairSummary(
        total_puzzles=10,
        repair_enabled_count=8,
        repair_attempted_count=5,
        repair_succeeded_count=4,
        total_structural_blocks=6,
        total_clue_fallbacks=2,
        avg_ambiguity_regions=1.5,
        avg_repair_time_ms=120.0,
        success_rate=80.0
    )
    
    formatted = format_repair_summary(summary)
    assert "10 puzzles" in formatted
    assert "Repair enabled: 8" in formatted
    assert "80.0%" in formatted


def test_metrics_ranges_sanity():
    """T042: Metrics values should be within sane ranges."""
    # Mask metrics
    mask_metrics = [
        {'selected': True, 'density': 0.05, 'cells_count': 5, 'attempts': 2}
        for _ in range(10)
    ]
    mask_summary = aggregate_mask_metrics(mask_metrics)
    
    assert 0.0 <= mask_summary.avg_density <= 0.10
    assert mask_summary.avg_cells_blocked >= 0
    assert mask_summary.avg_attempts >= 0
    
    # Repair metrics
    repair_metrics = [
        {
            'attempts': 1,
            'structural_blocks_applied': 1,
            'clue_fallbacks_used': 0,
            'ambiguity_regions_detected': 2,
            'uniqueness_restored': True,
            'repair_time_ms': 100.0
        }
        for _ in range(10)
    ]
    repair_summary = aggregate_repair_metrics(repair_metrics)
    
    assert 0.0 <= repair_summary.success_rate <= 100.0
    assert repair_summary.avg_repair_time_ms >= 0.0
    assert repair_summary.avg_ambiguity_regions >= 0.0
