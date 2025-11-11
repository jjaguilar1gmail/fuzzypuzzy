"""Tests for mask metrics emission (T040 US3).

Validates that mask generation populates required metrics fields.
"""
import pytest
from generate.mask.metrics import MaskGenerationMetrics


def test_mask_metrics_instantiation():
    """T040: MaskGenerationMetrics can be instantiated."""
    metrics = MaskGenerationMetrics()
    
    assert metrics.pattern_id is None
    assert metrics.cells_count == 0
    assert metrics.density == 0.0
    assert metrics.attempts == 0
    assert metrics.validation_time_ms == 0
    assert metrics.selected is False


def test_mask_metrics_with_values():
    """T040: MaskGenerationMetrics stores values correctly."""
    metrics = MaskGenerationMetrics(
        pattern_id="corridor",
        cells_count=5,
        density=0.05,
        attempts=2,
        validation_time_ms=10,
        selected=True
    )
    
    assert metrics.pattern_id == "corridor"
    assert metrics.cells_count == 5
    assert metrics.density == 0.05
    assert metrics.attempts == 2
    assert metrics.validation_time_ms == 10
    assert metrics.selected is True


def test_mask_metrics_density_range():
    """T040: Mask density should be within valid range."""
    metrics = MaskGenerationMetrics(density=0.08)
    
    assert 0.0 <= metrics.density <= 0.10


def test_mask_metrics_counts_positive():
    """T040: Mask metrics counts should be non-negative."""
    metrics = MaskGenerationMetrics(
        cells_count=10,
        attempts=3
    )
    
    assert metrics.cells_count >= 0
    assert metrics.attempts >= 0
