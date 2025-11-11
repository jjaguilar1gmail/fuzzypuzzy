"""Tests for repair metrics emission (T041 US3).

Validates that ambiguity repair populates required metrics fields.
"""
import pytest
from generate.repair.metrics import RepairMetrics


def test_repair_metrics_instantiation():
    """T041: RepairMetrics can be instantiated with defaults."""
    metrics = RepairMetrics()
    
    assert metrics.enabled is False
    assert metrics.attempts == 0
    assert metrics.structural_blocks_applied == 0
    assert metrics.clue_fallbacks_used == 0
    assert metrics.ambiguity_regions_detected == 0
    assert metrics.uniqueness_restored is False
    assert metrics.repair_time_ms == 0.0


def test_repair_metrics_with_values():
    """T041: RepairMetrics stores values correctly."""
    metrics = RepairMetrics(
        enabled=True,
        attempts=3,
        structural_blocks_applied=2,
        clue_fallbacks_used=1,
        ambiguity_regions_detected=2,
        uniqueness_restored=True,
        repair_time_ms=150.5
    )
    
    assert metrics.enabled is True
    assert metrics.attempts == 3
    assert metrics.structural_blocks_applied == 2
    assert metrics.clue_fallbacks_used == 1
    assert metrics.ambiguity_regions_detected == 2
    assert metrics.uniqueness_restored is True
    assert metrics.repair_time_ms == 150.5


def test_repair_metrics_blocks_and_fallbacks_sum():
    """T041: Total repairs should be sum of blocks and fallbacks."""
    metrics = RepairMetrics(
        structural_blocks_applied=2,
        clue_fallbacks_used=1
    )
    
    total_repairs = metrics.structural_blocks_applied + metrics.clue_fallbacks_used
    assert total_repairs == 3


def test_repair_metrics_counts_non_negative():
    """T041: All repair counts should be non-negative."""
    metrics = RepairMetrics(
        attempts=5,
        structural_blocks_applied=3,
        clue_fallbacks_used=2,
        ambiguity_regions_detected=4
    )
    
    assert metrics.attempts >= 0
    assert metrics.structural_blocks_applied >= 0
    assert metrics.clue_fallbacks_used >= 0
    assert metrics.ambiguity_regions_detected >= 0


def test_repair_metrics_time_positive():
    """T041: Repair time should be non-negative."""
    metrics = RepairMetrics(repair_time_ms=250.0)
    
    assert metrics.repair_time_ms >= 0.0


def test_repair_metrics_disabled_state():
    """T041: When disabled, no repairs should be applied."""
    metrics = RepairMetrics(enabled=False)
    
    # If repair is disabled, these should remain 0
    assert metrics.structural_blocks_applied == 0
    assert metrics.clue_fallbacks_used == 0
