"""Lightweight metric sanity test for guard computation helpers.

Does not attempt full visualization; ensures guard helper functions execute
and produce values within expected rough bounds for several seeds.
"""
from generate.generator import Generator
from generate.pruning import (
    _compute_anchor_dispersion,
    _compute_region_span_fit,
    _compute_flex_zone_size,
    _bidirectional_path_search,
)
from core.grid import Grid
from core.position import Position
from core.puzzle import Puzzle
from core.constraints import Constraints


def _build_puzzle(gp):
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


def test_guard_helpers_across_seeds():
    seeds = [42, 99, 123]
    for seed in seeds:
        gp = Generator.generate_puzzle(
            size=9,
            difficulty="hard",
            path_mode="backbite_v1",
            seed=seed,
            allow_diagonal=True,
            structural_repair_enabled=False,
        )
        assert gp is not None
        puzzle = _build_puzzle(gp)

        max_gap = _compute_anchor_dispersion(puzzle)
        # Guard A threshold
        assert max_gap <= 20  # lenient upper bound; regression test uses <=12

        region_mismatch = _compute_region_span_fit(puzzle)
        assert region_mismatch >= 0
        assert region_mismatch <= 100  # sanity upper cap

        density = gp.clue_count / len(gp.solution)
        if density < 0.28:
            flex_zone = _compute_flex_zone_size(puzzle)
            assert flex_zone >= 0
        # Bi-directional search only meaningful for very large gaps
        if max_gap > 15:
            path_count = _bidirectional_path_search(puzzle, max_gap, time_cap_ms=1000)
            assert path_count >= 1
