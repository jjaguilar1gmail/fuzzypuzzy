"""Regression tests for seed 42 and guardrails.

Ensures the previously problematic configuration is now structurally sound:
- Reasonable density band
- Max gap <= 12
- Quartile coverage present
- Good spatial dispersion
- Uniqueness confirmed by pipeline
"""
from core.grid import Grid
from core.position import Position
from core.puzzle import Puzzle
from core.constraints import Constraints

from generate.generator import Generator
from generate.pruning import _compute_anchor_dispersion, check_puzzle_uniqueness


def _build_puzzle_from_generated(gp):
    size = gp.size
    grid = Grid(size, size, allow_diagonal=gp.allow_diagonal)
    for r, c in gp.blocked_cells:
        grid.get_cell(Position(r, c)).blocked = True
    for r, c, v in gp.givens:
        cell = grid.get_cell(Position(r, c))
        cell.value = v
        cell.given = True
    constraints = Constraints(
        min_value=1,
        max_value=len(gp.solution),
        allow_diagonal=gp.allow_diagonal,
        must_be_connected=True,
    )
    return Puzzle(grid, constraints)


def test_seed42_hard_backbite_v1_is_reasonable_and_unique():
    gp = Generator.generate_puzzle(
        size=9,
        difficulty="hard",
        path_mode="backbite_v1",
        seed=42,
        allow_diagonal=True,
        structural_repair_enabled=False,
    )
    assert gp is not None

    # Density should be reasonable for hard (lenient bounds to avoid flakiness across small changes)
    density = gp.clue_count / len(gp.solution)
    assert 0.30 <= density <= 0.50

    # Max gap constraint
    puzzle = _build_puzzle_from_generated(gp)
    max_gap = _compute_anchor_dispersion(puzzle)
    assert max_gap <= 12

    # Quartile coverage
    given_values = sorted([v for _, _, v in gp.givens])
    min_v, max_v = 1, len(gp.solution)
    span = max_v - min_v + 1
    quartiles = [
        (min_v, min_v + span // 4),
        (min_v + span // 4 + 1, min_v + span // 2),
        (min_v + span // 2 + 1, min_v + 3 * span // 4),
        (min_v + 3 * span // 4 + 1, max_v),
    ]
    assert all(any(qs <= v <= qe for v in given_values) for (qs, qe) in quartiles)

    # Spatial dispersion: clues across most rows/cols
    rows = {r for r, _, _ in gp.givens}
    cols = {c for _, c, _ in gp.givens}
    assert len(rows) >= 7 and len(cols) >= 7

    # Pipeline verified uniqueness in generation result
    assert getattr(gp, "uniqueness_verified", False) is True

    # Classic counter should not find 2+ solutions within budget
    from generate.uniqueness import count_solutions
    classic = count_solutions(puzzle, cap=2, node_cap=20000, timeout_ms=10000)
    assert classic.solutions_found < 2
