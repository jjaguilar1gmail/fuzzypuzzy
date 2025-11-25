"""Tests for structural metric helpers."""

from core.position import Position
from generate.metrics import StructuralInputs, build_structural_metrics


def test_build_structural_metrics_computes_distributions():
    """Structural metrics should summarize givens, anchors, and branching."""
    size = 3
    path = [
        Position(0, 0),
        Position(0, 1),
        Position(0, 2),
        Position(1, 2),
        Position(2, 2),
    ]
    givens = [(0, 0, 1), (1, 2, 5)]
    anchors = [(0, 0), (0, 2), (1, 2)]
    solver_metrics = {
        'clue_density': len(givens) / (size * size),
        'logic_ratio': 0.75,
        'nodes': 20,
        'depth': 4,
        'steps': 10,
    }

    inputs = StructuralInputs(
        size=size,
        givens=givens,
        path=path,
        anchor_positions=anchors,
        solver_metrics=solver_metrics,
    )
    metrics = build_structural_metrics(inputs)

    assert metrics['givens']['total'] == len(givens)
    assert metrics['givens']['row_counts'][0] == 1
    assert metrics['givens']['row_counts'][1] == 1
    assert metrics['anchors']['count'] == 3
    assert metrics['anchors']['gaps']['min'] == 1
    assert metrics['branching']['average_branching_factor'] == round(20 / 4, 4)
    assert metrics['branching']['search_ratio'] == round(1 - solver_metrics['logic_ratio'], 4)
