"""Tests for uniqueness engines on clearly unique vs non-unique cases.

Covers both the classic solution counter and the staged checker. Also
verifies the high-level pipeline fallback via pruning.check_puzzle_uniqueness.
"""
from core.grid import Grid
from core.position import Position
from core.puzzle import Puzzle
from core.constraints import Constraints

from generate.uniqueness import count_solutions
from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision
from generate.pruning import check_puzzle_uniqueness


def make_ambiguous_3x3(diagonal: bool = True) -> Puzzle:
    size = 3
    grid = Grid(size, size, allow_diagonal=diagonal)
    # Place endpoints only
    grid.get_cell(Position(0, 0)).given = True
    grid.get_cell(Position(0, 0)).value = 1
    grid.get_cell(Position(2, 2)).given = True
    grid.get_cell(Position(2, 2)).value = 9
    constraints = Constraints(min_value=1, max_value=9, allow_diagonal=diagonal, must_be_connected=True)
    return Puzzle(grid, constraints)


def make_unique_3x3(diagonal: bool = True) -> Puzzle:
    size = 3
    grid = Grid(size, size, allow_diagonal=diagonal)
    # Serpentine path values 1..9
    order = [
        (0, 0), (0, 1), (0, 2),
        (1, 2), (1, 1), (1, 0),
        (2, 0), (2, 1), (2, 2),
    ]
    for v, (r, c) in enumerate(order, start=1):
        cell = grid.get_cell(Position(r, c))
        cell.given = True
        cell.value = v
    constraints = Constraints(min_value=1, max_value=9, allow_diagonal=diagonal, must_be_connected=True)
    return Puzzle(grid, constraints)


def test_ambiguous_3x3_non_unique():
    p = make_ambiguous_3x3(diagonal=True)

    # Classic counter must detect non-unique (>=2 solutions)
    classic = count_solutions(p, cap=3, node_cap=10000, timeout_ms=2000)
    assert not classic.is_unique and classic.solutions_found >= 2

    # Staged checker should not claim UNIQUE
    req = create_request(
        puzzle=p,
        size=p.grid.rows,
        adjacency=8,
        difficulty="medium",
        enable_early_exit=True,
        enable_probes=False,
        enable_sat=False,
    )
    staged = check_uniqueness(req)
    assert staged.decision in (UniquenessDecision.NON_UNIQUE, UniquenessDecision.INCONCLUSIVE)

    # High-level pipeline should conclude non-unique
    assert check_puzzle_uniqueness(p, solver_mode="logic_v2") is False


def test_unique_3x3_unique():
    p = make_unique_3x3(diagonal=True)

    # Classic counter must confirm unique
    classic = count_solutions(p, cap=2, node_cap=10000, timeout_ms=2000)
    assert classic.is_unique and classic.solutions_found == 1

    # Staged checker may be conservative; allow UNIQUE or INCONCLUSIVE
    req = create_request(
        puzzle=p,
        size=p.grid.rows,
        adjacency=8,
        difficulty="medium",
        enable_early_exit=True,
        enable_probes=False,
        enable_sat=False,
    )
    staged = check_uniqueness(req)
    assert staged.decision in (UniquenessDecision.UNIQUE, UniquenessDecision.INCONCLUSIVE)

    # High-level pipeline must confirm unique (staged + fallback if needed)
    assert check_puzzle_uniqueness(p, solver_mode="logic_v2") is True
